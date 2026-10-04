#!/bin/sh
# Host-only tests for bounds and data-safety logic in FreeWRL library code:
#   Component_HAnim.c    parse_float_values and its tokenizer
#   LoadTextures.c       GeneratedTexture blank-texture size checks
#   LoadTextures.c       web3dit, .vol and NRRD texture file headers
#   Compositing_Shaders.c shader PLUG compositing (Plug, AddDefine0, ...)
#   EAIEventsIn.c        GETNODEPARENTS reply, with outBufferCat (EAIHelpers.c)
#   io_files.c           fw_temp_file_create, fw_temp_dir_create
#   RenderFuncs.c        push_ray, pop_ray (the picking pass ray stack), with Vector.c
#   MainLoop.c           setSensitive, unRegisterSensitiveNode, freeContainerNode,
#                        sendSensorEvents, with
#   CParseParser.c       gc_broto_instance (pointing-device sensors freed with their world)
#   CParseParser.c       cParseErrorCurID, cParseErrorFieldString, with
#   ConsoleMessage.c     fwvsnprintf, ConsoleMessage0, ConsoleMessage (world text is not a format)
#   BVHreader.c          read_bvh_blob, the .bvh motion-capture parser (included whole)
# The functions are copied unchanged out of the real sources by extract.awk and
# compiled with small test doubles for what they call; nothing is reimplemented.
# Nothing here starts FreeWRL, opens a window, creates a GL context or loads a world.
#
#   tools/c-tests/run-bounds.sh                 run every suite; nonzero on failure
#   tools/c-tests/run-bounds.sh SUITE [INDEX]   run one suite or one test of it
#
# The test binary is built with AddressSanitizer and UndefinedBehaviorSanitizer; any
# report stops the run with a nonzero status. CC defaults to cc.
# Build output goes to a temporary directory that is removed on exit.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
lib=$root/freex3d/src/lib

CC=${CC:-cc}
out=$(mktemp -d "${TMPDIR:-/tmp}/freewrl-bounds-tests.XXXXXX")
trap 'rm -rf "$out"' EXIT INT TERM

san="-fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer"
cflags="-std=gnu17 -g -O0 $san"
export ASAN_OPTIONS=${ASAN_OPTIONS:-halt_on_error=1:detect_stack_use_after_return=1}
export UBSAN_OPTIONS=${UBSAN_OPTIONS:-halt_on_error=1:print_stacktrace=1}

# LC_ALL=C: the sources hold non-UTF-8 byte literals (e.g. the JPEG magic in
# LoadTextures.c), which a UTF-8 awk rejects; read them as bytes.
x() { LC_ALL=C awk -v fn="$2" -v to="${3:-}" -f "$here/extract.awk" "$lib/$1"; }
{
	x scenegraph/Component_HAnim.c char_is_separator
	x scenegraph/Component_HAnim.c next_token
	x scenegraph/Component_HAnim.c next_buffer_token
	x scenegraph/Component_HAnim.c parse_float_values
} > "$out/hanim.inc"
x opengl/LoadTextures.c texture_load_blank_Texture > "$out/texture.inc"
{
	# the size limits are macros, not functions: copy their lines unchanged
	LC_ALL=C grep -E '^#define (TEXTURE_FILE_MAX_AXIS|TEXTURE_FILE_MAX_RGBA|WEB3DIT_MAX_RGBA|VOL_MAX_RGBA) ' \
		"$lib/opengl/LoadTextures.c"
	x opengl/LoadTextures.c texture_mul_size texture_file_pixels
	x opengl/LoadTextures.c loadImage_web3dit
	x opengl/LoadTextures.c loadImage3DVol
	x opengl/LoadTextures.c isMachineLittleEndian loadImage_nrrd
} > "$out/texheader.inc"
x opengl/Compositing_Shaders.c dupRange AddDefine > "$out/shader.inc"
{
	x input/EAIHelpers.c outBufferCat
	x input/EAIEventsIn.c handleGETNODEPARENTS
} > "$out/eai.inc"
x io_files.c temp_template fw_temp_dir_create > "$out/tempfile.inc"
{
	x scenegraph/Vector.c newVector_ deleteVector_
	x scenegraph/Vector.c vector_ensureSpace_
	x scenegraph/Vector.c vector_removeElement
} > "$out/vector.inc"
x scenegraph/RenderFuncs.c push_ray pop_ray > "$out/pickray.inc"
{
	x main/MainLoop.c setSensitive freeContainerNode
	x main/MainLoop.c sendSensorEvents
	x vrml_parser/CParseParser.c gc_broto_instance
} > "$out/sensors.inc"
x main/ConsoleMessage.c fwvsnprintf ConsoleMessage > "$out/consolemsg.inc"
x vrml_parser/CParseParser.c cParseErrorCurID cParseErrorFieldString > "$out/parseerror.inc"

objs=
for t in test_bounds_main test_hanim test_texture test_texture_header test_shader_plug test_eai_reply test_tempfile \
	test_pick_ray test_sensor_lifetime test_parse_error; do
	# built like the production sources: no extra warning flags, since each test
	# includes extracted production code
	$CC $cflags \
		-I"$here" -I"$out" -I"$lib/scenegraph" -c "$here/$t.c" -o "$out/$t.o"
	objs="$objs $out/$t.o"
done
# BVHreader.c is included whole by test_bvh.c. It includes <config.h> and <malloc.h>;
# it uses neither, so empty stand-ins let it build the same way on Linux and macOS.
mkdir "$out/bvh-include"
: > "$out/bvh-include/config.h"
echo '#include <stdlib.h>' > "$out/bvh-include/malloc.h"
$CC $cflags -Wno-macro-redefined -I"$here" -I"$out/bvh-include" -I"$lib/scenegraph" \
	-c "$here/test_bvh.c" -o "$out/test_bvh.o"
objs="$objs $out/test_bvh.o"
$CC $san -o "$out/test_bounds" $objs -lm
"$out/test_bounds" "$@"
