/*
 * Texture file headers (CodeQL G08): loadImage_web3dit, loadImage3DVol and
 * loadImage_nrrd (LoadTextures.c), extracted unchanged by run-bounds.sh
 * (texheader.inc). A texture url reaches them when the downloaded file starts with
 * "web3dit", "vol" or "NRRD" (sniffImageFileHeader), on macOS and Linux.
 * Sizes and channel counts in the header must be checked before they size memory or
 * bound a loop; a rejected file returns FALSE and sets no texture data.
 * Each test writes a small file at run time; nothing large is written or allocated.
 */
#include "test_support.h"
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define TRUE 1
#define FALSE 0
#define UNUSED(v) ((void)(v))
#define MALLOC(t, _sz) ((_sz > 0) ? (t)malloc(_sz) : NULL)
#define FREE_IF_NZ(_ptr) { if (_ptr) { free(_ptr); _ptr = NULL; } }
#define min(A, B) ((A) < (B) ? (A) : (B))
#define max(A, B) ((A) < (B) ? (B) : (A))

struct textureTableIndexStruct {
	int x, y, z, channels, hasAlpha;
	unsigned char *texdata;
};

#include "texheader.inc"

static char tex_dir[512];
static char tex_path[600];

/* write the file; returns its path */
static char *tex_file(const void *data, size_t len)
{
	FILE *fp;
	if (!tex_dir[0]) {
		const char *t = getenv("TMPDIR");
		snprintf(tex_dir, sizeof tex_dir, "%s/fw-texheader.XXXXXX", t && *t ? t : "/tmp");
		if (!mkdtemp(tex_dir)) { perror("mkdtemp"); exit(2); }
	}
	snprintf(tex_path, sizeof tex_path, "%s/t", tex_dir);
	fp = fopen(tex_path, "wb");
	if (!fp) { perror("fopen"); exit(2); }
	fwrite(data, 1, len, fp);
	fclose(fp);
	return tex_path;
}

static void tex_done(void)
{
	unlink(tex_path);
	if (tex_dir[0]) rmdir(tex_dir);
	tex_dir[0] = 0;
}

typedef int (*loader_fn)(struct textureTableIndexStruct *, char *);

static int load(loader_fn fn, const void *data, size_t len, struct textureTableIndexStruct *t)
{
	int ok;
	memset(t, 0, sizeof *t);
	ok = fn(t, tex_file(data, len));
	tex_done();
	return ok;
}

static int load_text(loader_fn fn, const char *text, struct textureTableIndexStruct *t)
{
	return load(fn, text, strlen(text), t);
}

/* rejected: FALSE and no texture data */
static void expect_reject(loader_fn fn, const char *text)
{
	struct textureTableIndexStruct t;
	CHECK(!load_text(fn, text, &t));
	CHECK(t.texdata == NULL);
	free(t.texdata);
}

/* ---------- web3dit ---------- */

static char *web3dit(const char *type, const char *range, const char *n, const char *m,
	const char *dims, const char *sizes, const char *values)
{
	static char buf[4096];
	snprintf(buf, sizeof buf,
		"web3dit2 #H\n2 #G\n1 #F\n #O\n%s #T\n%s #R\n%s #N\n%s #M\nRGBA #C\n%s #D\n%s #P\nD #Y\n#I\n%s\n",
		type, range, n, m, dims, sizes, values);
	return buf;
}

static void web3dit_valid_2d(void)
{
	struct textureTableIndexStruct t;
	/* 2 x 2 RGBA, y-down: the first row in the file is the top of the image */
	CHECK(load_text(loadImage_web3dit,
		web3dit("x", "0 255", "4", "1", "2", "2 2", "0x11223344 0x55667788 0x99aabbcc 0xddeeff00"), &t));
	CHECK(t.x == 2 && t.y == 2 && t.z == 1 && t.channels == 4);
	CHECK(t.texdata != NULL);
	if (t.texdata) {
		/* texture row 0 is the bottom row: the file's second line of values */
		CHECK(t.texdata[0] == 0x99 && t.texdata[1] == 0xaa && t.texdata[2] == 0xbb && t.texdata[3] == 0xcc);
		CHECK(t.texdata[8] == 0x11 && t.texdata[11] == 0x44);
	}
	free(t.texdata);
}

static void web3dit_valid_3d_luminance(void)
{
	struct textureTableIndexStruct t;
	CHECK(load_text(loadImage_web3dit,
		web3dit("i", "0 255", "1", "1", "3", "2 1 2", "1 2 3 4"), &t));
	CHECK(t.x == 2 && t.y == 1 && t.z == 2 && t.channels == 1);
	if (t.texdata) {
		CHECK(t.texdata[0] == 1 && t.texdata[1] == 1 && t.texdata[3] == 255);
		CHECK(t.texdata[12] == 4);
	}
	free(t.texdata);
}

/* 'f' values outside the range are clamped, not converted out of range */
static void web3dit_float_range(void)
{
	struct textureTableIndexStruct t;
	CHECK(load_text(loadImage_web3dit,
		web3dit("f", "0 1", "1", "1", "2", "4 1", "0.5 -3 7 1e30"), &t));
	if (t.texdata) {
		CHECK(t.texdata[0] == 127);
		CHECK(t.texdata[4] == 0);
		CHECK(t.texdata[8] == 255);
		CHECK(t.texdata[12] == 255);
	}
	free(t.texdata);
	/* an empty or reversed range divides by zero or less */
	expect_reject(loadImage_web3dit, web3dit("f", "1 1", "1", "1", "2", "1 1", "0.5"));
	expect_reject(loadImage_web3dit, web3dit("f", "2 1", "1", "1", "2", "1 1", "0.5"));
}

/* N above 4 wrote past the 4-byte pixel[]; above 255 the unsigned char counter never
   reached it (CodeQL alert 123) */
static void web3dit_channel_count(void)
{
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "5", "1", "2", "1 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "256", "1", "2", "1 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "300", "1", "2", "1 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "2147483647", "1", "2", "1 1", "0x1"));
}

static void web3dit_channel_values(void)
{
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "0", "1", "2", "1 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "-1", "1", "2", "1 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "1", "0", "2", "1 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "1", "5", "2", "1 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "2", "4", "2", "1 1", "0x1"));
	/* N 1 with M 4 (RGBA as 4 values) is valid */
	{
		struct textureTableIndexStruct t;
		CHECK(load_text(loadImage_web3dit, web3dit("i", "0 255", "1", "4", "2", "1 1", "1 2 3 4"), &t));
		CHECK(t.channels == 4);
		free(t.texdata);
	}
}

/* 4 * nx * ny * nz in int overflowed and wrapped before the size check */
static void web3dit_size_overflow(void)
{
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "3", "2048 2048 2048", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "3", "65536 65536 65536", "0x1"));
}

/* the RGBA image is at most 256 x 256 x 256 x 4 bytes, as before */
static void web3dit_total_cap(void)
{
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "3", "257 256 256", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "65536 257", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "65537 1", "0x1"));
}

static void web3dit_bad_sizes(void)
{
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "0 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "1 0", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "3", "1 1 0", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "-1 1", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "3", "1 1 -5", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "3", "2 2", "0x1"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "abc", "0x1"));
}

static void web3dit_truncated(void)
{
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "2 2", "0x1 0x2 0x3"));
	expect_reject(loadImage_web3dit, web3dit("i", "0 255", "1", "4", "2", "1 1", "1 2"));
	expect_reject(loadImage_web3dit, web3dit("x", "0 255", "4", "1", "2", "2 2", "0x1 zz 0x3 0x4"));
	/* the header ends early */
	expect_reject(loadImage_web3dit, "web3dit2\n2\n1\n\nx\n0 255\n4\n");
	expect_reject(loadImage_web3dit, "web3dit2\n");
}

/* the description and component names are bounded by their buffers */
static void web3dit_long_header_text(void)
{
	char text[4096], word[901];
	struct textureTableIndexStruct t;
	memset(word, 'A', 900);
	word[900] = 0;
	snprintf(text, sizeof text,
		"web3dit2\n2\n1\n%s\nx\n0 255\n4\n1\n%s\n2\n1 1\nD\n#I\n0x01020304\n", word, word);
	CHECK(load_text(loadImage_web3dit, text, &t));
	CHECK(t.x == 1 && t.y == 1 && t.channels == 4);
	free(t.texdata);
}

/* ---------- .vol ---------- */

static size_t vol(char *buf, const char *sizes, const char *bits, size_t ndata)
{
	int n = snprintf(buf, 256, "vol\n%s\n1 1 1\n0 0 0\n%s 1\n", sizes, bits);
	memset(buf + n, 7, ndata);
	return (size_t)n + ndata;
}

static void vol_valid(void)
{
	char buf[512];
	struct textureTableIndexStruct t;
	size_t len = vol(buf, "2 2 1", "8", 4);
	CHECK(load(loadImage3DVol, buf, len, &t));
	CHECK(t.x == 2 && t.y == 2 && t.z == 1 && t.channels == 1);
	if (t.texdata) CHECK(t.texdata[0] == 7 && t.texdata[3] == 255 && t.texdata[15] == 255);
	free(t.texdata);
	/* short data reads as zero */
	len = vol(buf, "2 2 2", "16", 3);
	CHECK(load(loadImage3DVol, buf, len, &t));
	free(t.texdata);
}

static void vol_bad_header(void)
{
	char buf[512];
	struct textureTableIndexStruct t;
	const char *bad[][2] = {
		{ "2048 2048 2048", "8" },   /* bpp * nx * ny * nz overflowed int */
		{ "65536 65536 1", "32" },
		{ "4096 4096 4096", "2" },   /* 2 bits: no raw bytes, but a huge RGBA image */
		{ "0 1 1", "8" }, { "1 -1 1", "8" }, { "1 1 0", "8" },
		{ "1 1 1", "24" }, { "1 1 1", "-8" }, { "1 1 1", "0" },
		{ "", "8" },
	};
	for (int i = 0; i < CT_COUNT(bad); i++) {
		size_t len = vol(buf, bad[i][0], bad[i][1], 4);
		CHECK(!load(loadImage3DVol, buf, len, &t));
		CHECK(t.texdata == NULL);
	}
}

/* ---------- NRRD ---------- */

static size_t nrrd(char *buf, const char *header, const void *data, size_t ndata)
{
	size_t n = (size_t)snprintf(buf, 2048, "NRRD0001\n%s\n", header);
	memcpy(buf + n, data, ndata);
	return n + ndata;
}

static void nrrd_valid_uchar(void)
{
	static const unsigned char v[8] = { 0, 1, 2, 3, 4, 5, 6, 255 };
	char buf[4096];
	struct textureTableIndexStruct t;
	size_t len = nrrd(buf, "type: uchar\ndimension: 3\nsizes: 2 2 2\nencoding: raw\n", v, 8);
	CHECK(load(loadImage_nrrd, buf, len, &t));
	CHECK(t.x == 2 && t.y == 2 && t.z == 2 && t.channels == 1);
	if (t.texdata) {
		CHECK(t.texdata[0] == 255 && t.texdata[3] == 0);
		CHECK(t.texdata[7] == 1 && t.texdata[31] == 255);
	}
	free(t.texdata);
}

static void nrrd_valid_ushort_big_endian(void)
{
	static const unsigned char v[4] = { 0x12, 0x34, 0xff, 0x00 };
	char buf[4096];
	struct textureTableIndexStruct t;
	size_t len = nrrd(buf, "type: unsigned short\ndimension: 2\nsizes: 2 1\nendian: big\nencoding: raw\n", v, 4);
	CHECK(load(loadImage_nrrd, buf, len, &t));
	CHECK(t.x == 2 && t.y == 1 && t.z == 1);
	if (t.texdata) CHECK(t.texdata[3] == 0x12 && t.texdata[7] == 0xff);
	free(t.texdata);
}

/* 4-byte samples are read as 4 bytes (a long read 8, past the last one) */
static void nrrd_valid_int_types(void)
{
	static const int vi[2] = { 0x7fffffff, -1 };
	const char *types[] = { "int32", "uint32", "int", "uint", "signed int", "unsigned int" };
	char buf[4096], header[256];
	for (int i = 0; i < CT_COUNT(types); i++) {
		struct textureTableIndexStruct t;
		size_t len;
		snprintf(header, sizeof header, "type: %s\ndimension: 1\nsizes: 2\nendian: little\nencoding: raw\n", types[i]);
		len = nrrd(buf, header, vi, sizeof vi);
		CHECK(load(loadImage_nrrd, buf, len, &t));
		CHECK(t.x == 2 && t.y == 1 && t.z == 1);
		/* int32 0x7fffffff: / 65536 / 255 + 127 */
		if (t.texdata && i == 0) CHECK(t.texdata[3] == 255);
		free(t.texdata);
	}
}

static void nrrd_degenerate_axis(void)
{
	static const unsigned char v[8] = { 0 };
	char buf[4096];
	struct textureTableIndexStruct t;
	size_t len = nrrd(buf, "type: uchar\ndimension: 4\nsizes: 1 2 2 2\nencoding: raw\n", v, 8);
	CHECK(load(loadImage_nrrd, buf, len, &t));
	CHECK(t.x == 2 && t.y == 2 && t.z == 2);
	free(t.texdata);
}

static void nrrd_ascii(void)
{
	char buf[4096];
	struct textureTableIndexStruct t;
	size_t len = nrrd(buf, "type: uchar\ndimension: 2\nsizes: 2 2\nencoding: ascii\n", "1 2 3 4\n", 8);
	CHECK(load(loadImage_nrrd, buf, len, &t));
	CHECK(t.x == 2 && t.y == 2);
	free(t.texdata);
	len = nrrd(buf, "type: signed char\ndimension: 2\nsizes: 2 2\nencoding: ascii\n", "1 -2 3 4\n", 9);
	CHECK(load(loadImage_nrrd, buf, len, &t));
	free(t.texdata);
}

/* isize[0] * isize[1] * isize[2] in int overflowed before the conversion (alert 44) */
static void nrrd_size_overflow(void)
{
	char buf[4096];
	const char *bad[] = {
		"type: uchar\ndimension: 3\nsizes: 65536 65536 1\nencoding: raw\n",
		"type: uchar\ndimension: 3\nsizes: 2147483647 2 1\nencoding: raw\n",
		"type: double\ndimension: 3\nsizes: 46341 46341 1\nencoding: raw\n",
	};
	for (int i = 0; i < CT_COUNT(bad); i++) {
		struct textureTableIndexStruct t;
		size_t len = nrrd(buf, bad[i], "\0\0\0\0", 4);
		CHECK(!load(loadImage_nrrd, buf, len, &t));
		CHECK(t.texdata == NULL);
	}
}

static void nrrd_size_limits(void)
{
	char buf[4096];
	const char *bad[] = {
		"type: uchar\ndimension: 1\nsizes: 65537\nencoding: raw\n",       /* axis limit */
		"type: uchar\ndimension: 3\nsizes: 16384 16384 2\nencoding: raw\n", /* 2^29 voxels */
		"type: uchar\ndimension: 3\nsizes: 0 2 2\nencoding: raw\n",
		"type: uchar\ndimension: 3\nsizes: 2 -2 2\nencoding: raw\n",
		"type: uchar\ndimension: 3\nsizes: 2 2 0\nencoding: raw\n",
		"type: uchar\ndimension: 3\nencoding: raw\n",                       /* no sizes */
		"type: uchar\nsizes: 2 2 2\ndimension: 3\nencoding: raw\n",        /* sizes before dimension */
		"type: uchar\ndimension: 3\nsizes: 2 2\nencoding: raw\n",          /* too few sizes */
		"type: uchar\nsizes: 1 1\nencoding: raw\n",                         /* no dimension */
		"type: uchar\ndimension: 0\nsizes: 1\nencoding: raw\n",
		"type: uchar\ndimension: -3\nsizes: 1 1 1\nencoding: raw\n",
	};
	for (int i = 0; i < CT_COUNT(bad); i++) {
		struct textureTableIndexStruct t;
		size_t len = nrrd(buf, bad[i], "\0\0\0\0", 4);
		CHECK(!load(loadImage_nrrd, buf, len, &t));
		CHECK(t.texdata == NULL);
	}
}

/* a dimension of 0 after a degenerate first size made the shift loop run past isize[] */
static void nrrd_degenerate_dimension_zero(void)
{
	char buf[4096];
	struct textureTableIndexStruct t;
	size_t len = nrrd(buf, "type: uchar\ndimension: 2\nsizes: 1 2\ndimension: 0\nencoding: raw\n", "\0\0", 2);
	CHECK(!load(loadImage_nrrd, buf, len, &t));
	CHECK(t.texdata == NULL);
}

static void nrrd_bad_fields(void)
{
	char buf[4096], longword[600];
	const char *bad[] = {
		"dimension: 1\nsizes: 2\nencoding: raw\n",                    /* no type */
		"type: quaternion\ndimension: 1\nsizes: 2\nencoding: raw\n", /* unknown type */
		"type: uchar\ndimension: 1\nsizes: 2\n",                      /* no encoding */
		"type: uchar\ndimension: 1\nsizes: 2\nencoding: gzip\n",      /* not decoded here */
		"type: uchar\ndimension: 1\nsizes: 2\nencoding: raw\nnchannel:=0\n",
		"type: uchar\ndimension: 1\nsizes: 2\nencoding: raw\nnchannel:=5\n",
		"type: uchar\ndimension: 1\nsizes: 2\nencoding: raw\nnchannel:=-1\n",
	};
	char header[1200];
	for (int i = 0; i < CT_COUNT(bad); i++) {
		struct textureTableIndexStruct t;
		size_t len = nrrd(buf, bad[i], "\0\0", 2);
		CHECK(!load(loadImage_nrrd, buf, len, &t));
		CHECK(t.texdata == NULL);
	}
	/* encoding and endian words longer than their 256-byte buffers */
	memset(longword, 'r', sizeof longword - 1);
	longword[sizeof longword - 1] = 0;
	snprintf(header, sizeof header, "type: uchar\ndimension: 1\nsizes: 2\nendian: %s\nencoding: %s\n",
		longword, longword);
	{
		struct textureTableIndexStruct t;
		size_t len = nrrd(buf, header, "\0\0", 2);
		CHECK(!load(loadImage_nrrd, buf, len, &t));
		CHECK(t.texdata == NULL);
	}
}

static void nrrd_nchannel(void)
{
	static const unsigned char v[8] = { 1, 2, 3, 4, 5, 6, 7, 8 };
	char buf[4096];
	struct textureTableIndexStruct t;
	size_t len = nrrd(buf, "type: uchar\ndimension: 1\nsizes: 2\nencoding: raw\nnchannel:=4\n", v, 2);
	CHECK(load(loadImage_nrrd, buf, len, &t));
	CHECK(t.channels == 4);
	free(t.texdata);
}

/* the header must end with a blank line; at end of file the old loop never ended */
static void nrrd_header_without_end(void)
{
	expect_reject(loadImage_nrrd, "NRRD0001\ntype: uchar\ndimension: 1\nsizes: 2\nencoding: raw\n");
	expect_reject(loadImage_nrrd, "NRRD0001\n");
}

/* raw data shorter than the sizes is read as zero */
static void nrrd_truncated_raw(void)
{
	char buf[4096];
	struct textureTableIndexStruct t;
	size_t len = nrrd(buf, "type: ushort\ndimension: 3\nsizes: 4 4 4\nencoding: raw\n", "\1\1\1", 3);
	CHECK(load(loadImage_nrrd, buf, len, &t));
	CHECK(t.x == 4 && t.y == 4 && t.z == 4);
	free(t.texdata);
}

#ifndef G08_PREFIX
/* ---------- the shared size check ---------- */

static void size_check(void)
{
	size_t n = 0;
	CHECK(texture_file_pixels(1, 1, 1, 4, &n) && n == 1);
	CHECK(texture_file_pixels(TEXTURE_FILE_MAX_AXIS, 1, 1, TEXTURE_FILE_MAX_RGBA, &n) && n == 65536);
	CHECK(!texture_file_pixels(TEXTURE_FILE_MAX_AXIS + 1, 1, 1, TEXTURE_FILE_MAX_RGBA, &n));
	CHECK(!texture_file_pixels(1, TEXTURE_FILE_MAX_AXIS + 1, 1, TEXTURE_FILE_MAX_RGBA, &n));
	CHECK(!texture_file_pixels(1, 1, TEXTURE_FILE_MAX_AXIS + 1, TEXTURE_FILE_MAX_RGBA, &n));
	CHECK(!texture_file_pixels(0, 1, 1, TEXTURE_FILE_MAX_RGBA, &n));
	CHECK(!texture_file_pixels(1, -1, 1, TEXTURE_FILE_MAX_RGBA, &n));
	CHECK(!texture_file_pixels(1, 1, INT_MIN, TEXTURE_FILE_MAX_RGBA, &n));
	/* exactly at the RGBA limit, and one pixel over */
	CHECK(texture_file_pixels(16384, 16384, 1, TEXTURE_FILE_MAX_RGBA, &n) && n * 4 == TEXTURE_FILE_MAX_RGBA);
	CHECK(!texture_file_pixels(16384, 16384, 2, TEXTURE_FILE_MAX_RGBA, &n));
	CHECK(texture_file_pixels(256, 256, 256, WEB3DIT_MAX_RGBA, &n) && n == 256 * 256 * 256);
	CHECK(!texture_file_pixels(256, 256, 257, WEB3DIT_MAX_RGBA, &n));
	CHECK(!texture_file_pixels(65536, 65536, 65536, TEXTURE_FILE_MAX_RGBA, &n));
	/* the checked multiply */
	CHECK(texture_mul_size(SIZE_MAX, 1, &n) && n == SIZE_MAX);
	CHECK(texture_mul_size(0, SIZE_MAX, &n) && n == 0);
	CHECK(!texture_mul_size(SIZE_MAX / 2 + 1, 2, &n));
	CHECK(!texture_mul_size((size_t)1 << (sizeof(size_t) * 4), (size_t)1 << (sizeof(size_t) * 4), &n));
}
#endif

static const ct_case cases[] = {
	{ "web3dit valid 2D RGBA", web3dit_valid_2d },
	{ "web3dit valid 3D luminance", web3dit_valid_3d_luminance },
	{ "web3dit float range", web3dit_float_range },
	{ "web3dit channel count over 4 and 255", web3dit_channel_count },
	{ "web3dit channels and values per pixel", web3dit_channel_values },
	{ "web3dit size multiply overflow", web3dit_size_overflow },
	{ "web3dit total byte limit", web3dit_total_cap },
	{ "web3dit zero, negative, missing sizes", web3dit_bad_sizes },
	{ "web3dit truncated data and header", web3dit_truncated },
	{ "web3dit long description and names", web3dit_long_header_text },
	{ "vol valid", vol_valid },
	{ "vol bad header", vol_bad_header },
	{ "nrrd valid uchar", nrrd_valid_uchar },
	{ "nrrd valid ushort big endian", nrrd_valid_ushort_big_endian },
	{ "nrrd valid int and uint", nrrd_valid_int_types },
	{ "nrrd degenerate first axis", nrrd_degenerate_axis },
	{ "nrrd ascii", nrrd_ascii },
	{ "nrrd size multiply overflow", nrrd_size_overflow },
	{ "nrrd size limits and missing sizes", nrrd_size_limits },
	{ "nrrd degenerate axis with dimension 0", nrrd_degenerate_dimension_zero },
	{ "nrrd bad type, encoding, nchannel", nrrd_bad_fields },
	{ "nrrd nchannel 4", nrrd_nchannel },
	{ "nrrd header without end", nrrd_header_without_end },
	{ "nrrd truncated raw data", nrrd_truncated_raw },
#ifndef G08_PREFIX
	{ "shared size check", size_check },
#endif
};
const ct_suite ct_texheader_suite = { "texheader", cases, CT_COUNT(cases) };
