/*
 * EAI GETNODEPARENTS reply: handleGETNODEPARENTS from
 * freex3d/src/lib/input/EAIEventsIn.c and outBufferCat from
 * freex3d/src/lib/input/EAIHelpers.c, extracted unchanged by run-bounds.sh
 * (eai.inc). EAI_GetNodeParents, TickTime and the allocators are test doubles.
 *
 * Reply format: "RE\n<time>\n<seq>\n" then each parent handle followed by one space,
 * or the result code ("0 " no parents, "-1 " error) followed by one space.
 */
#include "test_support.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define EAIREADSIZE 8192

static int fail_malloc, fail_realloc;
static void *test_malloc(size_t n) { return fail_malloc ? NULL : malloc(n); }
static void *test_realloc(void *p, size_t n) { return fail_realloc ? NULL : realloc(p, n); }
#define MALLOC(t, _sz) ((t)test_malloc(_sz))
#define REALLOC(p, _sz) test_realloc((p), (_sz))
#define FREE_IF_NZ(p) do { if (p) { free(p); (p) = NULL; } } while (0)
#define ERROR_MSG(...) ((void)0)
#define ConsoleMessage(...) ((void)0)

struct tEAIHelpers { char *outBuffer; int outBufferLen; void *prv; };
struct tEAI_C_CommonFunctions { int eaiverbose; };
struct tglobal {
	struct tEAIHelpers EAIHelpers;
	struct tEAI_C_CommonFunctions EAI_C_CommonFunctions;
};
typedef struct tglobal *ttglobal;
static struct tglobal the_global;
static ttglobal gglobal(void) { return &the_global; }
static double TickTime(void) { return 12.5; }

static int parents_result;
static int *parents;
static int EAI_GetNodeParents(int cNode, int **parentNodesAdr)
{
	(void)cNode;
	if (parents_result > 0) {
		*parentNodesAdr = malloc(sizeof(int) * parents_result);
		memcpy(*parentNodesAdr, parents, sizeof(int) * parents_result);
	}
	return parents_result;
}

#include "eai.inc"

static void reset_out(const char *existing)
{
	free(the_global.EAIHelpers.outBuffer);
	the_global.EAIHelpers.outBufferLen = EAIREADSIZE;
	the_global.EAIHelpers.outBuffer = malloc(EAIREADSIZE);
	strcpy(the_global.EAIHelpers.outBuffer, existing);
	fail_malloc = fail_realloc = 0;
}

static const char *reply(int result, int *list)
{
	char arg[] = "17";
	parents_result = result;
	parents = list;
	handleGETNODEPARENTS(arg, 7);
	return the_global.EAIHelpers.outBuffer;
}

#define HEAD "RE\n12.500000\n7\n"

static void no_parents(void) { reset_out(""); CHECK(!strcmp(reply(0, NULL), HEAD "0 ")); }
static void error_result(void) { reset_out(""); CHECK(!strcmp(reply(-1, NULL), HEAD "-1 ")); }
static void one_parent(void) { int p[] = { 5 }; reset_out(""); CHECK(!strcmp(reply(1, p), HEAD "5 ")); }

static void several_parents(void)
{
	int p[] = { 5, 60, 700 };
	reset_out("");
	CHECK(!strcmp(reply(3, p), HEAD "5 60 700 "));
}

static void widest_handles(void)
{
	/* 10 and 11 characters: the old per-handle buffer held 9 */
	int p[] = { INT_MAX, INT_MIN };
	reset_out("");
	CHECK(!strcmp(reply(2, p), HEAD "2147483647 -2147483648 "));
}

static void appends_to_existing_reply(void)
{
	int p[] = { 5 };
	reset_out("earlier\nRE_EOT");
	CHECK(!strcmp(reply(1, p), "earlier\nRE_EOT" HEAD "5 "));
}

static void check_many(int count)
{
	int *p = malloc(sizeof(int) * count);
	size_t cap = (size_t)count * 12 + 64, len;
	char *want = malloc(cap);
	len = (size_t)sprintf(want, HEAD);
	for (int i = 0; i < count; i++) {
		p[i] = 100000 + i;
		len += (size_t)sprintf(want + len, "%d ", p[i]);
	}
	reset_out("");
	CHECK(!strcmp(reply(count, p), want));
	CHECK(strlen(the_global.EAIHelpers.outBuffer) == len);
	free(p);
	free(want);
}
static void near_old_buffer(void) { check_many((EAIREADSIZE - 20) / 7); }   /* just under 8192 */
static void larger_than_old_buffer(void) { check_many(5000); }             /* 35000 bytes */

static void allocation_failure(void)
{
	/* the reply cannot be built: an error result, not a partial list */
	int p[] = { 5, 6 };
	reset_out("");
	fail_malloc = 1;
	CHECK(!strcmp(reply(2, p), HEAD "-1 "));
	fail_malloc = 0;
}

static void out_buffer_growth_failure(void)
{
	/* outBufferCat keeps the existing reply if it cannot grow the buffer */
	char *big = malloc(EAIREADSIZE * 2);
	memset(big, 'x', EAIREADSIZE * 2 - 1);
	big[EAIREADSIZE * 2 - 1] = '\0';
	reset_out("keep");
	fail_realloc = 1;
	outBufferCat(big);
	CHECK(the_global.EAIHelpers.outBuffer != NULL);
	if (the_global.EAIHelpers.outBuffer) CHECK(!strcmp(the_global.EAIHelpers.outBuffer, "keep"));
	fail_realloc = 0;
	outBufferCat(big);
	CHECK(strlen(the_global.EAIHelpers.outBuffer) == 4 + EAIREADSIZE * 2 - 1);
	free(big);
	free(the_global.EAIHelpers.outBuffer);
	the_global.EAIHelpers.outBuffer = NULL;
}

static const ct_case cases[] = {
	{ "no parents", no_parents },
	{ "error result", error_result },
	{ "one parent", one_parent },
	{ "several parents", several_parents },
	{ "widest handles", widest_handles },
	{ "appends to existing reply", appends_to_existing_reply },
	{ "reply near old 8192-byte buffer", near_old_buffer },
	{ "reply larger than old buffer", larger_than_old_buffer },
	{ "allocation failure gives error result", allocation_failure },
	{ "outBufferCat growth failure keeps reply", out_buffer_growth_failure },
};
const ct_suite ct_eai_suite = { "eai-node-parents", cases, CT_COUNT(cases) };
