#!/bin/sh
# Host-only tests for bounds and data-safety logic in FreeWRL library code:
#   Component_HAnim.c    parse_float_values and its tokenizer
#   LoadTextures.c       GeneratedTexture blank-texture size checks
#   Compositing_Shaders.c shader PLUG compositing (Plug, AddDefine0, ...)
#   EAIEventsIn.c        GETNODEPARENTS reply, with outBufferCat (EAIHelpers.c)
#   io_files.c           fw_temp_file_create, fw_temp_dir_create
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

x() { awk -v fn="$2" -v to="${3:-}" -f "$here/extract.awk" "$lib/$1"; }
{
	x scenegraph/Component_HAnim.c char_is_separator
	x scenegraph/Component_HAnim.c next_token
	x scenegraph/Component_HAnim.c next_buffer_token
	x scenegraph/Component_HAnim.c parse_float_values
} > "$out/hanim.inc"
x opengl/LoadTextures.c texture_load_blank_Texture > "$out/texture.inc"
x opengl/Compositing_Shaders.c dupRange AddDefine > "$out/shader.inc"
{
	x input/EAIHelpers.c outBufferCat
	x input/EAIEventsIn.c handleGETNODEPARENTS
} > "$out/eai.inc"
x io_files.c temp_template fw_temp_dir_create > "$out/tempfile.inc"

objs=
for t in test_bounds_main test_hanim test_texture test_shader_plug test_eai_reply test_tempfile; do
	# built like the production sources: no extra warning flags, since each test
	# includes extracted production code
	$CC $cflags \
		-I"$here" -I"$out" -c "$here/$t.c" -o "$out/$t.o"
	objs="$objs $out/$t.o"
done
$CC $san -o "$out/test_bounds" $objs -lm
"$out/test_bounds" "$@"
