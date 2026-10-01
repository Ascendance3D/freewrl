/*
 * Pick-ray stack: push_ray and pop_ray from freex3d/src/lib/scenegraph/RenderFuncs.c, with
 * newVector_, deleteVector_, vector_ensureSpace_ and vector_removeElement from
 * scenegraph/Vector.c, extracted unchanged by run-bounds.sh (pickray.inc, vector.inc), and
 * the real Stack macros from Vector.h. upd_ray0 is a test double for the ray transformed
 * into the coordinates of the node being entered: it writes a new, numbered ray.
 *
 * In the picking pass render_node() calls push_ray() going down into each node and
 * pop_ray() coming back up. After each pop the current ray must be the parent's again, and
 * the outermost pop must not read below the stack. FreeWRL 6.7 popped first and then read
 * the top: the ray of the grandparent, and on the outermost pop the element before the
 * stack (AddressSanitizer heap-buffer-overflow in pop_ray on every picking pass).
 */
#include "test_support.h"
#include <stdlib.h>
#include <string.h>
#include "Vector.h"

#define MALLOC(t, _sz) ((t)malloc(_sz))
#define REALLOC(p, _sz) realloc((p), (_sz))
#define FREE_IF_NZ(p) do { if (p) { free(p); (p) = NULL; } } while (0)
#define ASSERT(c) ((void)0) /* as in the shipped app */
#define FALSE 0

struct point_XYZ { double x, y, z; };
struct point_XYZ3 { struct point_XYZ p1, p2, p3; };
typedef struct pRenderFuncs { Stack *ray_stack; struct point_XYZ3 t_r123; } *ppRenderFuncs;
struct tRenderFuncs { void *prv; };
struct tglobal { struct tRenderFuncs RenderFuncs; };
typedef struct tglobal *ttglobal;
static struct pRenderFuncs the_rf;
static struct tglobal the_global = { { &the_rf } };
static ttglobal gglobal(void) { return &the_global; }

static int rays; /* number of rays upd_ray0 has computed */
static void upd_ray0(struct point_XYZ *t_r1, struct point_XYZ *t_r2, struct point_XYZ *t_r3)
{
	rays++;
	t_r1->x = rays; t_r2->x = rays + 0.5; t_r3->x = rays + 0.25;
}

#include "vector.inc"
#include "pickray.inc"

static double ray(void) { return the_rf.t_r123.p1.x; }
static int depth(void) { return vectorSize(the_rf.ray_stack); }

static void start(void)
{
	the_rf.ray_stack = newStack(struct point_XYZ3);
	memset(&the_rf.t_r123, 0, sizeof the_rf.t_r123);
	rays = 0;
	the_rf.t_r123.p1.x = -1; /* the ray of the scene root, from upd_ray() in render_hier */
}

static void finish(void) { deleteVector(struct point_XYZ3, the_rf.ray_stack); }

/* one node: push, pop; the root ray is back and nothing is read below the stack */
static void single_node(void)
{
	start();
	push_ray();
	CHECK(ray() == 1 && depth() == 1);
	pop_ray();
	CHECK(ray() == -1);
	CHECK(depth() == 0);
	finish();
}

/* parent and child: each pop gives back the ray of the node above */
static void nested_restores_parent(void)
{
	double root, parent;
	start();
	root = ray();
	push_ray();
	parent = ray();
	push_ray();
	CHECK(ray() != parent);
	pop_ray();
	CHECK(ray() == parent);
	CHECK(depth() == 1);
	pop_ray();
	CHECK(ray() == root);
	CHECK(depth() == 0);
	finish();
}

/* a second child is entered with the parent's ray saved, not the root's */
static void sibling_sees_parent(void)
{
	double parent;
	start();
	push_ray();
	parent = ray();
	push_ray(); /* first child */
	pop_ray();
	push_ray(); /* second child */
	CHECK(stack_top(struct point_XYZ3, the_rf.ray_stack).p1.x == parent);
	pop_ray();
	CHECK(ray() == parent);
	pop_ray();
	CHECK(ray() == -1 && depth() == 0);
	finish();
}

/* 100 levels: the stack grows (reallocates) from its first 4 slots and unwinds exactly */
static void deep_nesting(void)
{
	double saved[100];
	start();
	for (int i = 0; i < 100; i++) {
		saved[i] = ray();
		push_ray();
	}
	CHECK(depth() == 100);
	for (int i = 99; i >= 0; i--) {
		pop_ray();
		CHECK(ray() == saved[i]);
		CHECK(depth() == i);
	}
	finish();
}

/* a pop with nothing pushed reads nothing, keeps the ray and leaves the stack usable */
static void pop_on_empty_stack(void)
{
	start();
	pop_ray();
	CHECK(ray() == -1 && depth() == 0);
	push_ray();
	pop_ray();
	CHECK(ray() == -1 && depth() == 0);
	finish();
}

static const ct_case cases[] = {
	{ "one node: root ray back, no read below the stack", single_node },
	{ "nested: each pop restores the parent's ray", nested_restores_parent },
	{ "second child saves the parent's ray", sibling_sees_parent },
	{ "100 levels through reallocation", deep_nesting },
	{ "pop with nothing pushed is safe", pop_on_empty_stack },
};
const ct_suite ct_pickray_suite = { "pickray", cases, CT_COUNT(cases) };
