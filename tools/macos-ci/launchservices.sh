#!/bin/bash
# launchservices.sh APP [OUTDIR] : the live macOS document-routing gate. MANDATORY release-QA step
# before packaging a build for distribution (see tools/macos-package/README.md).
#
# It opens each world THROUGH LaunchServices -- `open -a <APP path>`, exactly what Finder
# double-click and `open -a FreeWRL world.wrl` do -- never the inner binary, and proves the routed
# document reaches FreeWRL's loader ("file to load: <path>"), the renderer starts, and no load
# error or crash occurs. Covers .wrl/.wrz/.wrlz, .x3d/.x3dz, .x3dv/.x3dvz.
#
# Requires a login/GUI session, so it is not a CI gate (GitHub runners have none); CI runs the
# deterministic static gate tools/macos-ci/doctypes.sh instead. Run one FreeWRL at a time.
set -uo pipefail
APP=${1:?usage: launchservices.sh /path/to/FreeWRL.app [outdir]}
# physical paths: LaunchServices starts the app and opens documents by their real paths
# (/private/var/folders/..., no //), which kill_fw, the running check and "file to load:" match
APP=$(cd "$APP" && pwd -P) || exit 1
EXE="$APP/Contents/MacOS/FreeWRL"
SRC=$(cd "$(dirname "$0")/../.." && pwd)
T="$SRC/freewrl/tests"
OUT=${2:-$(mktemp -d)}; mkdir -p "$OUT" && OUT=$(cd "$OUT" && pwd -P) || exit 1; W="$OUT/worlds"; LOG="$OUT/logs"; mkdir -p "$W" "$LOG"
CRASH=~/Library/Logs/DiagnosticReports
LSREG=/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister
SEC=9

# self-contained fixtures: a texture-free VRML world, a self-contained X3D/X3DV, + gzip variants
cp "$T/1.wrl"                  "$W/world.wrl"
cp "$T/1.x3d"                  "$W/world.x3d";   cp -R "$T/helpers" "$W/helpers"   # 1.x3d refs helpers/
cp "$T/JohnCarlson/waves.x3dv" "$W/world.x3dv"
gzip -c "$W/world.wrl"  > "$W/world.wrz";  gzip -c "$W/world.wrl"  > "$W/world.wrlz"
gzip -c "$W/world.x3d"  > "$W/world.x3dz"; gzip -c "$W/world.x3dv" > "$W/world.x3dvz"

"$LSREG" -f "$APP" >/dev/null 2>&1     # disposable registration of THIS build
kill_fw(){ pkill -KILL -f "$EXE" 2>/dev/null; sleep 1; }
pass=0; total=0
for f in world.wrl world.wrz world.wrlz world.x3d world.x3dz world.x3dv world.x3dvz; do
  total=$((total+1)); o="$LOG/$f.out"; e="$LOG/$f.err"; : >"$o"; : >"$e"
  kill_fw
  before=$(ls "$CRASH"/FreeWRL* 2>/dev/null | wc -l | tr -d ' ')
  open --stdout "$o" --stderr "$e" -a "$APP" "$W/$f"; orc=$?
  for i in $(seq $((SEC*2))); do sleep 0.5; done
  running=$(ps -Ao comm= | grep -cF "$EXE")
  after=$(ls "$CRASH"/FreeWRL* 2>/dev/null | wc -l | tr -d ' ')
  L=$(cat "$o" "$e" 2>/dev/null); kill_fw
  loaded=$(printf '%s\n' "$L" | grep -F "file to load: $W/$f")
  renderer=$(printf '%s\n' "$L" | grep -m1 GL_RENDERER)
  err=$(printf '%s\n' "$L" | grep -iE "cannot open|could not|not found|no such|failed to (open|load|read|parse)|invalid|unrecognized|problem with (VERTEX|FRAGMENT) shader|GL error" | grep -viE "unloadable|zero texture" | head -1)
  v=PASS; why=""
  [ "$orc" -ne 0 ]        && { v=FAIL; why="$why open-rc=$orc"; }
  [ "$running" -lt 1 ]    && { v=FAIL; why="$why not-running"; }
  [ -z "$loaded" ]        && { v=FAIL; why="$why document-not-routed-to-loader"; }
  [ -z "$renderer" ]      && { v=FAIL; why="$why no-GL_RENDERER"; }
  [ -n "$err" ]           && { v=FAIL; why="$why err:'$err'"; }
  [ "$((after-before))" -gt 0 ] && { v=FAIL; why="$why crashreport"; }
  [ "$v" = PASS ] && pass=$((pass+1))
  printf '%-7s %-12s%s\n' "$v" "$f" "${why:+ FAIL:$why}"
done
kill_fw
echo "LAUNCHSERVICES $pass/$total  (logs: $LOG)"
[ "$pass" = "$total" ]
