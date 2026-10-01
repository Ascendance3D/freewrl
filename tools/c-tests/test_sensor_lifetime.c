/*
 * Pointing-device sensor lifetime: setSensitive, unRegisterSensitiveNode and
 * sendSensorEvents from freex3d/src/lib/main/MainLoop.c, and gc_broto_instance from
 * vrml_parser/CParseParser.c, extracted unchanged by run-bounds.sh (sensors.inc), with the
 * Vector functions of test_pick_ray.c. The do_*Sensor handlers are test doubles that read
 * the sensor node, as the real ones do, so a call for a freed node is an AddressSanitizer
 * heap-use-after-free; the other callees are no-op doubles.
 *
 * setSensitive (called from add_parent while parsing) records parent/sensor pairs in
 * SensorEvents, and each picking pass keeps the parent it hovers or presses in the touch
 * (lastOver, CursorOverSensitive, oldCOS, lastPressedOver, hypersensitive). When a world is
 * replaced, reset_Browser > unload_broto > gc_broto_instance frees the nodes; the next
 * picking pass then sends isOver FALSE to touch->lastOver through sendSensorEvents. In
 * FreeWRL 6.7 nothing removed the freed nodes from that state: do_SphereSensor read a freed
 * SphereSensor (AddressSanitizer heap-use-after-free, 10.wrl replaced while hovered).
 */
#include "test_support.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "Vector.h"

#define MALLOC(t, _sz) ((t)malloc(_sz))
#define FREE_IF_NZ(p) do { if (p) { free(p); (p) = NULL; } } while (0)
#define ASSERT(c) ((void)0) /* as in the shipped app */
#define TRUE 1
#define FALSE 0
#define X3D_NODE(node) ((struct X3D_Node *)node)
#define X3D_PROTO(node) ((struct X3D_Proto *)node)

enum { NODE_Group = 1, NODE_Proto, NODE_TouchSensor, NODE_GeoTouchSensor, NODE_LineSensor,
	NODE_PointSensor, NODE_PlaneSensor, NODE_MultiTouchSensor, NODE_CylinderSensor,
	NODE_SphereSensor, NODE_ProximitySensor, NODE_GeoProximitySensor, NODE_Anchor };
#define ButtonPress 4
#define ButtonRelease 5
#define MotionNotify 6
#define MapNotify 19

struct X3D_Node { int _nodeType; struct X3D_Node *_executionContext; float offset[4]; };
struct Multi_Node { int n; struct X3D_Node **p; };
struct X3D_Proto {
	int _nodeType; struct X3D_Node *_executionContext; float offset[4];
	struct Multi_Node __children, _sortedChildren;
	void *__protoDeclares, *__externProtoDeclares, *__nodes, *__subcontexts;
	int __protoFlags;
	struct X3D_Node *__parentProto;
	void *__ROUTES, *__EXPORTS, *__IMPORTS, *__DEFnames, *__IS, *__scripts;
};
struct brotoRoute { int unused; };
struct brotoIS { int unused; };
struct brotoDefpair { struct X3D_Node *node; char *name; };
struct EXIMPORT { int unused; };

struct SensStruct {
	struct X3D_Node *fromnode;
	struct X3D_Node *datanode;
	void (*interpptr)(void *, int, int, int);
};
struct Touch {
	struct X3D_Node *CursorOverSensitive, *oldCOS, *lastPressedOver, *lastOver;
	int lastOverButtonPressed;
	void *hypersensitive;
	int hyperhit;
};
typedef struct pMainloop { int ntouch; struct Touch touchlist[20]; struct Vector *SensorEvents; } *ppMainloop;
struct tMainloop { void *prv; };
struct tRenderFuncs {
	float hyp_save_posn[3], hyp_save_norm[3], ray_save_posn[3];
	void *hypersensitive;
	int hyperhit;
};
struct tglobal { struct tMainloop Mainloop; struct tRenderFuncs RenderFuncs; };
typedef struct tglobal *ttglobal;
static struct pMainloop the_mainloop;
static struct tglobal the_global = { { &the_mainloop } };
static ttglobal gglobal(void) { return &the_global; }

/* handlers: count calls and read the sensor node, as the real ones do */
static int calls;
static struct X3D_Node *last_sensor;
static float last_offset;
static void record(void *node) { calls++; last_sensor = node; last_offset = last_sensor->offset[0]; }
static void do_TouchSensor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }
static void do_GeoTouchSensor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }
static void do_LineSensor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }
static void do_PointSensor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }
static void do_PlaneSensor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }
static void do_MultiTouchSensor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }
static void do_CylinderSensor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }
static void do_SphereSensor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }
static void do_Anchor(void *n, int ev, int but, int over) { (void)ev; (void)but; (void)over; record(n); }

static const char *stringNodeType(int t) { (void)t; return "node"; }
static void get_hyperhit(void) { }
static void dis_send_sensor(struct X3D_Node *f, struct X3D_Node *d, int ev, int b, int s, float *p, float *n)
{ (void)f; (void)d; (void)ev; (void)b; (void)s; (void)p; (void)n; }
static char *getNodeDescription(struct X3D_Node *n) { (void)n; return NULL; }
static char *lookup_brotoDefname(struct X3D_Proto *c, struct X3D_Node *n) { (void)c; (void)n; return NULL; }
static void vecprint3fb(char *a, float *v, char *b) { (void)a; (void)v; (void)b; }
static struct X3D_Proto *hasContext(struct X3D_Node *n) { return n && n->_nodeType == NODE_Proto ? X3D_PROTO(n) : NULL; }
static void free_broute(struct brotoRoute *r) { (void)r; }
static void freeMallocedNodeFields(struct X3D_Node *n) { (void)n; }
static char ciflag_get(int flags, int index) { return (flags >> index) & 1; }

#include "sensors.inc"

static struct X3D_Node *node(int type, float offset)
{
	struct X3D_Node *n = calloc(1, sizeof(struct X3D_Proto));
	n->_nodeType = type;
	n->offset[0] = offset;
	return n;
}

/* a live broto context: a scene, or a PROTO instance (protoFlags bit 0: live scenery) */
static struct X3D_Proto *context(void)
{
	struct X3D_Proto *c = (struct X3D_Proto *)node(NODE_Proto, 0);
	c->__protoFlags = 1;
	c->__nodes = newVector(struct X3D_Node *, 4);
	return c;
}

static void own(struct X3D_Proto *c, struct X3D_Node *n) { vector_pushBack(struct X3D_Node *, c->__nodes, n); }

static void subcontext(struct X3D_Proto *c, struct X3D_Proto *sub)
{
	if (!c->__subcontexts) c->__subcontexts = newVector(struct X3D_Proto *, 2);
	vector_pushBack(struct X3D_Proto *, c->__subcontexts, sub);
	own(c, X3D_NODE(sub));
}

static void start(void)
{
	memset(&the_mainloop, 0, sizeof the_mainloop);
	memset(&the_global.RenderFuncs, 0, sizeof the_global.RenderFuncs);
	the_mainloop.ntouch = 20;
	the_mainloop.SensorEvents = newVector(struct SensStruct *, 0);
	calls = 0;
	last_sensor = NULL;
}

static void finish(void)
{
	for (int i = 0; i < vectorSize(the_mainloop.SensorEvents); i++)
		free(vector_get(struct SensStruct *, the_mainloop.SensorEvents, i));
	deleteVector(struct SensStruct *, the_mainloop.SensorEvents);
}

static int sensor_events(void) { return vectorSize(the_mainloop.SensorEvents); }

/* the pointer is over parent (and pressing it): the state the picking pass leaves */
static void hover_and_press(struct Touch *t, struct X3D_Node *parent)
{
	t->CursorOverSensitive = t->lastOver = t->oldCOS = t->lastPressedOver = parent;
	t->hypersensitive = parent;
	t->hyperhit = 1;
	the_global.RenderFuncs.hypersensitive = parent;
	the_global.RenderFuncs.hyperhit = 1;
}

/* the next picking pass after a replacement, as setup_picking runs it: nothing under the
   pointer now, so lastOver gets isOver FALSE, a pressed sensor gets the drag, oldCOS unmaps */
static void next_picking_pass(struct Touch *t)
{
	struct X3D_Node *now = NULL;
	if (t->lastOver != now) {
		sendSensorEvents(t->lastOver, MapNotify, 0, FALSE);
		t->lastOver = now;
	}
	sendSensorEvents(t->lastPressedOver, MotionNotify, 1, TRUE);
	sendSensorEvents(t->oldCOS, MapNotify, 0, FALSE);
}

/* 10.wrl: a PROTO instance holds a Group with a SphereSensor; the scene is replaced while the
   pointer is over it. The sensor works before, and nothing reaches it after it is freed. */
static void replaced_proto_sphere_sensor(void)
{
	struct X3D_Proto *scene, *instance;
	struct X3D_Node *group, *sphere;
	struct Touch *t = &the_mainloop.touchlist[0];

	start();
	scene = context();
	instance = context();
	group = node(NODE_Group, 0);
	sphere = node(NODE_SphereSensor, 7);
	own(instance, group);
	own(instance, sphere);
	subcontext(scene, instance);
	setSensitive(group, sphere);
	CHECK(sensor_events() == 1);

	/* the valid path: the hovered parent reaches its SphereSensor, which reads the node */
	sendSensorEvents(group, MapNotify, 0, TRUE);
	CHECK(calls == 1 && last_sensor == sphere && last_offset == 7);
	hover_and_press(t, group);

	gc_broto_instance(scene); /* frees group, sphere and the instance (reset_Browser) */
	CHECK(sensor_events() == 0);
	CHECK(t->lastOver == NULL && t->CursorOverSensitive == NULL);
	CHECK(t->oldCOS == NULL && t->lastPressedOver == NULL);
	CHECK(t->hypersensitive == NULL && t->hyperhit == 0);
	CHECK(the_global.RenderFuncs.hypersensitive == NULL && the_global.RenderFuncs.hyperhit == 0);

	calls = 0;
	next_picking_pass(t); /* in 6.7: heap-use-after-free in do_SphereSensor */
	CHECK(calls == 0);
	free(scene);
	finish();
}

/* PROTO declarations are parsed (and setSensitive runs) but are not live: their nodes are
   freed through __protoDeclares and must leave SensorEvents too */
static void replaced_proto_declaration(void)
{
	struct X3D_Proto *scene, *decl;
	struct X3D_Node *group, *touch;

	start();
	scene = context();
	decl = context();
	decl->__protoFlags = 0; /* a declaration, not live scenery */
	decl->__parentProto = X3D_NODE(scene);
	group = node(NODE_Group, 0);
	touch = node(NODE_TouchSensor, 1);
	own(decl, group);
	own(decl, touch);
	scene->__protoDeclares = newVector(struct X3D_Proto *, 1);
	vector_pushBack(struct X3D_Proto *, scene->__protoDeclares, decl);
	setSensitive(group, touch);
	CHECK(sensor_events() == 1);

	gc_broto_instance(scene);
	CHECK(sensor_events() == 0);
	free(scene);
	finish();
}

/* an Inline unloads (gc_broto_instance of its context only): its sensors go, the rest of the
   world keeps working through the same SensorEvents */
static void unloaded_inline_keeps_others(void)
{
	struct X3D_Proto *inl;
	struct X3D_Node *ga, *touch, *gb, *plane;
	struct Touch *t = &the_mainloop.touchlist[3];

	start();
	inl = context();
	ga = node(NODE_Group, 0);
	touch = node(NODE_TouchSensor, 1);
	own(inl, ga);
	own(inl, touch);
	gb = node(NODE_Group, 0);
	plane = node(NODE_PlaneSensor, 2);
	setSensitive(ga, touch);
	setSensitive(gb, plane);
	hover_and_press(t, ga);

	gc_broto_instance(inl);
	CHECK(sensor_events() == 1);
	CHECK(t->lastOver == NULL && t->lastPressedOver == NULL && t->hypersensitive == NULL);
	next_picking_pass(t);
	CHECK(calls == 0);

	sendSensorEvents(gb, ButtonPress, 1, TRUE);
	CHECK(calls == 1 && last_sensor == plane && last_offset == 2);
	CHECK(the_global.RenderFuncs.hypersensitive == gb);
	sendSensorEvents(gb, ButtonRelease, 0, TRUE);
	CHECK(calls == 2 && the_global.RenderFuncs.hypersensitive == NULL);

	free(inl);
	free(gb);
	free(plane);
	finish();
}

/* one sensor under two parents (DEF/USE), an Anchor (its own parent), other touches: only
   what names the node goes */
static void unregister_one_node(void)
{
	struct X3D_Node *g1, *g2, *cyl, *anchor;
	struct Touch *a = &the_mainloop.touchlist[0], *b = &the_mainloop.touchlist[19];

	start();
	g1 = node(NODE_Group, 0);
	g2 = node(NODE_Group, 0);
	cyl = node(NODE_CylinderSensor, 3);
	anchor = node(NODE_Anchor, 4);
	setSensitive(g1, cyl);
	setSensitive(g2, cyl);
	setSensitive(g2, cyl); /* a duplicate is not recorded twice */
	setSensitive(g1, anchor);
	CHECK(sensor_events() == 3);
	hover_and_press(a, g1);
	hover_and_press(b, g2);

	unRegisterSensitiveNode(g1);
	CHECK(sensor_events() == 2);
	CHECK(a->lastOver == NULL && a->lastPressedOver == NULL && a->oldCOS == NULL);
	CHECK(b->lastOver == g2 && b->lastPressedOver == g2 && b->hypersensitive == g2);
	CHECK(the_global.RenderFuncs.hypersensitive == g2);
	sendSensorEvents(g2, MapNotify, 0, TRUE);
	CHECK(calls == 1 && last_sensor == cyl && last_offset == 3);
	sendSensorEvents(anchor, MapNotify, 0, TRUE);
	CHECK(calls == 2 && last_sensor == anchor && last_offset == 4);

	unRegisterSensitiveNode(cyl);
	CHECK(sensor_events() == 1);
	unRegisterSensitiveNode(anchor);
	CHECK(sensor_events() == 0);
	unRegisterSensitiveNode(NULL);
	CHECK(b->lastOver == g2);

	free(g1);
	free(g2);
	free(cyl);
	free(anchor);
	finish();
}

static const ct_case cases[] = {
	{ "world replaced while a PROTO SphereSensor is hovered and pressed", replaced_proto_sphere_sensor },
	{ "PROTO declaration sensors leave SensorEvents when freed", replaced_proto_declaration },
	{ "Inline unload: its sensors go, the others keep working", unloaded_inline_keeps_others },
	{ "unregistering one node keeps every other sensor and touch", unregister_one_node },
};
const ct_suite ct_sensors_suite = { "sensors", cases, CT_COUNT(cases) };
