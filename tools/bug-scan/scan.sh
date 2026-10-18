#!/bin/sh
# Static bug scan of FreeWRL on Linux: gcc -fanalyzer with -Wall -Wextra over the X11 Autotools
# build, cppcheck over freex3d/src, and a TODO/FIXME/XXX inventory. Writes the logs and
# findings.json (see findings.py) to OUTDIR; file_issues.py turns findings.json into issues.
#
# usage: scan.sh [-j jobs] [-m MB] [-o outdir]
#   -j  parallel jobs for make and cppcheck  (default: nproc, capped at one job per 2.5 GB of
#       MemAvailable: one -fanalyzer compile can take 2.4 GB, and an 8-core 6 GB runner ran out)
#   -m  virtual memory limit per compiler process, in MB (default: none). A file whose analysis
#       needs more fails alone ("virtual memory exhausted" or an internal compiler error in
#       gcc.log, counted in the inventory); one
#       -fanalyzer compile reached 5.3 GB on the 6 GB runner.
#   -o  output directory                     (default: ./bug-scan-out)
#
# Run from anywhere in a checkout; the source tree is only read, apart from autogen.sh output.
# The build is out of tree in a temporary directory. Needs the FreeWRL X11 build dependencies,
# autotools and gcc 13+; cppcheck is skipped with a note when it is not installed. A failed
# compile is recorded in gcc.log (make -k) and does not stop the scan.
set -eu
H=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$H/../.." && pwd)
JOBS= OUT= MEM=
while getopts "j:m:o:" opt; do
	case $opt in
	j) JOBS=$OPTARG ;;
	m) MEM=$OPTARG ;;
	o) OUT=$OPTARG ;;
	*) sed -n '2,18p' "$0"; exit 2 ;;
	esac
done
if [ -z "$JOBS" ]; then
	mem=$(awk '/^MemAvailable:/ { print int($2 / 2621440) }' /proc/meminfo)
	JOBS=$(nproc)
	[ "${mem:-1}" -lt "$JOBS" ] && JOBS=$mem
	[ "$JOBS" -ge 1 ] || JOBS=1
fi
case $MEM in
''|[1-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]|[1-9][0-9][0-9][0-9][0-9]) ;;
*) echo "-m needs a size in MB, 1 to 99999" >&2; exit 2 ;;
esac
OUT=${OUT:-bug-scan-out}
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
WORK=$(mktemp -d "${TMPDIR:-/tmp}/freewrl-bug-scan.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

echo "== gcc -fanalyzer ($JOBS jobs)"
(cd "$ROOT/freex3d" && ./autogen.sh) > "$OUT/autogen.log" 2>&1
(cd "$WORK" && "$ROOT/freex3d/configure" --with-target=x11 --with-javascript=duk \
	CFLAGS="-O1 -g -fanalyzer -Wall -Wextra -fdiagnostics-plain-output") > "$OUT/configure.log" 2>&1
rc=0
(if [ -n "$MEM" ]; then ulimit -v $((MEM * 1024)) || exit 3; fi
	make -C "$WORK" -k -j"$JOBS") > "$OUT/gcc.log" 2>&1 || rc=$?
[ $rc -ne 3 ] || { echo "could not set the -m $MEM memory limit" >&2; exit 1; }
[ $rc -eq 0 ] || echo "make failed; see gcc.log"
oom=$(grep -cE 'virtual memory exhausted|out of memory|internal compiler error|Killed signal terminated' "$OUT/gcc.log" || :)
[ "${oom:-0}" -eq 0 ] || echo "$oom compiles hit the memory limit or crashed (-m $MEM); see gcc.log"

if command -v cppcheck > /dev/null; then
	echo "== $(cppcheck --version)"
	(cd "$ROOT" && cppcheck -j "$JOBS" -q --enable=warning,portability --inline-suppr \
		--suppress=missingIncludeSystem --suppress=missingInclude -DHAVE_CONFIG_H -D__linux__ \
		-I freex3d/src/lib --template='{file}:{line}:{column}: {severity}: {message} [{id}]' \
		freex3d/src/lib freex3d/src/bin) 2> "$OUT/cppcheck.log"
else
	echo "== cppcheck not installed; skipped"
	: > "$OUT/cppcheck.log"
fi

echo "== TODO/FIXME/XXX"
git -C "$ROOT" grep -nIE '\b(TODO|FIXME|XXX)\b' -- 'freex3d/src/*.c' 'freex3d/src/*.h' 'freex3d/src/*.cpp' \
	> "$OUT/todo.txt" || :

python3 "$H/findings.py" "$ROOT" "$OUT"
