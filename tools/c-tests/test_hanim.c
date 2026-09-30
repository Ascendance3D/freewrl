/*
 * parse_float_values and its tokenizer, extracted unchanged from
 * freex3d/src/lib/scenegraph/Component_HAnim.c by run-bounds.sh (hanim.inc).
 * Inputs are copied to heap blocks of exactly strlen+1 bytes, so AddressSanitizer
 * reports any read past the terminating NUL.
 */
#include "test_support.h"
#include <assert.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define FALSE 0
#define TRUE 1
#ifndef min
#define min(a, b) ((a) < (b) ? (a) : (b))
#endif

#include "hanim.inc"

static float *parse(int n, const char *text)
{
	char *s = malloc(strlen(text) + 1);
	float *fv;
	strcpy(s, text);
	fv = parse_float_values(n, s);
	free(s);
	return fv;
}

static int same(const float *fv, const float *want, int n)
{
	for (int i = 0; i < n; i++)
		if (fabsf(fv[i] - want[i]) > 1e-6f) {
			printf("    [%d] = %g, want %g\n", i, fv[i], want[i]);
			return 0;
		}
	return 1;
}

#define EXPECT(n, text, ...) do { \
	const float want_[] = { __VA_ARGS__ }; \
	float *fv_ = parse((n), (text)); \
	CHECK(fv_ != NULL); \
	if (fv_) CHECK(same(fv_, want_, (n))); \
	free(fv_); } while (0)

static void one_float(void) { EXPECT(1, "1.5", 1.5f); }
static void several_spaces(void) { EXPECT(3, "1 2 3", 1, 2, 3); }
static void commas(void) { EXPECT(4, "1,2, 3 ,4", 1, 2, 3, 4); }
static void tabs_newlines(void) { EXPECT(4, "1\t2\n3\r\n4", 1, 2, 3, 4); }
static void negative_decimal(void) { EXPECT(4, "-1.25 0.5 -.75 1e2", -1.25f, 0.5f, -0.75f, 100); }
static void leading_trailing_separators(void) { EXPECT(2, " ,\t1 ,2,\n ", 1, 2); }
static void final_token_no_separator(void) { EXPECT(2, "7 8", 7, 8); }
static void malformed_token_reads_as_zero(void) { EXPECT(3, "1 abc 3", 1, 0, 3); }
static void fewer_tokens_than_requested(void) { EXPECT(4, "1 2", 1, 2, 0, 0); }
static void empty_string(void) { EXPECT(2, "", 0, 0); }
static void only_separators(void) { EXPECT(2, " , \t\n", 0, 0); }
static void more_tokens_than_requested(void) { EXPECT(2, "1 2 3 4", 1, 2); }

static void long_token_keeps_sync(void)
{
	/* a 200-character token is longer than the tokenizer's 127-byte copy */
	char text[256];
	memset(text, '0', 200);
	text[0] = '1'; text[1] = '.';
	strcpy(text + 200, " 5");
	EXPECT(2, text, 1, 5);
}

static void invalid_count(void)
{
	CHECK(parse(0, "1 2") == NULL);
	CHECK(parse(-1, "1 2") == NULL);
	CHECK(parse_float_values(2, NULL) == NULL);
}

static const ct_case cases[] = {
	{ "one float", one_float },
	{ "several floats, spaces", several_spaces },
	{ "commas", commas },
	{ "tabs and newlines", tabs_newlines },
	{ "negative and decimal values", negative_decimal },
	{ "leading and trailing separators", leading_trailing_separators },
	{ "final token without separator", final_token_no_separator },
	{ "malformed token reads as 0", malformed_token_reads_as_zero },
	{ "fewer tokens than requested", fewer_tokens_than_requested },
	{ "empty string", empty_string },
	{ "only separators", only_separators },
	{ "more tokens than requested", more_tokens_than_requested },
	{ "long token keeps token sync", long_token_keeps_sync },
	{ "zero, negative count and NULL string", invalid_count },
};
const ct_suite ct_hanim_suite = { "hanim-parse-floats", cases, CT_COUNT(cases) };
