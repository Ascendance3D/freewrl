/*
 * texture_load_blank_Texture (GeneratedTexture), extracted unchanged from
 * freex3d/src/lib/opengl/LoadTextures.c by run-bounds.sh (texture.inc).
 * Only the fields the function uses are declared here.
 */
#include "test_support.h"
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define TEX_LOADING      1
#define TEX_NEEDSBINDING 3
#define TEX_NOTFOUND     6
#define MALLOC(t, _sz) ((_sz > 0) ? (t)malloc(_sz) : NULL)

struct Multi_Int32 { int n; int *p; };
struct X3D_GeneratedTexture { struct Multi_Int32 size; };
typedef struct {
	int x, y, hasAlpha, channels, status;
	unsigned char *texdata;
} textureTableIndexStruct_s;

static int console_messages;
static void ConsoleMessage(const char *fmt, ...) { (void)fmt; console_messages++; }

#include "texture.inc"

static textureTableIndexStruct_s load(int n, int w, int h)
{
	int vals[2] = { w, h };
	struct X3D_GeneratedTexture node;
	textureTableIndexStruct_s tex;
	memset(&tex, 0, sizeof tex);
	tex.status = TEX_LOADING;
	node.size.n = n;
	node.size.p = n ? malloc(sizeof(int) * n) : NULL; /* exact size: ASan sees overreads */
	for (int i = 0; i < n; i++) node.size.p[i] = vals[i];
	console_messages = 0;
	texture_load_blank_Texture(&tex, &node);
	free(node.size.p);
	return tex;
}

/* an invalid size gives no texture data and marks the texture as not found */
static void rejected(int n, int w, int h)
{
	textureTableIndexStruct_s t = load(n, w, h);
	CHECK(t.texdata == NULL);
	CHECK(t.status == TEX_NOTFOUND);
	CHECK(console_messages > 0);
}

static void normal_size(void)
{
	textureTableIndexStruct_s t = load(2, 3, 2);
	CHECK(t.status == TEX_NEEDSBINDING);
	CHECK(t.x == 3 && t.y == 2 && t.channels == 4 && t.hasAlpha);
	CHECK(t.texdata != NULL);
	if (t.texdata)
		for (int i = 0; i < 3 * 2 * 4; i++)
			CHECK(t.texdata[i] == ((i % 4 == 3) ? 0xff : 0));
	free(t.texdata);
}

static void one_by_one(void)
{
	textureTableIndexStruct_s t = load(2, 1, 1);
	CHECK(t.status == TEX_NEEDSBINDING && t.texdata && t.texdata[3] == 0xff);
	free(t.texdata);
}

static void default_empty_size(void) { rejected(0, 0, 0); }
static void only_one_value(void) { rejected(1, 128, 0); }
static void width_zero(void) { rejected(2, 0, 4); }
static void height_zero(void) { rejected(2, 4, 0); }
static void both_zero(void) { rejected(2, 0, 0); }
static void negative_width(void) { rejected(2, -5, 4); }
static void negative_height(void) { rejected(2, 4, -5); }
static void both_negative(void) { rejected(2, -1, -1); }
static void byte_count_overflow(void) { rejected(2, 32768, 32769); }  /* 4*w*h > INT_MAX */
static void pixel_count_overflow(void) { rejected(2, 65536, 65536); } /* w*h > INT_MAX */
static void int_max(void) { rejected(2, INT_MAX, INT_MAX); }

static void just_over_limit(void) { rejected(2, INT_MAX / 4 + 1, 1); } /* 4*w*h = INT_MAX+1 */

static void large_valid(void)
{
	textureTableIndexStruct_s t = load(2, 1024, 1024);
	CHECK(t.status == TEX_NEEDSBINDING && t.texdata != NULL);
	if (t.texdata) CHECK(t.texdata[1024 * 1024 * 4 - 1] == 0xff && t.texdata[1024 * 1024 * 4 - 2] == 0);
	free(t.texdata);
}

static const ct_case cases[] = {
	{ "normal size, black opaque pixels", normal_size },
	{ "1 x 1", one_by_one },
	{ "default empty size field", default_empty_size },
	{ "only one size value", only_one_value },
	{ "width zero", width_zero },
	{ "height zero", height_zero },
	{ "both zero", both_zero },
	{ "negative width", negative_width },
	{ "negative height", negative_height },
	{ "both negative", both_negative },
	{ "byte count overflows int", byte_count_overflow },
	{ "pixel count overflows int", pixel_count_overflow },
	{ "INT_MAX x INT_MAX", int_max },
	{ "one byte over the int limit", just_over_limit },
	{ "1024 x 1024", large_valid },
};
const ct_suite ct_texture_suite = { "texture-blank-size", cases, CT_COUNT(cases) };
