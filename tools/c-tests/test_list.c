/*
 * Tests for the real linked-list implementation (freex3d/src/lib/list.c + list.h),
 * built with the Mac app's config.h: the singly linked s_list_t, its queue helpers,
 * payload-freeing deletes, and the circular doubly linked cd_list_t.
 * These record current behavior; they are not a specification of what it should be.
 *
 * cd_list_t has no users in the engine. cdl_insert into a non-empty list is not covered
 * here: it corrupts the forward links (see known_defects/cdl_insert.c).
 */
#include <stdlib.h>

#include <config.h>
#include <system.h>
#include <display.h>
#include <internal.h>

#include <list.h>

#include "test_support.h"

static int V[8] = { 0, 1, 2, 3, 4, 5, 6, 7 }; /* element payloads the lists do not own */

/* ------------------------------------------------------------------ singly linked */

/* list of V[0..n-1] built with ml_append */
static s_list_t *ml_build(int n)
{
	s_list_t *list = NULL;
	for (int i = 0; i < n; i++)
		list = ml_append(list, ml_new(&V[i]));
	return list;
}

/* the list holds exactly V[idx[0]], V[idx[1]], ... and ends with NULL */
static int ml_is(s_list_t *list, const int *idx, int n)
{
	for (int i = 0; i < n; i++, list = ml_next(list))
		if (!list || ml_elem(list) != &V[idx[i]]) return 0;
	return list == NULL;
}

static void t_ml_new(void)
{
	s_list_t *a = ml_new(&V[3]);
	CHECK(a != NULL);
	CHECK(ml_elem(a) == &V[3]);
	CHECK(ml_next(a) == NULL);
	ml_free(a);
	s_list_t *n = ml_new(NULL);
	CHECK(n != NULL && ml_elem(n) == NULL && ml_next(n) == NULL);
	ml_free(n);
}

static void t_ml_count(void)
{
	CHECK(ml_count(NULL) == 0);
	s_list_t *l = ml_build(1);
	CHECK(ml_count(l) == 1);
	ml_delete_all(l);
	l = ml_build(5);
	CHECK(ml_count(l) == 5);
	CHECK(ml_count(ml_next(l)) == 4);
	ml_delete_all(l);
}

static void t_ml_append(void)
{
	static const int want[] = { 0, 1, 2 };
	s_list_t *a = ml_new(&V[0]);
	CHECK(ml_append(NULL, a) == a); /* appending to an empty list returns the item */
	s_list_t *l = ml_append(a, ml_new(&V[1]));
	CHECK(l == a);
	CHECK(ml_append(l, ml_new(&V[2])) == a);
	CHECK(ml_is(l, want, 3));
	ml_delete_all(l);
}

static void t_ml_last_prev(void)
{
	CHECK(ml_last(NULL) == NULL);
	s_list_t *l = ml_build(3);
	s_list_t *b = ml_get(l, 1), *c = ml_get(l, 2);
	CHECK(ml_last(l) == c);
	CHECK(ml_last(c) == c);
	CHECK(ml_prev(l, l) == NULL); /* head has no predecessor */
	CHECK(ml_prev(l, b) == l);
	CHECK(ml_prev(l, c) == b);
	CHECK(ml_prev(l, NULL) == NULL);
	s_list_t *stranger = ml_new(&V[7]);
	CHECK(ml_prev(l, stranger) == NULL);
	ml_free(stranger);
	ml_delete_all(l);
}

static void t_ml_find(void)
{
	s_list_t *l = ml_build(3);
	s_list_t *b = ml_get(l, 1);
	CHECK(ml_find(l, l) == l);
	CHECK(ml_find(l, b) == b);
	CHECK(ml_find(b, l) == NULL); /* search is forward only */
	CHECK(ml_find(NULL, b) == NULL);
	s_list_t *stranger = ml_new(&V[1]);
	CHECK(ml_find(l, stranger) == NULL);
	ml_free(stranger);
	ml_delete_all(l);
}

static void t_ml_find_elem(void)
{
	s_list_t *l = ml_build(3);
	l = ml_append(l, ml_new(&V[1])); /* duplicate payload at index 3 */
	CHECK(ml_find_elem(l, &V[0]) == l);
	CHECK(ml_find_elem(l, &V[1]) == ml_get(l, 1)); /* first match wins */
	CHECK(ml_find_elem(ml_get(l, 2), &V[1]) == ml_get(l, 3));
	CHECK(ml_find_elem(l, &V[6]) == NULL);
	CHECK(ml_find_elem(NULL, &V[0]) == NULL);
	ml_delete_all(l);
}

static void t_ml_get(void)
{
	s_list_t *l = ml_build(3);
	CHECK(ml_elem(ml_get(l, 0)) == &V[0]);
	CHECK(ml_elem(ml_get(l, 1)) == &V[1]);
	CHECK(ml_elem(ml_get(l, 2)) == &V[2]);
	CHECK(ml_get(l, 3) == NULL);
	CHECK(ml_get(l, -1) == NULL);
	CHECK(ml_get(NULL, 0) == NULL);
	ml_delete_all(l);
}

static void t_ml_insert(void)
{
	/* into an empty list: the item is the new list */
	s_list_t *x = ml_new(&V[5]);
	s_list_t *l = ml_insert(NULL, NULL, x);
	CHECK(l == x && ml_next(x) == NULL);
	ml_delete_all(l);

	/* before the head (point == list, or point NULL): returns the new head */
	static const int front[] = { 5, 0, 1 };
	l = ml_build(2);
	l = ml_insert(l, l, ml_new(&V[5]));
	CHECK(ml_is(l, front, 3));
	ml_delete_all(l);
	static const int front2[] = { 6, 0, 1 };
	l = ml_build(2);
	l = ml_insert(l, NULL, ml_new(&V[6]));
	CHECK(ml_is(l, front2, 3));
	ml_delete_all(l);

	/* before a later item: returns the inserted item; the list head is unchanged */
	static const int mid[] = { 0, 5, 1, 2 };
	l = ml_build(3);
	x = ml_new(&V[5]);
	CHECK(ml_insert(l, ml_get(l, 1), x) == x);
	CHECK(ml_is(l, mid, 4));
	static const int tail[] = { 0, 5, 1, 6, 2 };
	x = ml_new(&V[6]);
	CHECK(ml_insert(l, ml_last(l), x) == x);
	CHECK(ml_is(l, tail, 5));
	ml_delete_all(l);

	/* point not in the list: returns NULL and links nothing */
	static const int same[] = { 0, 1 };
	l = ml_build(2);
	s_list_t *stranger = ml_new(&V[7]);
	x = ml_new(&V[5]);
	CHECK(ml_insert(l, stranger, x) == NULL);
	CHECK(ml_is(l, same, 2));
	ml_free(x);
	ml_free(stranger);
	ml_delete_all(l);
}

static void t_ml_delete(void)
{
	static const int no_mid[] = { 0, 2, 3 }, no_tail[] = { 0, 2 }, all[] = { 0, 1, 2 };
	s_list_t *l = ml_build(4);
	ml_delete(l, ml_get(l, 1));
	CHECK(ml_is(l, no_mid, 3));
	ml_delete(l, ml_last(l));
	CHECK(ml_is(l, no_tail, 2));
	ml_delete_all(l);

	/* ml_delete cannot remove the head: it leaves the list unchanged */
	l = ml_build(3);
	ml_delete(l, l);
	CHECK(ml_is(l, all, 3));
	ml_delete_all(l);
}

static void t_ml_delete_self(void)
{
	static const int no_head[] = { 1, 2, 3 }, no_mid[] = { 1, 3 }, no_tail[] = { 1 };
	s_list_t *l = ml_build(4);
	l = ml_delete_self(l, l); /* head: returns the new head */
	CHECK(ml_is(l, no_head, 3));
	l = ml_delete_self(l, ml_get(l, 1)); /* middle: head unchanged */
	CHECK(ml_is(l, no_mid, 2));
	l = ml_delete_self(l, ml_last(l)); /* tail */
	CHECK(ml_is(l, no_tail, 1));
	l = ml_delete_self(l, l); /* the only item: the list becomes empty */
	CHECK(l == NULL);
}

static void t_ml_delete_all(void)
{
	s_list_t *l = ml_build(6);
	ml_delete_all(l); /* ASan reports any node left or freed twice */
	ml_delete_all(NULL);
	CHECK(1);
}

static void t_ml_foreach(void)
{
	s_list_t *l = ml_build(5);
	int sum = 0;
	ml_foreach(l, sum += *(int *)ml_elem(__l));
	CHECK(sum == 0 + 1 + 2 + 3 + 4);
	/* the macro reads next before the action, so the action may free the item */
	ml_foreach(l, ml_free(__l));
}

static const ct_case list_cases[] = {
	{ "ml_new / ml_free", t_ml_new },
	{ "ml_count", t_ml_count },
	{ "ml_append", t_ml_append },
	{ "ml_last / ml_prev", t_ml_last_prev },
	{ "ml_find", t_ml_find },
	{ "ml_find_elem", t_ml_find_elem },
	{ "ml_get", t_ml_get },
	{ "ml_insert (empty, head, middle, tail, unknown point)", t_ml_insert },
	{ "ml_delete (middle, tail; head is a no-op)", t_ml_delete },
	{ "ml_delete_self (head, middle, tail, only)", t_ml_delete_self },
	{ "ml_delete_all", t_ml_delete_all },
	{ "ml_foreach", t_ml_foreach },
};

const ct_suite ct_list_suite = { "list", list_cases, CT_COUNT(list_cases) };

/* ------------------------------------------------------------------ queue */

/* ml_enqueue inserts at the head; ml_dequeue takes the tail: first in, first out. */

static void t_queue_order(void)
{
	s_list_t *q = NULL;
	for (int i = 1; i <= 4; i++)
		ml_enqueue(&q, ml_new(&V[i]));
	CHECK(ml_count(q) == 4);
	CHECK(ml_elem(q) == &V[4]);          /* newest at the head */
	CHECK(ml_elem(ml_last(q)) == &V[1]); /* oldest at the tail */
	for (int i = 1; i <= 4; i++) {
		s_list_t *item = ml_dequeue(&q);
		CHECK(item != NULL);
		if (!item) break;
		CHECK(ml_elem(item) == &V[i]);
		CHECK(ml_next(item) == NULL);
		CHECK(ml_count(q) == 4 - i);
		ml_free(item);
	}
	CHECK(q == NULL);
}

static void t_queue_interleaved(void)
{
	s_list_t *q = NULL, *item;
	int got[5], n = 0;
	ml_enqueue(&q, ml_new(&V[1]));
	ml_enqueue(&q, ml_new(&V[2]));
	item = ml_dequeue(&q); got[n++] = *(int *)ml_elem(item); ml_free(item);
	ml_enqueue(&q, ml_new(&V[3]));
	ml_enqueue(&q, ml_new(&V[4]));
	item = ml_dequeue(&q); got[n++] = *(int *)ml_elem(item); ml_free(item);
	ml_enqueue(&q, ml_new(&V[5]));
	while ((item = ml_dequeue(&q)) != NULL) {
		if (n < 5) got[n++] = *(int *)ml_elem(item);
		ml_free(item);
	}
	CHECK(n == 5);
	for (int i = 0; i < n; i++)
		CHECK(got[i] == i + 1);
	CHECK(q == NULL);
}

static void t_queue_empty(void)
{
	s_list_t *q = NULL;
	CHECK(ml_dequeue(&q) == NULL);
	CHECK(q == NULL);
	ml_enqueue(&q, ml_new(&V[1]));
	s_list_t *item = ml_dequeue(&q);
	CHECK(item != NULL && ml_elem(item) == &V[1]);
	CHECK(q == NULL); /* dequeuing the only item empties the queue */
	ml_free(item);
	CHECK(ml_dequeue(&q) == NULL);
}

static const ct_case queue_cases[] = {
	{ "enqueue at head, dequeue from tail (FIFO)", t_queue_order },
	{ "interleaved enqueue/dequeue keeps FIFO order", t_queue_interleaved },
	{ "empty and single-item queue", t_queue_empty },
};

const ct_suite ct_queue_suite = { "queue", queue_cases, CT_COUNT(queue_cases) };

/* ------------------------------------------------------------------ payload ownership */

static int freed;

/* counts payloads handed to it and frees them, so ASan sees any double free */
static void count_free(void *p)
{
	freed++;
	free(p);
}

static int *payload(int v)
{
	int *p = malloc(sizeof *p);
	*p = v;
	return p;
}

static void t_ml_delete2(void)
{
	s_list_t *l = NULL;
	for (int i = 0; i < 4; i++)
		l = ml_append(l, ml_new(payload(i)));
	freed = 0;
	ml_delete2(l, ml_get(l, 1), count_free); /* middle */
	CHECK(freed == 1);
	CHECK(ml_count(l) == 3);
	CHECK(*(int *)ml_elem(ml_get(l, 1)) == 2);
	ml_delete2(l, ml_last(l), count_free); /* tail */
	CHECK(freed == 2);
	CHECK(ml_count(l) == 2);
	CHECK(*(int *)ml_elem(ml_last(l)) == 2);
	/* an item with no payload: the node is freed, the callback is not called
	   (prints an ml_delete2 error to stderr) */
	l = ml_append(l, ml_new(NULL));
	ml_delete2(l, ml_last(l), count_free);
	CHECK(freed == 2);
	CHECK(ml_count(l) == 2);
	/* ml_delete2 needs a predecessor, so the head goes through ml_delete_all2 */
	ml_delete_all2(l, count_free);
	CHECK(freed == 4);
}

static void t_ml_delete_all2(void)
{
	s_list_t *l = NULL;
	for (int i = 0; i < 5; i++)
		l = ml_append(l, ml_new(payload(i)));
	freed = 0;
	ml_delete_all2(l, count_free);
	CHECK(freed == 5);

	/* items without a payload are skipped (with an ml_delete_all2 error on stderr) */
	l = ml_append(ml_new(payload(0)), ml_new(NULL));
	l = ml_append(l, ml_new(payload(2)));
	freed = 0;
	ml_delete_all2(l, count_free);
	CHECK(freed == 2);

	freed = 0;
	ml_delete_all2(NULL, count_free);
	CHECK(freed == 0);

	/* a NULL callback means free(); ASan checks the payloads are released correctly */
	l = NULL;
	for (int i = 0; i < 3; i++)
		l = ml_append(l, ml_new(payload(i)));
	ml_delete_all2(l, NULL);
	CHECK(freed == 0);
}

static void t_cdl_delete2(void)
{
	cd_list_t *h = NULL;
	for (int i = 0; i < 4; i++)
		h = cdl_append(h, cdl_new(payload(i)));
	freed = 0;
	cd_list_t *old = h;
	h = cdl_delete2(h, h, count_free); /* head */
	CHECK(freed == 1);
	CHECK(h != old && *(int *)cdl_elem(h) == 1);
	CHECK(cdl_count(h) == 3);
	h = cdl_delete2(h, cdl_get(h, 1), count_free); /* middle */
	CHECK(freed == 2 && cdl_count(h) == 2);
	h = cdl_delete2(h, cdl_last(h), count_free); /* tail */
	CHECK(freed == 3 && cdl_count(h) == 1);
	CHECK(*(int *)cdl_elem(h) == 1);
	h = cdl_delete2(h, h, count_free); /* the only item */
	CHECK(freed == 4);
	CHECK(h == NULL);
}

static void t_cdl_delete_all2(void)
{
	cd_list_t *h = NULL;
	for (int i = 0; i < 5; i++)
		h = cdl_append(h, cdl_new(payload(i)));
	freed = 0;
	cdl_delete_all2(h, count_free);
	CHECK(freed == 5);

	freed = 0;
	cdl_delete_all2(NULL, count_free);
	CHECK(freed == 0);

	h = cdl_append(NULL, cdl_new(payload(0)));
	h = cdl_append(h, cdl_new(payload(1)));
	cdl_delete_all2(h, NULL); /* NULL callback means free() */
	CHECK(freed == 0);
}

static const ct_case payload_cases[] = {
	{ "ml_delete2 frees one payload per item", t_ml_delete2 },
	{ "ml_delete_all2 (callback, empty items, NULL list, NULL callback)", t_ml_delete_all2 },
	{ "cdl_delete2 (head, middle, tail, only)", t_cdl_delete2 },
	{ "cdl_delete_all2 (callback, NULL list, NULL callback)", t_cdl_delete_all2 },
};

const ct_suite ct_payload_suite = { "payload", payload_cases, CT_COUNT(payload_cases) };

/* ------------------------------------------------------------------ circular doubly linked */

/* list of V[0..n-1] built with cdl_append */
static cd_list_t *cdl_build(int n)
{
	cd_list_t *head = NULL;
	for (int i = 0; i < n; i++)
		head = cdl_append(head, cdl_new(&V[i]));
	return head;
}

/* Walking next from head visits V[idx[0]], V[idx[1]], ... and is back at head after n
   steps, and every node's next->prev is itself. The walk is bounded, so broken links
   fail the check instead of looping. */
static int cdl_is(cd_list_t *head, const int *idx, int n)
{
	cd_list_t *l = head;
	if (!head) return n == 0;
	for (int i = 0; i < n; i++) {
		if (!l || cdl_elem(l) != &V[idx[i]]) return 0;
		if (!cdl_next(l) || cdl_prev(cdl_next(l)) != l) return 0;
		if (!cdl_prev(l) || cdl_next(cdl_prev(l)) != l) return 0;
		l = cdl_next(l);
	}
	return l == head;
}

static void t_cdl_new(void)
{
	cd_list_t *a = cdl_new(&V[3]);
	CHECK(a != NULL);
	CHECK(cdl_elem(a) == &V[3]);
	CHECK(cdl_next(a) == a && cdl_prev(a) == a); /* a single item links to itself */
	CHECK(cdl_count(a) == 1);
	CHECK(cdl_last(a) == a);
	cdl_delete_all(a);
}

static void t_cdl_count(void)
{
	CHECK(cdl_count(NULL) == 0);
	cd_list_t *h = cdl_build(5);
	CHECK(cdl_count(h) == 5);
	CHECK(cdl_count(cdl_next(h)) == 5); /* any node counts the whole ring */
	cdl_delete_all(h);
}

static void t_cdl_append(void)
{
	static const int one[] = { 0 }, three[] = { 0, 1, 2 };
	cd_list_t *a = cdl_new(&V[0]);
	cd_list_t *h = cdl_append(NULL, a);
	CHECK(h == a);
	CHECK(cdl_is(h, one, 1));
	CHECK(cdl_append(h, cdl_new(&V[1])) == a); /* head unchanged */
	CHECK(cdl_append(h, cdl_new(&V[2])) == a);
	CHECK(cdl_is(h, three, 3));
	CHECK(cdl_elem(cdl_last(h)) == &V[2]);
	CHECK(cdl_elem(cdl_prev(cdl_prev(h))) == &V[1]); /* backward walk */
	cdl_delete_all(h);
}

static void t_cdl_insert_empty(void)
{
	static const int one[] = { 4 };
	cd_list_t *a = cdl_new(&V[4]);
	cd_list_t *h = cdl_insert(NULL, NULL, a);
	CHECK(h == a);
	CHECK(cdl_is(h, one, 1));
	/* inserting nothing returns the head unchanged */
	CHECK(cdl_insert(h, h, NULL) == h);
	CHECK(cdl_is(h, one, 1));
	cdl_delete_all(h);
}

static void t_cdl_find(void)
{
	cd_list_t *h = cdl_build(3);
	cd_list_t *b = cdl_get(h, 1);
	CHECK(cdl_find(h, h) == h);
	CHECK(cdl_find(h, b) == b);
	CHECK(cdl_find(b, h) == h); /* the ring is searched from any node */
	CHECK(cdl_find(NULL, b) == NULL);
	cd_list_t *stranger = cdl_new(&V[1]);
	CHECK(cdl_find(h, stranger) == NULL);
	cdl_delete_all(stranger);
	cdl_delete_all(h);
}

static void t_cdl_find_elem(void)
{
	cd_list_t *h = cdl_build(3);
	h = cdl_append(h, cdl_new(&V[1])); /* duplicate payload at index 3 */
	CHECK(cdl_find_elem(h, &V[0]) == h);
	CHECK(cdl_find_elem(h, &V[1]) == cdl_get(h, 1)); /* first match wins */
	CHECK(cdl_find_elem(cdl_get(h, 2), &V[1]) == cdl_get(h, 3));
	CHECK(cdl_find_elem(h, &V[6]) == NULL);
	CHECK(cdl_find_elem(NULL, &V[0]) == NULL);
	cdl_delete_all(h);
}

static void t_cdl_get(void)
{
	cd_list_t *h = cdl_build(3);
	CHECK(cdl_elem(cdl_get(h, 0)) == &V[0]);
	CHECK(cdl_elem(cdl_get(h, 1)) == &V[1]);
	CHECK(cdl_elem(cdl_get(h, 2)) == &V[2]);
	CHECK(cdl_get(h, 3) == NULL); /* does not wrap around */
	CHECK(cdl_get(h, -1) == NULL);
	CHECK(cdl_get(NULL, 0) == NULL);
	cdl_delete_all(h);
}

static void t_cdl_delete(void)
{
	static const int no_mid[] = { 0, 2, 3, 4 }, no_head[] = { 2, 3, 4 }, no_tail[] = { 2, 3 };
	cd_list_t *h = cdl_build(5);
	cd_list_t *head = h;
	h = cdl_delete(h, cdl_get(h, 1)); /* middle: head unchanged */
	CHECK(h == head);
	CHECK(cdl_is(h, no_mid, 4));
	h = cdl_delete(h, h); /* head: the next item becomes the head */
	CHECK(cdl_is(h, no_head, 3));
	h = cdl_delete(h, cdl_last(h)); /* tail */
	CHECK(cdl_is(h, no_tail, 2));
	/* no item: prints a cdl_delete error to stderr and returns the head */
	CHECK(cdl_delete(h, NULL) == h);
	CHECK(cdl_is(h, no_tail, 2));
	h = cdl_delete(h, h);
	CHECK(cdl_count(h) == 1 && cdl_next(h) == h && cdl_prev(h) == h);
	h = cdl_delete(h, h); /* the only item: the list becomes empty */
	CHECK(h == NULL);
}

static void t_cdl_delete_all(void)
{
	cd_list_t *h = cdl_build(6);
	cdl_delete_all(h); /* ASan reports any node left or freed twice */
	cdl_delete_all(NULL);
	cdl_delete_all(cdl_new(&V[0]));
	CHECK(1);
}

static const ct_case cdl_cases[] = {
	{ "cdl_new (self-linked)", t_cdl_new },
	{ "cdl_count", t_cdl_count },
	{ "cdl_append (forward/backward links)", t_cdl_append },
	{ "cdl_insert into an empty list", t_cdl_insert_empty },
	{ "cdl_find", t_cdl_find },
	{ "cdl_find_elem", t_cdl_find_elem },
	{ "cdl_get", t_cdl_get },
	{ "cdl_delete (middle, head, tail, only)", t_cdl_delete },
	{ "cdl_delete_all", t_cdl_delete_all },
};

const ct_suite ct_cdl_suite = { "circular", cdl_cases, CT_COUNT(cdl_cases) };
