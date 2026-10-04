/*
 * Parser error reporting (CodeQL group G01): cParseErrorCurID and
 * cParseErrorFieldString (CParseParser.c) with fwvsnprintf, ConsoleMessage0 and
 * ConsoleMessage (ConsoleMessage.c), extracted unchanged by run-bounds.sh
 * (parseerror.inc, consolemsg.inc).
 *
 * Text from a world file (the current token, the rest of the input, a field value)
 * must reach the console as data, never as a printf format, and must not overflow the
 * 800-byte message buffer. Formatted ConsoleMessage calls must keep working.
 * The messages are captured through the real callback path (ConsoleMessage0).
 * Markers such as %x and %5d are harmless: if they are interpreted, the text changes.
 */
#include "test_support.h"
#include <ctype.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

#define FALSE 0
#define TRUE 1
#ifndef min
#define min(a, b) ((a) < (b) ? (a) : (b))
#endif
#define ERROR_MSG(...) ((void)0)

/* as in ConsoleMessage.c and CParseParser.c */
#define STRING_LENGTH 4096
#define OUTLINELEN 800
#define FROMSRC 140
#define MAX_IDLEN 155 /* CParseLexer.c: lexer_setCurID never stores a longer curID */

typedef struct pConsoleMessage {
	int androidFreeSlot;
	char **androidMessageSlot;
	int androidHaveUnreadMessages;
	char FWbuffer[STRING_LENGTH];
	int maxLineLength;
	int maxLines;
	int tabSpaces;
	void (*callback[2])(char *);
	void (*callbackB[4])(void *, char *);
	void *dataB[4];
	int nbackB;
} *ppConsoleMessage;

typedef struct pCParseParser {
	int foundInputErrors;
} *ppCParseParser;

struct VRMLLexer {
	char *nextIn;
	char *curID;
};
struct VRMLParser {
	struct VRMLLexer *lexer;
};

struct tglobal_double {
	struct { void *prv; } ConsoleMessage;
	struct { void *prv; } CParseParser;
};
typedef struct tglobal_double *ttglobal;

static struct pConsoleMessage console;
static struct pCParseParser parser_state;
static struct tglobal_double tg_double = { { &console }, { &parser_state } };
#define gglobal() (&tg_double)

int ConsoleMessage(const char *fmt, ...);

#include "consolemsg.inc"
#include "parseerror.inc"

static char *last_message;
static int messages;

static void capture(char *text)
{
	free(last_message);
	last_message = strdup(text);
	messages++;
}

static void reset(void)
{
	memset(&console, 0, sizeof console);
	console.callback[0] = capture;
	free(last_message);
	last_message = NULL;
	messages = 0;
	parser_state.foundInputErrors = 0;
}

/* heap copy of exactly strlen+1 bytes, so AddressSanitizer sees any overread */
static char *heap(const char *s)
{
	char *h = malloc(strlen(s) + 1);
	strcpy(h, s);
	return h;
}

static char *repeat(char c, size_t n)
{
	char *s = malloc(n + 1);
	memset(s, c, n);
	s[n] = '\0';
	return s;
}

static int has(const char *needle)
{
	if (last_message && strstr(last_message, needle))
		return 1;
	printf("    message %s does not contain \"%s\"\n", last_message ? "" : "(none)", needle);
	if (last_message)
		printf("    message: \"%.300s\"\n", last_message);
	return 0;
}

static void report_curid(const char *str, const char *curid, const char *next)
{
	struct VRMLLexer lexer;
	struct VRMLParser parser = { &lexer };
	char *s = heap(str);
	lexer.curID = curid ? heap(curid) : NULL;
	lexer.nextIn = next ? heap(next) : NULL;
	cParseErrorCurID(&parser, s);
	free(lexer.curID);
	free(lexer.nextIn);
	free(s);
}

static void report_fieldstring(const char *str, const char *str2, const char *curid, const char *next)
{
	struct VRMLLexer lexer;
	struct VRMLParser parser = { &lexer };
	char *s = heap(str), *s2 = heap(str2);
	lexer.curID = curid ? heap(curid) : NULL;
	lexer.nextIn = next ? heap(next) : NULL;
	cParseErrorFieldString(&parser, s, s2);
	CHECK(strcmp(s, str) == 0); /* the caller's text is not modified */
	free(lexer.curID);
	free(lexer.nextIn);
	free(s2);
	free(s);
}

static void normal_parse_error(void)
{
	reset();
	report_curid("Expected default value for field!", "Transform", "{ children [] }");
	CHECK(messages == 1);
	CHECK(parser_state.foundInputErrors == 1);
	CHECK(last_message && strcmp(last_message,
		"Expected default value for field!; current token :Transform:  at: \"{ children [] }\"") == 0);
}

static void no_token_no_input(void)
{
	reset();
	report_curid("ERROR: Expected a closing brace after fields of a node;", NULL, NULL);
	CHECK(last_message && strcmp(last_message,
		"ERROR: Expected a closing brace after fields of a node;") == 0);
}

static void token_percent_is_text(void)
{
	/* IS_ID_REST accepts '%', so a VRML name can hold format characters */
	reset();
	report_curid("ERROR:Expected an X3D node in a DEF statement, got \"", "Mark%xMark", "rest");
	CHECK(has("current token :Mark%xMark:"));
}

static void input_format_tokens_are_text(void)
{
	reset();
	report_curid("Expected a string after a META keyword", "META", "%d%x%c%% %5d%%%%");
	CHECK(has("at: \"%d%x%c%% %5d%%%%\""));
}

static void input_width_is_text(void)
{
	/* a width that would pad the message if it were interpreted */
	reset();
	report_curid("Expected a profile after a PROFILE keyword", "PROFILE", "%99d end");
	CHECK(has("at: \"%99d end\""));
	CHECK(last_message && strlen(last_message) < 200);
}

static void message_text_percent_is_text(void)
{
	/* ROUTE errors pass a message that already holds the token */
	reset();
	report_curid("ERROR:ROUTE: Expected \"TO\" found \"A%xB", "A%xB", NULL);
	CHECK(has("found \"A%xB; current token :A%xB:"));
}

static void longest_token_and_input(void)
{
	/* message 2000, token MAX_IDLEN, input 5000: the 800-byte buffer must hold */
	char *msg = repeat('m', 2000), *id = repeat('i', MAX_IDLEN), *next = repeat('n', 5000);
	char *want_id = malloc(MAX_IDLEN + 3);
	reset();
	report_curid(msg, id, next);
	CHECK(messages == 1);
	CHECK(last_message && strlen(last_message) < OUTLINELEN);
	snprintf(want_id, MAX_IDLEN + 3, ":%s:", id);
	CHECK(has(want_id));
	CHECK(has("nnn...\""));
	free(want_id);
	free(next);
	free(id);
	free(msg);
}

static void fieldstring_normal(void)
{
	reset();
	report_fieldstring("error finding SFNode id on line", "12x", "Shape", "x }");
	CHECK(messages == 1);
	CHECK(parser_state.foundInputErrors == 1);
	CHECK(has("error finding SFNode id on line (12x"));
	CHECK(has("Shape"));
	CHECK(has("at: \"x }\""));
}

static void fieldstring_value_percent_is_text(void)
{
	reset();
	report_fieldstring("error finding SFNode id on line", "%x%d%5d", "Id%x", "%c");
	CHECK(has("(%x%d%5d"));
	CHECK(has("Id%x"));
	CHECK(has("at: \"%c\""));
}

static void fieldstring_long_value(void)
{
	/* the field value is a whole attribute from the world file; it has no length limit */
	char *value = repeat('v', 2000), *next = repeat('n', 5000), *id = repeat('i', MAX_IDLEN);
	char *msg = repeat('m', 300);
	reset();
	report_fieldstring(msg, value, id, next);
	CHECK(messages == 1);
	CHECK(last_message && strlen(last_message) < OUTLINELEN);
	CHECK(has("vvv..."));
	free(msg);
	free(id);
	free(next);
	free(value);
}

static void console_formatted(void)
{
	reset();
	ConsoleMessage("n=%d u=%u x=%x c=%c s=%s f=%.2f e=%e pct=%% end", -5, 7u, 255u, 'Q', "abc", 1.5, 2.0);
	CHECK(last_message && strcmp(last_message,
		"n=-5 u=7 x=ff c=Q s=abc f=1.50 e=2.000000e+00 pct=% end") == 0);
	if (last_message && strcmp(last_message, "n=-5 u=7 x=ff c=Q s=abc f=1.50 e=2.000000e+00 pct=% end"))
		printf("    message: \"%s\"\n", last_message);
}

static void console_widths(void)
{
	reset();
	ConsoleMessage("[%5d][%-4s][%05.1f][%3c]", 42, "ab", 3.14159, 'z');
	CHECK(last_message && strcmp(last_message, "[   42][ab  ][003.1][  z]") == 0);
}

static void console_string_argument_is_text(void)
{
	reset();
	ConsoleMessage("%s", "keep %d %x %s %n %% as text");
	CHECK(last_message && strcmp(last_message, "keep %d %x %s %n %% as text") == 0);
}

static void console_long_string_argument(void)
{
	/* one byte short of, at and over the formatter's buffer length (STRING_LENGTH - 1) */
	for (size_t n = STRING_LENGTH - 2; n <= STRING_LENGTH + 1; n++) {
		char *s = repeat('s', n);
		reset();
		ConsoleMessage("%s", s);
		CHECK(messages == 1);
		CHECK(last_message && strlen(last_message) < STRING_LENGTH);
		free(s);
	}
}

static void console_large_width(void)
{
	/* a width larger than the formatter's buffers, from a trusted format */
	reset();
	ConsoleMessage("a%8000db", 1);
	CHECK(messages == 1);
	CHECK(last_message && strlen(last_message) < STRING_LENGTH);
	CHECK(has("a"));
}

static void console_long_literal(void)
{
	/* literal text longer than the formatter's buffers */
	char *s = repeat('L', STRING_LENGTH + 100);
	reset();
	ConsoleMessage(s);
	CHECK(messages == 1);
	CHECK(last_message && strlen(last_message) < STRING_LENGTH);
	free(s);
}

static void console_trailing_percent(void)
{
	/* a lone '%' at the end of a trusted format must not read past the NUL */
	char *s = heap("100%");
	reset();
	ConsoleMessage(s);
	CHECK(messages == 1);
	CHECK(has("100"));
	free(s);
}

static const ct_case cases[] = {
	{ "normal parse error", normal_parse_error },
	{ "parse error with no token and no input", no_token_no_input },
	{ "token with % is text", token_percent_is_text },
	{ "input with format tokens is text", input_format_tokens_are_text },
	{ "input with a width is text", input_width_is_text },
	{ "message with % is text", message_text_percent_is_text },
	{ "longest token, long message and input", longest_token_and_input },
	{ "field string error, normal", fieldstring_normal },
	{ "field string error, % is text", fieldstring_value_percent_is_text },
	{ "field string error, 2000-character value", fieldstring_long_value },
	{ "ConsoleMessage formatted arguments", console_formatted },
	{ "ConsoleMessage widths and precision", console_widths },
	{ "ConsoleMessage %s argument is text", console_string_argument_is_text },
	{ "ConsoleMessage long %s argument", console_long_string_argument },
	{ "ConsoleMessage width larger than buffer", console_large_width },
	{ "ConsoleMessage literal longer than buffer", console_long_literal },
	{ "ConsoleMessage trailing %", console_trailing_percent },
};
const ct_suite ct_parse_error_suite = { "parse_error", cases, CT_COUNT(cases) };
