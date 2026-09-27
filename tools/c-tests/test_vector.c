/*
 * Tests for the real Vector / Stack implementation
 * (freex3d/src/lib/scenegraph/Vector.c + Vector.h), built with the Mac app's config.h.
 * These record current behavior; they are not a specification of what it should be.
 *
 * Pointer-lifetime contract (from the modernization audit):
 *   A pointer returned by vector_get_ptr or stack_top_ptr is valid only until the next
 *   operation that may reallocate Vector.data: a push that grows the vector, vector_shrink,
 *   vector_releaseData, vector_clear, testVector, deleteVector. Whether growth moves the
 *   block is up to the allocator, so no test here compares addresses before and after;
 *   they read values back through a fresh lookup instead.
 */
#include <stdlib.h>

#include <config.h>
#include <system.h>
#include <display.h>
#include <internal.h>

#include "scenegraph/Vector.h"

#include "test_support.h"

/* An element wider than a pointer, so element-size arithmetic is exercised. */
struct item {
	double weight;
	int tag;
};

static struct Vector *int_vector(int cap, int count)
{
	struct Vector *v = newVector(int, cap);
	for (int i = 0; i < count; i++)
		vector_pushBack(int, v, (i + 1) * 10);
	return v;
}

static int ints_are(struct Vector *v, const int *want, int n)
{
	if (vectorSize(v) != n) return 0;
	for (int i = 0; i < n; i++)
		if (vector_get(int, v, i) != want[i]) return 0;
	return 1;
}

static struct Vector *item_vector(int count)
{
	struct Vector *v = newVector(struct item, 2);
	for (int i = 0; i < count; i++) {
		struct item it = { i + 0.5, i };
		vector_pushBack(struct item, v, it);
	}
	return v;
}

static int item_tags_are(struct Vector *v, const int *tags, int n)
{
	if (vectorSize(v) != n) return 0;
	for (int i = 0; i < n; i++) {
		struct item it = vector_get(struct item, v, i);
		if (it.tag != tags[i] || it.weight != tags[i] + 0.5) return 0;
	}
	return 1;
}

static void t_new(void)
{
	struct Vector *v = newVector(int, 4);
	CHECK(v != NULL);
	CHECK(v->n == 0);
	CHECK(vectorSize(v) == 0);
	CHECK(vector_empty(v));
	CHECK(v->allocn == 4);
	CHECK(v->data != NULL);
	/* every allocated slot is writable (ASan flags a short allocation) */
	for (int i = 0; i < v->allocn; i++)
		((int *)v->data)[i] = i;
	deleteVector(int, v);
}

static void t_new_zero_capacity(void)
{
	struct Vector *v = newVector(int, 0);
	CHECK(v != NULL);
	CHECK(v->n == 0);
	CHECK(v->allocn == 0);
	CHECK(v->data == NULL);
	deleteVector(int, v);
}

static void t_push_without_growth(void)
{
	static const int want[] = { 10, 20, 30 };
	struct Vector *v = int_vector(4, 3);
	CHECK(v->allocn == 4);
	CHECK(ints_are(v, want, 3));
	CHECK(!vector_empty(v));
	deleteVector(int, v);
}

static void t_push_with_growth(void)
{
	struct Vector *v = int_vector(2, 2);
	CHECK(v->allocn == 2);
	vector_pushBack(int, v, 30);
	CHECK(v->allocn == 4); /* doubles when full */
	CHECK(vectorSize(v) == 3);
	CHECK(vector_get(int, v, 0) == 10);
	CHECK(vector_get(int, v, 1) == 20);
	CHECK(vector_get(int, v, 2) == 30);
	for (int i = 3; i < 100; i++)
		vector_pushBack(int, v, (i + 1) * 10);
	CHECK(vectorSize(v) == 100);
	CHECK(v->allocn == 128);
	int ok = 1;
	for (int i = 0; i < 100; i++)
		if (vector_get(int, v, i) != (i + 1) * 10) ok = 0;
	CHECK(ok);
	deleteVector(int, v);
}

static void t_push_from_zero_capacity(void)
{
	struct Vector *v = newVector(int, 0);
	vector_pushBack(int, v, 7);
	CHECK(vectorSize(v) == 1);
	CHECK(v->allocn == 1); /* growth from 0 goes to 1 */
	CHECK(v->data != NULL);
	CHECK(vector_get(int, v, 0) == 7);
	vector_pushBack(int, v, 8);
	CHECK(v->allocn == 2);
	CHECK(vector_get(int, v, 0) == 7 && vector_get(int, v, 1) == 8);
	deleteVector(int, v);
}

static void t_push_struct_growth(void)
{
	static const int want[] = { 0, 1, 2, 3, 4, 5, 6 };
	struct Vector *v = item_vector(7);
	CHECK(v->allocn == 8);
	CHECK(item_tags_are(v, want, 7));
	deleteVector(struct item, v);
}

static void t_get_set(void)
{
	struct Vector *v = int_vector(4, 4);
	vector_set(int, v, 0, -1);
	vector_set(int, v, 2, -3);
	CHECK(vector_get(int, v, 0) == -1);
	CHECK(vector_get(int, v, 1) == 20);
	CHECK(vector_get(int, v, 2) == -3);
	CHECK(vector_get(int, v, 3) == 40);
	CHECK(*vector_get_ptr(int, v, 3) == 40);
	*vector_get_ptr(int, v, 1) = 99;
	CHECK(vector_get(int, v, 1) == 99);
	CHECK(vectorSize(v) == 4);
	deleteVector(int, v);
}

static void t_back(void)
{
	struct Vector *v = int_vector(2, 5);
	CHECK(vector_back(int, v) == 50);
	vector_pushBack(int, v, 60);
	CHECK(vector_back(int, v) == 60);
	deleteVector(int, v);
}

static void t_pop_back(void)
{
	static const int want[] = { 10, 20, 30 };
	struct Vector *v = int_vector(4, 4);
	vector_popBack(int, v);
	CHECK(v->allocn == 4); /* popping never shrinks */
	CHECK(ints_are(v, want, 3));
	vector_popBack_(v, 1); /* the function form */
	CHECK(ints_are(v, want, 2));
	deleteVector(int, v);
}

static void t_pop_back_n(void)
{
	static const int want[] = { 10, 20 };
	struct Vector *v = int_vector(8, 6);
	vector_popBackN(int, v, 3);
	CHECK(vectorSize(v) == 3);
	vector_popBack_(v, 1);
	CHECK(ints_are(v, want, 2));
	vector_popBackN(int, v, 2);
	CHECK(vector_empty(v));
	CHECK(v->allocn == 8);
	deleteVector(int, v);
}

static void t_remove_first(void)
{
	static const int want[] = { 1, 2, 3, 4 };
	struct Vector *v = item_vector(5);
	vector_remove_elem(struct item, v, 0);
	CHECK(item_tags_are(v, want, 4));
	deleteVector(struct item, v);
}

static void t_remove_middle(void)
{
	static const int want[] = { 0, 1, 3, 4 };
	struct Vector *v = item_vector(5);
	int allocn = v->allocn;
	vector_remove_elem(struct item, v, 2);
	CHECK(item_tags_are(v, want, 4));
	CHECK(v->allocn == allocn);
	deleteVector(struct item, v);
}

static void t_remove_last(void)
{
	static const int want[] = { 0, 1, 2, 3 };
	/* exactly full, so any read past element n-1 would leave the allocation (ASan) */
	struct Vector *v = item_vector(4);
	struct item extra = { 4.5, 4 };
	vector_pushBack(struct item, v, extra);
	vector_shrink(struct item, v);
	CHECK(v->allocn == 5 && vectorSize(v) == 5);
	vector_remove_elem(struct item, v, 4);
	CHECK(item_tags_are(v, want, 4));
	deleteVector(struct item, v);
}

static void t_remove_only(void)
{
	struct Vector *v = int_vector(1, 1);
	vector_remove_elem(int, v, 0);
	CHECK(vector_empty(v));
	vector_pushBack(int, v, 5);
	CHECK(vectorSize(v) == 1 && vector_get(int, v, 0) == 5);
	deleteVector(int, v);
}

static void t_remove_invalid(void)
{
	static const int want[] = { 10, 20, 30 };
	struct Vector *v = int_vector(4, 3);
	vector_remove_elem(int, v, -1);
	CHECK(ints_are(v, want, 3));
	vector_remove_elem(int, v, 3);
	CHECK(ints_are(v, want, 3));
	vector_remove_elem(int, v, 100);
	CHECK(ints_are(v, want, 3));
	CHECK(v->allocn == 4);
	/* NULL vector and empty vector are ignored */
	vector_removeElement((int)sizeof(int), NULL, 0);
	struct Vector *e = newVector(int, 2);
	vector_remove_elem(int, e, 0);
	CHECK(vector_empty(e) && e->allocn == 2);
	deleteVector(int, e);
	deleteVector(int, v);
}

static void t_clear(void)
{
	struct Vector *v = int_vector(2, 5);
	vector_clear(v);
	CHECK(v->n == 0);
	CHECK(v->allocn == 0);
	CHECK(v->data == NULL);
	vector_pushBack(int, v, 11);
	vector_pushBack(int, v, 12);
	vector_pushBack(int, v, 13);
	CHECK(vectorSize(v) == 3);
	CHECK(v->allocn == 4); /* 0 -> 1 -> 2 -> 4 */
	CHECK(vector_get(int, v, 0) == 11 && vector_get(int, v, 2) == 13);
	vector_clear(v);
	vector_clear(v); /* clearing an already clear vector is harmless */
	CHECK(v->data == NULL && v->n == 0 && v->allocn == 0);
	vector_clear(NULL);
	deleteVector(int, v);
}

static void t_shrink(void)
{
	static const int want[] = { 10, 20, 30, 40, 50 };
	struct Vector *v = int_vector(16, 5);
	vector_shrink(int, v);
	CHECK(v->allocn == 5);
	CHECK(ints_are(v, want, 5));
	vector_shrink(int, v); /* already tight: no change */
	CHECK(v->allocn == 5);
	CHECK(ints_are(v, want, 5));
	vector_pushBack(int, v, 60); /* growth after a shrink still doubles */
	CHECK(v->allocn == 10);
	CHECK(vector_back(int, v) == 60);
	deleteVector(int, v);
}

static void t_release_data(void)
{
	struct Vector *v = int_vector(8, 5);
	int *buf = vector_releaseData(int, v);
	CHECK(buf != NULL);
	CHECK(v->n == 0);
	CHECK(v->allocn == 0);
	CHECK(v->data == NULL);
	int ok = buf != NULL;
	for (int i = 0; ok && i < 5; i++)
		if (buf[i] != (i + 1) * 10) ok = 0;
	CHECK(ok);
	free(buf); /* the caller owns the buffer; it was allocated with malloc/realloc */
	/* the released vector is reusable */
	vector_pushBack(int, v, 1);
	CHECK(vectorSize(v) == 1 && vector_get(int, v, 0) == 1);
	deleteVector(int, v);
}

static void t_release_data_empty(void)
{
	struct Vector *v = newVector(int, 4);
	void *buf = vector_releaseData(int, v);
	/* what realloc(p, 0) returns is allocator-defined; only the vector's state is checked */
	CHECK(v->n == 0 && v->allocn == 0 && v->data == NULL);
	free(buf);
	deleteVector(int, v);
}

static void t_delete(void)
{
	struct Vector *v = int_vector(2, 3);
	deleteVector(int, v);
	CHECK(v == NULL);
	deleteVector(int, v); /* deleting a NULL vector is a no-op */
	CHECK(v == NULL);
	struct Vector *c = int_vector(2, 3);
	vector_clear(c); /* delete after clear: data is already NULL */
	deleteVector(int, c);
	CHECK(c == NULL);
}

static void t_stack(void)
{
	Stack *s = newStack(int);
	CHECK(s != NULL);
	CHECK(stack_empty(s));
	CHECK(s->allocn == 4);
	for (int i = 1; i <= 6; i++) {
		stack_push(int, s, i);
		CHECK(stack_top(int, s) == i);
	}
	CHECK(vectorSize(s) == 6);
	CHECK(s->allocn == 8);
	stack_pop(int, s);
	CHECK(stack_top(int, s) == 5);
	*stack_top_ptr(int, s) = 50;
	CHECK(stack_top(int, s) == 50);
	stack_pop(int, s);
	stack_pop(int, s);
	CHECK(stack_top(int, s) == 3 && vectorSize(s) == 3);
	clearStack(s);
	CHECK(stack_empty(s) && s->allocn == 0 && s->data == NULL);
	stack_push(int, s, 9);
	CHECK(stack_top(int, s) == 9 && vectorSize(s) == 1);
	deleteStack(int, s);
	CHECK(s == NULL);
}

static void t_test_vector_realloc_check(void)
{
	static const int want[] = { 10, 20, 30, 40, 50, 60 };
	struct Vector *v = int_vector(8, 6);
	testVector(int, v);
	CHECK(v->allocn == 8);
	CHECK(v->data != NULL);
	CHECK(ints_are(v, want, 6));
	vector_pushBack(int, v, 70);
	CHECK(vector_back(int, v) == 70);
	deleteVector(int, v);
}

/* See the pointer-lifetime contract at the top of this file. */
static void t_pointer_lifetime_contract(void)
{
	struct Vector *v = newVector(int, 1);
	vector_pushBack(int, v, 1);
	int *p = vector_get_ptr(int, v, 0);
	*p = 42; /* valid: no reallocating operation since the lookup */
	p = NULL; /* growth below may move data; p must not be used after it */
	for (int i = 0; i < 64; i++)
		vector_pushBack(int, v, i);
	CHECK(vector_get(int, v, 0) == 42); /* fresh lookup after growth */
	CHECK(*vector_get_ptr(int, v, 0) == 42);
	CHECK(vector_get(int, v, 64) == 63);
	deleteVector(int, v);

	Stack *s = newStack(int);
	stack_push(int, s, 1);
	int *top = stack_top_ptr(int, s);
	*top = 7;
	top = NULL; /* likewise invalid after the pushes below */
	for (int i = 0; i < 32; i++)
		stack_push(int, s, 100 + i);
	CHECK(vector_get(int, s, 0) == 7);
	CHECK(stack_top(int, s) == 131);
	CHECK(*stack_top_ptr(int, s) == 131);
	deleteStack(int, s);
}

static const ct_case cases[] = {
	{ "new vector", t_new },
	{ "new vector with zero capacity", t_new_zero_capacity },
	{ "push without growth", t_push_without_growth },
	{ "push with growth preserves values", t_push_with_growth },
	{ "push from zero capacity", t_push_from_zero_capacity },
	{ "push struct elements with growth", t_push_struct_growth },
	{ "vector_get / vector_set / vector_get_ptr", t_get_set },
	{ "vector_back", t_back },
	{ "pop back", t_pop_back },
	{ "pop back N", t_pop_back_n },
	{ "remove first element", t_remove_first },
	{ "remove middle element", t_remove_middle },
	{ "remove last element (exactly full)", t_remove_last },
	{ "remove only element", t_remove_only },
	{ "invalid removal leaves state unchanged", t_remove_invalid },
	{ "clear then push", t_clear },
	{ "shrink", t_shrink },
	{ "releaseData transfers ownership", t_release_data },
	{ "releaseData of an empty vector", t_release_data_empty },
	{ "delete sets the pointer to NULL", t_delete },
	{ "Stack push/top/pop/clear", t_stack },
	{ "testVector keeps contents", t_test_vector_realloc_check },
	{ "pointer lifetime: fresh lookup after growth", t_pointer_lifetime_contract },
};

const ct_suite ct_vector_suite = { "vector", cases, CT_COUNT(cases) };
