/*
 * BVH motion-capture parser (CodeQL G09): read_bvh_blob (BVHreader.c), the loader
 * for HAnimMotionDataFile .bvh URLs. BVHreader.c needs no OpenGL or global state, so
 * it is included whole and unchanged (its static helpers are tested directly).
 * Frame and channel counts come from the file: they must be checked before they
 * size the frame-value buffer or index the joint table, and a missing token
 * (strtok returning NULL) must fail the parse, not be read.
 */
#include "BVHreader.c"

#include "test_support.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct bvh_result {
	int ok;
	struct joint_frame_motion *chan;
	int njoint, channel_count, frame_count;
	float *values;
	float frame_time;
};

static void bvh_parse(const char *text, int teePose, float scale, struct bvh_result *r)
{
	char *blob = strdup(text); /* read_bvh_blob tokenizes in place */
	memset(r, 0x5a, sizeof *r); /* outputs must all be set, also on failure */
	r->ok = read_bvh_blob(blob, 0, 1, teePose, 0, 0.0f, 0.0f, scale, &r->chan, &r->njoint,
		&r->channel_count, &r->values, &r->frame_time, &r->frame_count);
	free(blob);
}

static void bvh_free(struct bvh_result *r)
{
	if (r->ok) {
		for (int j = 0; j < r->njoint; j++)
			free(r->chan[j].mocap_name);
		free(r->chan);
		free(r->values);
	}
}

/* rejected, with every output empty: nothing for the caller to use or free */
static void expect_reject(const char *text)
{
	struct bvh_result r;
	bvh_parse(text, 0, 1.0f, &r);
	CHECK(!r.ok);
	CHECK(r.chan == NULL);
	CHECK(r.values == NULL);
	CHECK(r.njoint == 0);
	CHECK(r.channel_count == 0);
	CHECK(r.frame_count == 0);
	bvh_free(&r);
}

static int near(float a, float b) { return a - b < 1e-5f && b - a < 1e-5f; }

/* a HIERARCHY of njoints joints with nchan channels each, then MOTION */
static char *bvh_make(int njoints, int nchan, const char *frames_line, int nvalue_rows)
{
	static const char *names[] = { "Xposition", "Yposition", "Zposition",
		"Zrotation", "Xrotation", "Yrotation" };
	size_t cap = 256 + (size_t)njoints * 160 + (size_t)nvalue_rows * njoints * nchan * 2;
	char *s = malloc(cap), *p = s;
	p += sprintf(p, "HIERARCHY\n");
	for (int j = 0; j < njoints; j++) {
		p += sprintf(p, "%s J%d\n{\nOFFSET 0 1 0\nCHANNELS %d", j ? "JOINT" : "ROOT", j, nchan);
		for (int c = 0; c < nchan; c++)
			p += sprintf(p, " %s", names[c % 6]);
		p += sprintf(p, "\n");
	}
	for (int j = 0; j < njoints; j++)
		p += sprintf(p, "}\n");
	p += sprintf(p, "MOTION\n%s\nFrame Time: 0.0083333\n", frames_line);
	for (int f = 0; f < nvalue_rows; f++) {
		for (int v = 0; v < njoints * nchan; v++)
			p += sprintf(p, v ? " 1" : "1");
		p += sprintf(p, "\n");
	}
	return s;
}

static const char small_bvh[] =
	"HIERARCHY\n"
	"ROOT Hips\n"
	"{\n"
	"\tOFFSET 0.00 0.00 0.00\n"
	"\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation\n"
	"\tJOINT Chest\n"
	"\t{\n"
	"\t\tOFFSET 0.00 5.21 0.00\n"
	"\t\tCHANNELS 3 Zrotation Xrotation Yrotation\n"
	"\t\tEnd Site\n"
	"\t\t{\n"
	"\t\t\tOFFSET 0.00 4.00 0.00\n"
	"\t\t}\n"
	"\t}\n"
	"}\n"
	"MOTION\n"
	"Frames: 2\n"
	"Frame Time: 0.0333333\n"
	"1.0 2.0 3.0 180.0 90.0 -90.0 45.0 0.0 360.0\n"
	"4.0 5.0 6.0 0.0 0.0 0.0 0.0 0.0 0.0\n";

static void test_small_valid(void)
{
	struct bvh_result r;
	bvh_parse(small_bvh, 0, 2.0f, &r);
	CHECK(r.ok);
	CHECK(r.njoint == 2);
	CHECK(r.channel_count == 9);
	CHECK(r.frame_count == 2);
	CHECK(near(r.frame_time, 0.0333333f));
	if (r.ok && r.njoint == 2 && r.channel_count == 9 && r.frame_count == 2) {
		CHECK(!strcmp(r.chan[0].mocap_name, "Hips"));
		CHECK(!strcmp(r.chan[1].mocap_name, "Chest"));
		CHECK(r.chan[0].nchan == 6 && r.chan[1].nchan == 3);
		CHECK(r.chan[0].ichan[0] == CHAN_TX && r.chan[0].ichan[3] == CHAN_RZ);
		CHECK(r.chan[1].ichan[2] == CHAN_RY);
		CHECK(near(r.values[0], 2.0f));  /* position x scale */
		CHECK(near(r.values[2], 6.0f));
		CHECK(near(r.values[3], (float)(180.0 * RADIANS_PER_DEGREE)));
		CHECK(near(r.values[5], (float)(-90.0 * RADIANS_PER_DEGREE)));
		CHECK(near(r.values[8], (float)(360.0 * RADIANS_PER_DEGREE)));
		CHECK(near(r.values[9], 8.0f));
		CHECK(near(r.values[17], 0.0f));
	}
	bvh_free(&r);
}

static void test_blank_lines_crlf(void)
{
	struct bvh_result r;
	bvh_parse("HIERARCHY\r\n\r\nROOT Hips\r\n{\r\n\r\n"
		"CHANNELS 3 Zrotation Xrotation Yrotation\r\n}\r\nMOTION\r\n"
		"Frames: 1\r\nFrame Time: 0.1\r\n0 0 0\r\n", 0, 1.0f, &r);
	CHECK(r.ok);
	CHECK(r.njoint == 1 && r.channel_count == 3 && r.frame_count == 1);
	bvh_free(&r);
}

static void test_largest_joint_table(void)
{
	/* 100 joints x 6 channels = 600 channels, 3 frames: at the joint and channel limits */
	char *s = bvh_make(BVH_MAX_JOINTS, 6, "Frames: 3", 3);
	struct bvh_result r;
	bvh_parse(s, 0, 1.0f, &r);
	CHECK(r.ok);
	CHECK(r.njoint == 100 && r.channel_count == 600 && r.frame_count == 3);
	if (r.ok && r.frame_count == 3 && r.channel_count == 600)
		CHECK(near(r.values[3 * 600 - 1], (float)RADIANS_PER_DEGREE));
	bvh_free(&r);
	free(s);
}

static void test_too_many_joints(void)
{
	char *s = bvh_make(BVH_MAX_JOINTS + 1, 3, "Frames: 1", 1);
	expect_reject(s);
	free(s);
}

static void test_checked_multiply(void)
{
	size_t out = 7;
	CHECK(bvh_mul_size(0, SIZE_MAX, &out) && out == 0);
	CHECK(bvh_mul_size(600, BVH_MAX_FRAMES, &out) && out == (size_t)600 * BVH_MAX_FRAMES);
	CHECK(bvh_mul_size(SIZE_MAX / 4, 4, &out) && out == SIZE_MAX / 4 * 4);
	out = 7;
	CHECK(!bvh_mul_size(SIZE_MAX / 4 + 1, 4, &out) && out == 7);
	CHECK(!bvh_mul_size(SIZE_MAX, 2, &out));
	CHECK(!bvh_mul_size((size_t)1 << (sizeof(size_t) * 4), (size_t)1 << (sizeof(size_t) * 4), &out));
}

static void test_int_overflow_product(void)
{
	/* 4 x 1073741825 = 2^32 + 4: the old int product wrapped to 4 (a 16-byte buffer) */
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 4 Xposition Yposition Zposition Zrotation\n}\n"
		"MOTION\nFrames: 1073741825\nFrame Time: 0.1\n1 2 3 4 5 6 7 8\n");
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation\n}\n"
		"MOTION\nFrames: 2147483647\nFrame Time: 0.1\n1 2 3 4 5 6\n");
}

static void test_too_many_values(void)
{
	/* 600 channels x 1,000,000 frames: each count in range, the product over 2^26 */
	char *s = bvh_make(BVH_MAX_JOINTS, 6, "Frames: 1000000", 1);
	expect_reject(s);
	free(s);
	s = bvh_make(1, 3, "Frames: 1000001", 1);
	expect_reject(s);
	free(s);
}

static void test_bad_frame_count(void)
{
	static const char *frames[] = { "Frames: -1", "Frames: 0", "Frames: -2147483648",
		"Frames: lots", "Frames:", "Frame: 1", "1 2 3" };
	for (int i = 0; i < CT_COUNT(frames); i++) {
		char *s = bvh_make(1, 3, frames[i], 1);
		expect_reject(s);
		free(s);
	}
}

static void test_bad_channel_count(void)
{
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 7 Zrotation Xrotation Yrotation Zrotation Xrotation Yrotation Zrotation\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n1 2 3 4 5 6 7\n");
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 2147483647 Zrotation\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n1\n");
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS -3 Zrotation Xrotation Yrotation\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n1 2 3\n");
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n1\n");
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS three\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n1\n");
}

static void test_repeated_channels_total(void)
{
	/* one joint repeating CHANNELS 6 beyond the 600-channel total */
	size_t cap = 64 + 101 * 80;
	char *s = malloc(cap), *p = s;
	p += sprintf(p, "HIERARCHY\nROOT Hips\n{\n");
	for (int i = 0; i < 101; i++)
		p += sprintf(p, "CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation\n");
	sprintf(p, "}\nMOTION\nFrames: 1\nFrame Time: 0.1\n1\n");
	expect_reject(s);
	free(s);
}

static void test_zero_channels(void)
{
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 0\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n\n");
	expect_reject("HIERARCHY\nROOT Hips\n{\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n1\n");
	expect_reject("HIERARCHY\nMOTION\nFrames: 1\nFrame Time: 0.1\n1\n");
}

static void test_missing_tokens(void)
{
	expect_reject("");
	expect_reject("\n");
	expect_reject("HIERARCHY");            /* no newline: no first line */
	expect_reject("MOTION\nFrames: 1\n");  /* not a BVH file */
	/* fewer channel names than the count */
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 3 Zrotation\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n1 2 3\n");
	/* ROOT without a name */
	expect_reject("HIERARCHY\nROOT\n{\nCHANNELS 3 Zrotation Xrotation Yrotation\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n1 2 3\n");
	/* CHANNELS before any ROOT: no joint to hold them */
	expect_reject("HIERARCHY\nCHANNELS 3 Zrotation Xrotation Yrotation\nROOT Hips\n{\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n1 2 3\n");
	/* file ends at MOTION, after Frames, after Frame Time */
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 3 Zrotation Xrotation Yrotation\n}\nMOTION\n");
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 3 Zrotation Xrotation Yrotation\n}\nMOTION\nFrames: 1\n");
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 3 Zrotation Xrotation Yrotation\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n");
	/* no MOTION section at all */
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 3 Zrotation Xrotation Yrotation\n}\n");
}

static void test_truncated_frames(void)
{
	/* 2 frames declared, 1 present: caught by the length check before allocating */
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 3 Zrotation Xrotation Yrotation\n}\n"
		"MOTION\nFrames: 2\nFrame Time: 0.1\n1 2 3\n");
	/* long enough in characters, short in tokens: caught at the missing token */
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 3 Zrotation Xrotation Yrotation\n}\n"
		"MOTION\nFrames: 2\nFrame Time: 0.1\n1.000000 2.000000 3.000000\n");
	/* a value that is not a number */
	expect_reject("HIERARCHY\nROOT Hips\n{\nCHANNELS 3 Zrotation Xrotation Yrotation\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n1 x 3\n");
}

static void test_joint_names(void)
{
	char text[512];
	char longname[160];
	struct bvh_result r;

	/* 99 characters fit the 100-byte name; 100 do not */
	memset(longname, 'a', 99);
	longname[99] = '\0';
	snprintf(text, sizeof text, "HIERARCHY\nROOT %s\n{\nCHANNELS 1 Zrotation\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n1\n", longname);
	bvh_parse(text, 0, 1.0f, &r);
	CHECK(r.ok);
	if (r.ok) CHECK(strlen(r.chan[0].mocap_name) == 99);
	bvh_free(&r);
	memset(longname, 'a', 100);
	longname[100] = '\0';
	snprintf(text, sizeof text, "HIERARCHY\nROOT %s\n{\nCHANNELS 1 Zrotation\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n1\n", longname);
	expect_reject(text);
	/* joined name parts over 99 characters */
	memset(longname, 'b', 60);
	longname[60] = '\0';
	snprintf(text, sizeof text, "HIERARCHY\nROOT %s %s x\n{\nCHANNELS 1 Zrotation\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n1\n", longname, longname);
	expect_reject(text);
	/* more name parts than the 4 slots: extra parts are ignored, not stored */
	bvh_parse("HIERARCHY\nROOT Left Upper Arm Joint Extra Parts\n{\nCHANNELS 1 Zrotation\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n1\n", 0, 1.0f, &r);
	CHECK(r.ok);
	if (r.ok) CHECK(!strcmp(r.chan[0].mocap_name, "Left_Upper_Arm"));
	bvh_free(&r);
}

static void test_unknown_channel_name(void)
{
	struct bvh_result r;
	bvh_parse("HIERARCHY\nROOT Hips\n{\nCHANNELS 2 Zrotation Wobble\n}\n"
		"MOTION\nFrames: 1\nFrame Time: 0.1\n10 20\n", 0, 1.0f, &r);
	CHECK(r.ok);
	if (r.ok) {
		CHECK(r.chan[0].ichan[0] == CHAN_RZ);
		CHECK(r.chan[0].ichan[1] == CHAN_NONE);
		/* CHAN_NONE (0) is below the position channels, so it converts like a rotation */
		CHECK(near(r.values[1], (float)(20.0 * RADIANS_PER_DEGREE)));
	}
	bvh_free(&r);
}

static void test_teepose_missing_axis(void)
{
	/* teePose swaps a shoulder's X and Y rotations; with no X rotation it must not index */
	struct bvh_result r;
	bvh_parse("HIERARCHY\nROOT Hips\n{\nCHANNELS 1 Zrotation\nJOINT LeftShoulder\n{\n"
		"CHANNELS 2 Zrotation Yrotation\n}\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n0 90 45\n",
		1, 1.0f, &r);
	CHECK(r.ok);
	if (r.ok) {
		CHECK(near(r.values[1], (float)(90.0 * RADIANS_PER_DEGREE)));
		CHECK(near(r.values[2], (float)(45.0 * RADIANS_PER_DEGREE)));
	}
	bvh_free(&r);
	/* with both axes the swap still happens */
	bvh_parse("HIERARCHY\nROOT Hips\n{\nCHANNELS 1 Zrotation\nJOINT LeftShoulder\n{\n"
		"CHANNELS 2 Xrotation Yrotation\n}\n}\nMOTION\nFrames: 1\nFrame Time: 0.1\n0 10 20\n",
		1, 1.0f, &r);
	CHECK(r.ok);
	if (r.ok) {
		CHECK(near(r.values[1], (float)(20.0 * RADIANS_PER_DEGREE)));
		CHECK(near(r.values[2], (float)(-10.0 * RADIANS_PER_DEGREE)));
	}
	bvh_free(&r);
}

static const ct_case cases[] = {
	{ "small valid file", test_small_valid },
	{ "blank lines and CRLF", test_blank_lines_crlf },
	{ "100 joints, 600 channels", test_largest_joint_table },
	{ "101 joints rejected", test_too_many_joints },
	{ "checked size_t multiply", test_checked_multiply },
	{ "int-overflowing frames x channels rejected", test_int_overflow_product },
	{ "frames x channels over the value limit rejected", test_too_many_values },
	{ "negative, zero, missing frame count rejected", test_bad_frame_count },
	{ "channel count over 6, negative, missing rejected", test_bad_channel_count },
	{ "repeated CHANNELS over the total rejected", test_repeated_channels_total },
	{ "zero channels rejected", test_zero_channels },
	{ "missing tokens rejected", test_missing_tokens },
	{ "truncated or non-numeric frame data rejected", test_truncated_frames },
	{ "joint name length and parts", test_joint_names },
	{ "unknown channel name", test_unknown_channel_name },
	{ "teePose with a missing rotation axis", test_teepose_missing_axis },
};
const ct_suite ct_bvh_suite = { "bvh", cases, CT_COUNT(cases) };
