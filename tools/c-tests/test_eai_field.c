/*
 * X3D_newSFVec3d, X3D_getSFVec3d, X3D_newSFRotation, and X3D_getSFRotation, extracted unchanged from
 * freex3d/src/libeai/EAI_C_Field.c by run-bounds.sh. The X3DNode union and the
 * FIELDTYPE_ constants come from the real libeai headers.
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


static void test_new_sfrotation(void)
{
	X3DNode *node = X3D_newSFRotation(0.0, 1.0, 0.0, 3.14);
	CHECK(node != NULL);
	if (node) {
		CHECK(node->X3D_SFRotation.type == FIELDTYPE_SFRotation);
		CHECK(node->X3D_SFRotation.r[0] == 0.0);
		CHECK(node->X3D_SFRotation.r[1] == 1.0);
		CHECK(node->X3D_SFRotation.r[2] == 0.0);
		CHECK(node->X3D_SFRotation.r[3] == 3.14f);
		free(node);
	}
}

static void test_get_sfrotation_round_trip(void)
{
	float v[4] = { 0, 0, 0, 0 };
	X3DNode *node = X3D_newSFRotation(1.0, 0.0, 0.0, 1.57);
	CHECK(node != NULL);
	if (node) {
		X3D_getSFRotation(node, v);
		CHECK(v[0] == 1.0f && v[1] == 0.0f && v[2] == 0.0f && v[3] == 1.57f);
		free(node);
	}
}

static void test_get_sfrotation_wrong_type_leaves_output(void)
{
	float v[4] = { 7.0, 8.0, 9.0, 10.0 };
	X3DNode *node = X3D_newSFRotation(1.0, 2.0, 3.0, 4.0);
	CHECK(node != NULL);
	if (node) {
		node->X3D_SFRotation.type = FIELDTYPE_SFFloat;
		X3D_getSFRotation(node, v);
		CHECK(v[0] == 7.0f && v[1] == 8.0f && v[2] == 9.0f && v[3] == 10.0f);
		free(node);
	}
}
static const ct_case cases[] = {
	{ "X3D_newSFVec3d creates and populates a node", test_new_sfvec3d },
	{ "X3D_getSFVec3d returns what X3D_newSFVec3d stored", test_get_sfvec3d_round_trip },
	{ "X3D_getSFVec3d ignores a node of another field type", test_get_sfvec3d_wrong_type_leaves_output },
	{ "X3D_newSFRotation creates and populates a node", test_new_sfrotation },
	{ "X3D_getSFRotation returns what X3D_newSFRotation stored", test_get_sfrotation_round_trip },
	{ "X3D_getSFRotation ignores a node of another field type", test_get_sfrotation_wrong_type_leaves_output },
};
const ct_suite ct_eaifield_suite = { "eai-field", cases, CT_COUNT(cases) };
