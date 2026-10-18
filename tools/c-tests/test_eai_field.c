/*
 * The X3D_new and X3D_get functions for SFVec3d, SFVec3f, SFVec2f, SFRotation and
 * SFColorRGBA, extracted unchanged from freex3d/src/libeai/EAI_C_Field.c by
 * run-bounds.sh. The X3DNode union and the FIELDTYPE_ constants come from the real
 * libeai headers.
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

static void test_new_sfvec3f(void)
{
	X3DNode *node = X3D_newSFVec3f(1.5f, -2.0f, 3.14f);
	CHECK(node != NULL);
	if (node) {
		CHECK(node->X3D_SFVec3f.type == FIELDTYPE_SFVec3f);
		CHECK(node->X3D_SFVec3f.c[0] == 1.5f);
		CHECK(node->X3D_SFVec3f.c[1] == -2.0f);
		CHECK(node->X3D_SFVec3f.c[2] == 3.14f);
		free(node);
	}
}

static void test_get_sfvec3f_round_trip(void)
{
	float v[3] = { 0, 0, 0 };
	X3DNode *node = X3D_newSFVec3f(4.0f, 5.0f, 6.0f);
	CHECK(node != NULL);
	if (node) {
		X3D_getSFVec3f(node, v);
		CHECK(v[0] == 4.0f && v[1] == 5.0f && v[2] == 6.0f);
		free(node);
	}
}

static void test_get_sfvec3f_wrong_type_leaves_output(void)
{
	float v[3] = { 7.0f, 8.0f, 9.0f };
	X3DNode *node = X3D_newSFVec3f(1.0f, 2.0f, 3.0f);
	CHECK(node != NULL);
	if (node) {
		node->X3D_SFVec3f.type = FIELDTYPE_SFFloat;
		X3D_getSFVec3f(node, v);
		CHECK(v[0] == 7.0f && v[1] == 8.0f && v[2] == 9.0f);
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

static void test_new_sfcolorrgba(void)
{
	X3DNode *node = X3D_newSFColorRGBA(0.1f, 0.2f, 0.3f, 0.4f);
	CHECK(node != NULL);
	if (node) {
		CHECK(node->X3D_SFColorRGBA.type == FIELDTYPE_SFColorRGBA);
		CHECK(node->X3D_SFColorRGBA.r[0] == 0.1f);
		CHECK(node->X3D_SFColorRGBA.r[1] == 0.2f);
		CHECK(node->X3D_SFColorRGBA.r[2] == 0.3f);
		CHECK(node->X3D_SFColorRGBA.r[3] == 0.4f);
		free(node);
	}
}

static void test_get_sfcolorrgba_round_trip(void)
{
	float v[4] = { 0, 0, 0, 0 };
	X3DNode *node = X3D_newSFColorRGBA(0.5f, 0.6f, 0.7f, 0.8f);
	CHECK(node != NULL);
	if (node) {
		X3D_getSFColorRGBA(node, v);
		CHECK(v[0] == 0.5f && v[1] == 0.6f && v[2] == 0.7f && v[3] == 0.8f);
		free(node);
	}
}

static void test_get_sfcolorrgba_wrong_type_leaves_output(void)
{
	float v[4] = { 1.0f, 2.0f, 3.0f, 4.0f };
	X3DNode *node = X3D_newSFColorRGBA(0.1f, 0.2f, 0.3f, 0.4f);
	CHECK(node != NULL);
	if (node) {
		node->X3D_SFColorRGBA.type = FIELDTYPE_SFFloat;
		X3D_getSFColorRGBA(node, v);
		CHECK(v[0] == 1.0f && v[1] == 2.0f && v[2] == 3.0f && v[3] == 4.0f);
		free(node);
	}
}

static const ct_case cases[] = {
	{ "X3D_newSFVec3d creates and populates a node", test_new_sfvec3d },
	{ "X3D_getSFVec3d returns what X3D_newSFVec3d stored", test_get_sfvec3d_round_trip },
	{ "X3D_getSFVec3d ignores a node of another field type", test_get_sfvec3d_wrong_type_leaves_output },
	{ "X3D_newSFVec3f creates and populates a node", test_new_sfvec3f },
	{ "X3D_getSFVec3f returns what X3D_newSFVec3f stored", test_get_sfvec3f_round_trip },
	{ "X3D_getSFVec3f ignores a node of another field type", test_get_sfvec3f_wrong_type_leaves_output },
	{ "X3D_newSFVec2f creates and populates a node", test_new_sfvec2f },
	{ "X3D_getSFVec2f returns what X3D_newSFVec2f stored", test_get_sfvec2f_round_trip },
	{ "X3D_getSFVec2f ignores a node of another field type", test_get_sfvec2f_wrong_type_leaves_output },
	{ "X3D_newSFRotation creates and populates a node", test_new_sfrotation },
	{ "X3D_getSFRotation returns what X3D_newSFRotation stored", test_get_sfrotation_round_trip },
	{ "X3D_getSFRotation ignores a node of another field type", test_get_sfrotation_wrong_type_leaves_output },
	{ "X3D_newSFColorRGBA creates and populates a node", test_new_sfcolorrgba },
	{ "X3D_getSFColorRGBA returns what X3D_newSFColorRGBA stored", test_get_sfcolorrgba_round_trip },
	{ "X3D_getSFColorRGBA ignores a node of another field type", test_get_sfcolorrgba_wrong_type_leaves_output },
};
const ct_suite ct_eaifield_suite = { "eai-field", cases, CT_COUNT(cases) };
