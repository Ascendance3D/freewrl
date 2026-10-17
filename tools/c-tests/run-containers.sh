#!/bin/sh
# Host-only tests for FreeWRL's container code. Compiles the real
# freex3d/src/lib/scenegraph/Vector.c and freex3d/src/lib/list.c with the Mac app's
# config.h, links them with the tests in this directory, and runs the result.
# Nothing here starts FreeWRL, opens a window, creates a GL context or loads a world.
#
#   tools/c-tests/run-containers.sh                  routine run (CI); nonzero on failure
#   tools/c-tests/run-containers.sh --known-defects  also run known_defects/ reproducers
#
# A reproducer exits 42 when its defect reproduces normally and 0 when it no longer
# does; any other status (sanitizer report, crash, signal) fails the run.
#
# Build output goes to a temporary directory that is removed on exit.
# CC defaults to clang. The test binary (only) is built with AddressSanitizer and
# UndefinedBehaviorSanitizer; any sanitizer report stops the run with a nonzero status.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
lib=$root/freex3d/src/lib
known=0
[ "${1:-}" = --known-defects ] && known=1

CC=${CC:-clang}
out=$(mktemp -d "${TMPDIR:-/tmp}/freewrl-c-tests.XXXXXX")
trap 'rm -rf "$out"' EXIT INT TERM

san="-fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer"
cflags="-std=c17 -g -O0 $san"
inc="-I$root/OSX_gui/FreeWRL-Desktop/FreeWRL -I$lib -I$root/freex3d/src/libtess"
export ASAN_OPTIONS=${ASAN_OPTIONS:-halt_on_error=1:detect_stack_use_after_return=1}
export UBSAN_OPTIONS=${UBSAN_OPTIONS:-halt_on_error=1:print_stacktrace=1}

# production sources exactly as they are, with the app's defines; no extra warnings
$CC $cflags $inc -c "$lib/scenegraph/Vector.c" -o "$out/Vector.o"
$CC $cflags $inc -c "$lib/list.c" -o "$out/list.o"
for t in test_main test_vector test_list; do
	$CC $cflags -Wall -Wextra -Werror $inc -c "$here/$t.c" -o "$out/$t.o"
done
$CC $san -o "$out/test_containers" "$out/test_main.o" "$out/test_vector.o" "$out/test_list.o" \
	"$out/Vector.o" "$out/list.o"

status=0
"$out/test_containers" || status=1

if [ $known = 1 ]; then
	for f in "$here"/known_defects/*.c; do
		n=$(basename "$f" .c)
		$CC $cflags -Wall -Wextra -Werror $inc "$f" "$out/list.o" -o "$out/kd_$n"
		echo "-- known defect: $n"
		rc=0
		"$out/kd_$n" || rc=$?
		case $rc in
		42) echo "-- $n: known defect reproduced as expected (exit 42)" ;;
		0) echo "-- $n: defect no longer reproduces; review and retire this reproducer" ;;
		*) echo "-- $n: UNEXPECTED FAILURE (exit $rc; not the expected-defect status 42)"
		   status=1 ;;
		esac
	done
fi
exit $status
