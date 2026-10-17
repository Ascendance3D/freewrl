/*
 * X3D_newSFVec3d, X3D_getSFVec3d, X3D_newSFVec2f, and X3D_getSFVec2f extracted
 * unchanged from freex3d/src/libeai/EAI_C_Field.c by run-bounds.sh.
 * The X3DNode union and the FIELDTYPE_ constants come from the real libeai headers.
 */
#include "test_support.h"
#include <stdlib.h>
#include "X3DNode.h"
#include "GeneratedHeaders.h"

#include "eaifield.inc"

static void test_new_sfvec3d(void)
{
	X3DNode *node = X3D_newSFVec3d(1.5, -2.0, 3.14);
	CHECK(node != NULL);
	if (node) {
		CHECK(node->X3D_SFVec3d.type == FIELDTYPE_SFVec3d);
		CHECK(node->X3D_SFVec3d.c[0] == 1.5);
		CHECK(node->X3D_SFVec3d.c[1] == -2.0);
		CHECK(node->X3D_SFVec3d.c[2] == 3.14);
		free(node);
	}
}

static void test_get_sfvec3d_round_trip(void)
{
	double v[3] = { 0, 0, 0 };
	X3DNode *node = X3D_newSFVec3d(4.0, 5.0, 6.0);
	CHECK(node != NULL);
	if (node) {
		X3D_getSFVec3d(node, v);
		CHECK(v[0] == 4.0 && v[1] == 5.0 && v[2] == 6.0);
		free(node);
	}
}

static void test_get_sfvec3d_wrong_type_leaves_output(void)
{
	double v[3] = { 7.0, 8.0, 9.0 };
	X3DNode *node = X3D_newSFVec3d(1.0, 2.0, 3.0);
	CHECK(node != NULL);
	if (node) {
		node->X3D_SFVec3d.type = FIELDTYPE_SFFloat;
		X3D_getSFVec3d(node, v);
		CHECK(v[0] == 7.0 && v[1] == 8.0 && v[2] == 9.0);
		free(node);
	}
}

static void test_new_sfvec2f(void)
{
	X3DNode *node = X3D_newSFVec2f(1.5, -2.0);
	CHECK(node != NULL);
	if (node) {
		CHECK(node->X3D_SFVec2f.type == FIELDTYPE_SFVec2f);
		CHECK(node->X3D_SFVec2f.c[0] == 1.5);
		CHECK(node->X3D_SFVec2f.c[1] == -2.0);
		free(node);
	}
}

static void test_get_sfvec2f_round_trip(void)
{
	float v[2] = { 0, 0 };
	X3DNode *node = X3D_newSFVec2f(4.0, 5.0);
	CHECK(node != NULL);
	if (node) {
		X3D_getSFVec2f(node, v);
		CHECK(v[0] == 4.0 && v[1] == 5.0);
		free(node);
	}
}

static void test_get_sfvec2f_wrong_type_leaves_output(void)
{
	float v[2] = { 7.0, 8.0 };
	X3DNode *node = X3D_newSFVec2f(1.0, 2.0);
	CHECK(node != NULL);
	if (node) {
		node->X3D_SFVec2f.type = FIELDTYPE_SFFloat;
		X3D_getSFVec2f(node, v);
		CHECK(v[0] == 7.0 && v[1] == 8.0);
		free(node);
	}
}

static const ct_case cases[] = {
	{ "X3D_newSFVec3d creates and populates a node", test_new_sfvec3d },
	{ "X3D_getSFVec3d returns what X3D_newSFVec3d stored", test_get_sfvec3d_round_trip },
	{ "X3D_getSFVec3d ignores a node of another field type", test_get_sfvec3d_wrong_type_leaves_output },
	{ "X3D_newSFVec2f creates and populates a node", test_new_sfvec2f },
	{ "X3D_getSFVec2f returns what X3D_newSFVec2f stored", test_get_sfvec2f_round_trip },
	{ "X3D_getSFVec2f ignores a node of another field type", test_get_sfvec2f_wrong_type_leaves_output },
};
const ct_suite ct_eaifield_suite = { "eai-field", cases, CT_COUNT(cases) };
