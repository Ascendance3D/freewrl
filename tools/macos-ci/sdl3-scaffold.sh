#!/bin/bash
# sdl3-scaffold.sh BIN OUTDIR [WORLD] [SECONDS] : check the experimental freewrl_sdl3 frontend
# (cmake -DFREEWRL_SDL3_FRONTEND=ON). It runs BIN on WORLD (default freewrl/tests/1.wrl) for
# SECONDS (default 10), closes the window with its native close button, and prints one PASS/FAIL
# line per check. Exit 1 if any check fails. Needs a GUI session; the close button and the window
# count need the Accessibility permission (without it the script sends SIGTERM, which SDL also
# turns into a quit event, and reports the window count as SKIP).
# Checks: SDL3 linkage and the loaded library (pinned version and commit from
# tools/macos-deps/build.sh, not Homebrew), the OpenGL 4.1 core context, the GL_IDENTITY line,
# the window geometry, CPU use (vsync pacing), one window, and a clean shutdown in which every
# frame calls fw_frontend_frame_hook once and dllFreeWRL_onDraw once.
H=$(cd "$(dirname "$0")" && pwd); R=$(cd "$H/../.." && pwd)
BIN=$1 OUT=$2 WORLD=${3:-$R/freewrl/tests/1.wrl} SEC=${4:-10}
[ -x "$BIN" ] && [ -n "$OUT" ] || { sed -n '2,11p' "$0"; exit 2; }
mkdir -p "$OUT"
ver=$(sed -n 's/^SDL3 \([0-9.]*\) .*/\1/p' "$R/tools/macos-deps/build.sh")
commit=$(sed -n 's/^SDL3_COMMIT=//p' "$R/tools/macos-deps/build.sh")
BREW='^[[:space:]]*(/opt/homebrew|/usr/local|/opt/local)/'
fails=0
check() { # verdict name detail
	[ "$1" = FAIL ] && fails=$((fails + 1))
	echo "$1 $2: $3"
}
ok() { if [ "$1" = 0 ]; then echo PASS; else echo FAIL; fi; }

otool -L "$BIN" > "$OUT/otool.txt"
grep -q '@rpath/libSDL3.0.dylib' "$OUT/otool.txt" && ! grep -qiE "$BREW.*sdl" "$OUT/otool.txt"
check "$(ok $?)" linkage "$(grep -o '[^[:space:]]*libSDL3[^[:space:]]*' "$OUT/otool.txt")"

FREEWRL_GL_IDENTITY=1 "$BIN" "$WORLD" > "$OUT/sdl3.out" 2> "$OUT/sdl3.err" &
pid=$!
sleep "$SEC"
if ! kill -0 $pid 2>/dev/null; then
	wait $pid; check FAIL running "exited early with status $?"; cat "$OUT/sdl3.err" | tail -5
	echo "== $fails check(s) failed"; exit 1
fi
cpu=$(ps -o %cpu= -p $pid | tr -d ' ')
lib=$(vmmap $pid 2>/dev/null | grep -o '/[^[:space:]]*libSDL3[^[:space:]]*\.dylib' | sort -u)
windows=$(osascript -e "tell application \"System Events\" to count windows of (first process whose unix id is $pid)" 2>/dev/null)
screencapture -x "$OUT/sdl3.png" 2>/dev/null || true

[ -n "$lib" ] && ! echo "$lib" | grep -qE "$BREW"
check "$(ok $?)" loaded-sdl3 "${lib:-none}"
grep -q "^SDL3_VERSION runtime=$ver revision=.*-g${commit:0:9}" "$OUT/sdl3.err"
check "$(ok $?)" sdl3-version "$(grep -m1 ^SDL3_VERSION "$OUT/sdl3.err") (pinned $ver ${commit:0:9})"
grep -q '^SDL3_GL_CONTEXT version=4.1 profile=core doublebuffer=1' "$OUT/sdl3.err"
check "$(ok $?)" gl-context "$(grep -m1 ^SDL3_GL_CONTEXT "$OUT/sdl3.err")"
grep -q '^GL_IDENTITY .*glsl="4.10" profile_mask=1 ' "$OUT/sdl3.err"
check "$(ok $?)" gl-identity "$(grep -m1 ^GL_IDENTITY "$OUT/sdl3.err")"
grep -q '^SDL3_GEOMETRY logical=672x480 ' "$OUT/sdl3.err"
check "$(ok $?)" geometry "$(grep -m1 ^SDL3_GEOMETRY "$OUT/sdl3.err")"
! grep -qE 'problem with (VERTEX|FRAGMENT) shader|GL error|failed to load' "$OUT/sdl3.err" "$OUT/sdl3.out"
check "$(ok $?)" log "no shader, GL or load error"
awk -v c="$cpu" 'BEGIN { exit !(c < 90) }'
check "$(ok $?)" cpu "${cpu}% (FAIL at 90% or more: the loop is not paced)"
if [ -z "$windows" ]; then check SKIP windows "no Accessibility permission"
else [ "$windows" = 1 ]; check "$(ok $?)" windows "$windows"; fi

how=close-button
osascript -e "tell application \"System Events\" to tell (first process whose unix id is $pid) to click (first button of window 1 whose subrole is \"AXCloseButton\")" > /dev/null 2>&1 \
	|| { how=SIGTERM; kill -TERM $pid; }
for _ in $(seq 1 100); do kill -0 $pid 2>/dev/null || break; sleep 0.1; done
if kill -0 $pid 2>/dev/null; then kill -KILL $pid; check FAIL shutdown "still running 10 s after $how"; fi
wait $pid; status=$?
frames=$(grep -m1 ^SDL3_FRAMES "$OUT/sdl3.err")
h=$(echo "$frames" | sed -n 's/.*hooks=\([0-9]*\).*/\1/p')
d=$(echo "$frames" | sed -n 's/.*draws=\([0-9]*\).*/\1/p')
s=$(echo "$frames" | sed -n 's/.*swaps=\([0-9]*\).*/\1/p')
[ $status = 0 ] && grep -q '^SDL3_EXIT clean' "$OUT/sdl3.err"
check "$(ok $?)" shutdown "$how, exit status $status"
[ -n "$h" ] && [ "$h" = "$d" ] && [ "$s" = $((d - 1)) ]
check "$(ok $?)" frames "$frames (the last draw reports shutdown and is not swapped)"
echo "== $fails check(s) failed"
[ $fails = 0 ]
