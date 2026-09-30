/*
 * Shader compositing (Castle Game Engine PLUGs): the code from dupRange through
 * AddDefine, extracted unchanged from freex3d/src/lib/opengl/Compositing_Shaders.c
 * by run-bounds.sh (shader.inc). Tests go through Plug, AddDefine0, AddVersion0 and
 * AddExtension, which own CompleteCode[] (heap strings) and replace them.
 */
#include "test_support.h"
#include <ctype.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

#define TRUE 1
#define FALSE 0
#define UNUSED(v) ((void)(v))
#define FREE_IF_NZ(p) do { if (p) { free(p); (p) = NULL; } } while (0)
enum TShaderType { SHADERPART_VERTEX, SHADERPART_GEOMETRY, SHADERPART_FRAGMENT };

static int console_messages;
static void ConsoleMessage(const char *fmt, ...) { (void)fmt; console_messages++; }

#include "shader.inc"

static char *code[3];

static void set_code(const char *text)
{
	for (int i = 0; i < 3; i++) FREE_IF_NZ(code[i]);
	code[SHADERPART_FRAGMENT] = strdup(text);
	console_messages = 0;
}

static char *repeat(char c, size_t n)
{
	char *s = malloc(n + 1);
	memset(s, c, n);
	s[n] = '\0';
	return s;
}

static char *join(const char *a, const char *b, const char *c, const char *d, const char *e)
{
	size_t n = strlen(a) + strlen(b) + strlen(c) + strlen(d) + strlen(e);
	char *s = malloc(n + 1);
	strcpy(s, a); strcat(s, b); strcat(s, c); strcat(s, d); strcat(s, e);
	return s;
}

#define MAIN "/* PLUG-DECLARATIONS */\nvoid main(){\n/* PLUG: fog_apply (color, N) */\n}\n"
#define FOG "void PLUG_fog_apply (inout vec4 c, in vec3 n){ c.r = 1.0; }\n"

static void normal_plug(void)
{
	int u = 0;
	set_code(MAIN);
	Plug(SHADERPART_FRAGMENT, FOG, code, &u);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT],
		"void fog_apply_0(inout vec4 c, in vec3 n);\n"
		"/* PLUG-DECLARATIONS */\nvoid main(){\n"
		"fog_apply_0(color, N);\n/* PLUG: fog_apply (color, N) */\n}\n"
		"void fog_apply_0 (inout vec4 c, in vec3 n){ c.r = 1.0; }\n"));
	CHECK(u == 1);
	CHECK(console_messages == 0);
}

static void two_plug_points_and_two_plugs(void)
{
	int u = 0;
	set_code("/* PLUG-DECLARATIONS */\n/* PLUG: a (x) */\n/* PLUG: a (y) */\n/* PLUG: b (z) */\n");
	Plug(SHADERPART_FRAGMENT, "void PLUG_a (float p){}\nvoid PLUG_b (float q){}\n", code, &u);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT],
		"void a_0(float p);\nvoid b_1(float q);\n/* PLUG-DECLARATIONS */\n"
		"a_0(x);\n/* PLUG: a (x) */\na_0(y);\n/* PLUG: a (y) */\nb_1(z);\n/* PLUG: b (z) */\n"
		"void a_0 (float p){}\nvoid b_1 (float q){}\n"));
	CHECK(u == 2);
}

static void undeclared_plug_is_still_appended(void)
{
	int u = 0;
	set_code(MAIN);
	Plug(SHADERPART_FRAGMENT, "void PLUG_other (float p){}\n", code, &u);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT],
		MAIN "void other_0 (float p){}\n"));
	CHECK(console_messages == 1);
}

static void library_without_plug(void)
{
	int u = 0;
	set_code(MAIN);
	Plug(SHADERPART_FRAGMENT, "float helper(float x){ return x; }\n", code, &u);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT],
		MAIN "float helper(float x){ return x; }\n"));
	CHECK(u == 0);
}

static void missing_part_is_ignored(void)
{
	int u = 0;
	set_code(MAIN);
	Plug(SHADERPART_VERTEX, FOG, code, &u);
	CHECK(code[SHADERPART_VERTEX] == NULL);
	CHECK(!strcmp(code[SHADERPART_FRAGMENT], MAIN));
}

/* a name of n characters in both the plug and the plug point */
static void long_name(size_t n)
{
	int u = 0;
	char *name = repeat('q', n);
	char *main_code = join("/* PLUG-DECLARATIONS */\n/* PLUG: ", name, " (x) */\n", "", "");
	char *plug = join("void PLUG_", name, " (float p){}\n", "", "");
	char *expect = malloc(4 * n + 200);
	sprintf(expect, "void %s_0(float p);\n/* PLUG-DECLARATIONS */\n%s_0(x);\n/* PLUG: %s (x) */\n"
		"void %s_0 (float p){}\n", name, name, name, name);
	set_code(main_code);
	Plug(SHADERPART_FRAGMENT, plug, code, &u);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT], expect));
	CHECK(console_messages == 0);
	free(name); free(main_code); free(plug); free(expect);
}
static void name_94(void) { long_name(94); }   /* fits every old buffer */
static void name_99(void) { long_name(99); }   /* old PlugName[100] limit */
static void name_100(void) { long_name(100); }
static void name_300(void) { long_name(300); }

static void long_parameters(size_t n)
{
	int u = 0;
	char *pad = repeat('p', n);
	char *main_code = join("/* PLUG-DECLARATIONS */\n/* PLUG: f (", pad, ") */\n", "", "");
	char *plug = join("void PLUG_f (float ", pad, "){}\n", "", "");
	char *expect = malloc(4 * n + 200);
	sprintf(expect, "void f_0(float %s);\n/* PLUG-DECLARATIONS */\nf_0(%s);\n/* PLUG: f (%s) */\n"
		"void f_0 (float %s){}\n", pad, pad, pad, pad);
	set_code(main_code);
	Plug(SHADERPART_FRAGMENT, plug, code, &u);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT], expect));
	free(pad); free(main_code); free(plug); free(expect);
}
static void params_490(void) { long_parameters(490); }   /* old call buffer is 500 */
static void params_2000(void) { long_parameters(2000); } /* old parameter buffers are 1000 */

static void malformed_plug_declaration(void)
{
	/* "void PLUG_" with no parameter list: skipped, the text is still appended */
	const char *plugs[] = { "void PLUG_broken", "void PLUG_broken (float p", "void PLUG_" };
	for (int i = 0; i < CT_COUNT(plugs); i++) {
		int u = 0;
		char *expect = join(MAIN, plugs[i], "", "", "");
		set_code(MAIN);
		Plug(SHADERPART_FRAGMENT, plugs[i], code, &u);
		CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT], expect));
		CHECK(u == 0);
		CHECK(console_messages > 0);
		free(expect);
	}
}

static void malformed_plug_point(void)
{
	/* plug points without a parameter list are skipped; a later good one is used */
	const char *mains[] = {
		"/* PLUG: fog_apply",
		"/* PLUG: fog_apply (color",
		"/* PLUG: ",
	};
	for (int i = 0; i < CT_COUNT(mains); i++) {
		int u = 0;
		char *main_code = join(mains[i], "\n/* PLUG: fog_apply (c, n) */\n", "", "", "");
		set_code(main_code);
		Plug(SHADERPART_FRAGMENT, FOG, code, &u);
		CHECK(code[SHADERPART_FRAGMENT] != NULL);
		if (code[SHADERPART_FRAGMENT]) {
			CHECK(strstr(code[SHADERPART_FRAGMENT], "fog_apply_0(c, n);\n/* PLUG: fog_apply (c, n) */") != NULL);
			CHECK(!strncmp(code[SHADERPART_FRAGMENT], "void fog_apply_0(inout vec4 c, in vec3 n);\n", 43));
		}
		free(main_code);
	}
}

static void code_longer_than_old_buffer(void)
{
	/* main code of 70000 bytes; the old Code buffer held 65533 characters */
	int u = 0;
	char *body = repeat(' ', 70000);
	char *main_code = join(MAIN, body, "", "", "");
	char *expect = join("void fog_apply_0(inout vec4 c, in vec3 n);\n"
		"/* PLUG-DECLARATIONS */\nvoid main(){\n"
		"fog_apply_0(color, N);\n/* PLUG: fog_apply (color, N) */\n}\n", body,
		"void fog_apply_0 (inout vec4 c, in vec3 n){ c.r = 1.0; }\n", "", "");
	set_code(main_code);
	Plug(SHADERPART_FRAGMENT, FOG, code, &u);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT], expect));
	free(body); free(main_code); free(expect);
}

static void plug_longer_than_old_buffer(void)
{
	/* a plug of 20000 bytes; the old Plug buffer held 16383 characters */
	int u = 0;
	char *body = repeat(' ', 20000);
	char *plug = join("void PLUG_fog_apply (inout vec4 c, in vec3 n){", body, "}\n", "", "");
	char *expect = join("void fog_apply_0(inout vec4 c, in vec3 n);\n"
		"/* PLUG-DECLARATIONS */\nvoid main(){\n"
		"fog_apply_0(color, N);\n/* PLUG: fog_apply (color, N) */\n}\n",
		"void fog_apply_0 (inout vec4 c, in vec3 n){", body, "}\n", "");
	set_code(MAIN);
	Plug(SHADERPART_FRAGMENT, plug, code, &u);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT], expect));
	free(body); free(plug); free(expect);
}

static void defines_version_extension(void)
{
	set_code("/*EXTENSIONS */\n/* DEFINES */\nvoid main(){}\n");
	AddDefine0(SHADERPART_FRAGMENT, "FULL", 1, code);
	AddVersion0(SHADERPART_FRAGMENT, 410, "core", code);
	AddExtension(SHADERPART_FRAGMENT, "GL_ARB_x", "enable", code);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT],
		"#version 410 core\n#extension GL_ARB_x : enable\n/*EXTENSIONS */\n"
		"#define FULL 1 \n/* DEFINES */\nvoid main(){}\n"));
	/* no marker: nothing changes */
	set_code("void main(){}\n");
	AddDefine0(SHADERPART_FRAGMENT, "FULL", 1, code);
	AddExtension(SHADERPART_FRAGMENT, "GL_ARB_x", "enable", code);
	CHECK(!strcmp(code[SHADERPART_FRAGMENT], "void main(){}\n"));
}

static void define_in_code_longer_than_old_buffer(void)
{
	char *body = repeat(' ', 70000);
	char *main_code = join(body, "/* DEFINES */\n", "", "", "");
	char *expect = join(body, "#define FULL 1 \n/* DEFINES */\n", "", "", "");
	set_code(main_code);
	AddDefine0(SHADERPART_FRAGMENT, "FULL", 1, code);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT], expect));
	free(body); free(main_code); free(expect);
}

static void long_define_name(void)
{
	char *name = repeat('D', 2000);
	char *expect = join("#define ", name, " 7 \n/* DEFINES */\n", "", "");
	set_code("/* DEFINES */\n");
	AddDefine0(SHADERPART_FRAGMENT, name, 7, code);
	CHECK(code[SHADERPART_FRAGMENT] && !strcmp(code[SHADERPART_FRAGMENT], expect));
	free(name); free(expect);
	for (int i = 0; i < 3; i++) FREE_IF_NZ(code[i]);
}

static const ct_case cases[] = {
	{ "normal plug", normal_plug },
	{ "two plug points, two plugs", two_plug_points_and_two_plugs },
	{ "undeclared plug is still appended", undeclared_plug_is_still_appended },
	{ "library without PLUG_", library_without_plug },
	{ "missing shader part is ignored", missing_part_is_ignored },
	{ "plug name of 94 characters", name_94 },
	{ "plug name of 99 characters", name_99 },
	{ "plug name of 100 characters", name_100 },
	{ "plug name of 300 characters", name_300 },
	{ "parameters of 490 characters", params_490 },
	{ "parameters of 2000 characters", params_2000 },
	{ "malformed PLUG_ declaration", malformed_plug_declaration },
	{ "malformed PLUG: point", malformed_plug_point },
	{ "main code longer than old buffer", code_longer_than_old_buffer },
	{ "plug longer than old buffer", plug_longer_than_old_buffer },
	{ "define, version, extension", defines_version_extension },
	{ "define in code longer than old buffer", define_in_code_longer_than_old_buffer },
	{ "define name of 2000 characters", long_define_name },
};
const ct_suite ct_shader_suite = { "shader-plug", cases, CT_COUNT(cases) };
