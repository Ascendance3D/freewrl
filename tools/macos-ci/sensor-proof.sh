#!/bin/bash
# sensor-proof.sh APP OUTDIR [SECONDS] : prove the pointing-device sensor path end to end, one
# FreeWRL at a time, with the pointer driven through dllFreeWRL_onMouse (reloader.py; the
# picking pass, not a marker shortcut) and no world replacement.
#   10.wrl               the arrow's PROTO SphereSensor: a breakpoint on do_SphereSensor counts
#                        its calls by event; hover, press, drag and release must each occur.
#                        The pointer is on arrow A1's cone, SPHERE_POINTER (default 620,328
#                        backing pixels: the app's default 672x512 window on a 2x display)
#   sensor_replace.wrl   its Script must print SENSOR_TOUCH_OVER, SENSOR_TOUCH_TIME,
#                        SENSOR_SPHERE, SENSOR_PLANE and SENSOR_CYLINDER (the sensors fire);
#                        its box fills the view, RELOAD_POINTER (default 300,300) as suite.sh
# Prints one PASS/FAIL line per world and SENSORPROOF n/2; exit 1 unless 2/2.
H=$(cd "$(dirname "$0")" && pwd); R=$(cd "$H/../.." && pwd)
APP=${1:?usage: sensor-proof.sh APP OUTDIR [SECONDS]} OUT=${2:?usage: sensor-proof.sh APP OUTDIR [SECONDS]} SEC=${3:-40}
T=$R/freewrl/tests; G=$T/regression; mkdir -p "$OUT"
export RELOAD_PERIOD=90
unset RELOAD_PATHS
pass=0
res=$(RELOAD_POINTER=${SPHERE_POINTER:-620,328} TRACE_SENSOR=do_SphereSensor "$H/run.sh" "$APP" "$T/10.wrl" "$SEC" "$OUT/sphere-10wrl")
why=""
echo "$res" | grep -q 'HARNESS:' && why="$why harness-fault"
echo "$res" | grep -qE 'CRASH:|malloc=[^n]' && why="$why crash"
for ev in hover press drag release; do echo "$res" | grep -qE "$ev=[1-9]" || why="$why no-$ev"; done
[ -z "$why" ] && { v=PASS; pass=$((pass+1)); } || v=FAIL
echo "$v 10.wrl SphereSensor: $res${why:+ FAIL:$why}"
res=$(RELOAD_POINTER=${RELOAD_POINTER:-300,300} "$H/run.sh" "$APP" "$G/sensor_replace.wrl" "$SEC" "$OUT/markers-sensor_replace")
why=""
echo "$res" | grep -q 'HARNESS:' && why="$why harness-fault"
echo "$res" | grep -qE 'CRASH:|malloc=[^n]' && why="$why crash"
for m in SENSOR_TOUCH_OVER SENSOR_TOUCH_TIME SENSOR_SPHERE SENSOR_PLANE SENSOR_CYLINDER; do
	grep -qo "$m" "$OUT/markers-sensor_replace.out" "$OUT/markers-sensor_replace.err" 2>/dev/null || why="$why no-$m"
done
[ -z "$why" ] && { v=PASS; pass=$((pass+1)); } || v=FAIL
echo "$v sensor_replace.wrl markers: $res${why:+ FAIL:$why}"
echo "SENSORPROOF $pass/2"
[ "$pass" = 2 ]
