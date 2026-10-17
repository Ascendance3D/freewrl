/*
 * EAI_C_Field node creations, testing X3D_newSFVec3d.
 * Included unchanged by run-bounds.sh.
 */
#include "test_support.h"
#include <stdlib.h>

#define FIELDTYPE_SFVec3d 25
typedef struct { int type; double c[3]; } _intX3D_SFVec3d;
typedef union _X3DNode {
    int type;
    _intX3D_SFVec3d X3D_SFVec3d;
} X3DNode;

#include "eaifield.inc"

static void test_new_sfvec3d(void)
{
    X3DNode *node = X3D_newSFVec3d(1.5, -2.0, 3.14);
    CHECK(node != NULL);
    if (node) {
        CHECK(node->type == FIELDTYPE_SFVec3d);
        CHECK(node->X3D_SFVec3d.c[0] == 1.5);
        CHECK(node->X3D_SFVec3d.c[1] == -2.0);
        CHECK(node->X3D_SFVec3d.c[2] == 3.14);
        free(node);
    }
}

static const ct_case cases[] = {
    { "X3D_newSFVec3d creates and populates node", test_new_sfvec3d },
};
const ct_suite ct_eaifield_suite = { "eai-field", cases, CT_COUNT(cases) };
