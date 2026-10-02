#!/bin/bash
# run.sh APP WORLD SECONDS OUTPREFIX
# Launch FreeWRL under lldb (stops on malloc_error_break, abort, crashes) for SECONDS, then stop it.
# RELOAD_PERIOD (frames) and RELOAD_PATHS (colon list): replace the world every RELOAD_PERIOD frames
# by calling dllFreeWRL_onLoad(fwctx, path), which is what the Load button does.
# RELOAD_POINTER=X,Y (with RELOAD_PERIOD): hover, press and drag the pointer there each period
# through dllFreeWRL_onMouse, as FWGLView does, so the picking pass runs (see reloader.py).
# TRACE_SENSOR=do_SphereSensor (or another do_*Sensor): count that handler's calls by event.
# Prints one result line: reloads= counts only loads lldb made (an expression error is a
# reload-failure, not a reload); pointer-events= and pointer-failures= the same for the pointer;
# HARNESS: names a harness fault (reloader.py not armed, a failed load or pointer event).
H=$(cd "$(dirname "$0")" && pwd)
APP=$1 W=$2 SEC=$3 O=$4
EXE=$APP/Contents/MacOS/FreeWRL
{
echo "command script import $H/reloader.py"
echo "target create \"$EXE\""
echo "breakpoint set -n malloc_error_break"
echo "breakpoint set -n abort"
bp=2
if [ -n "$RELOAD_PERIOD" ]; then
  echo "breakpoint set -S animationTimer:"
  bp=$((bp+1)); echo "breakpoint command add -F reloader.cb $bp"
fi
if [ -n "$TRACE_SENSOR" ]; then
  echo "breakpoint set -n $TRACE_SENSOR"
  bp=$((bp+1)); echo "breakpoint command add -F reloader.trace $bp"
fi
[ -n "$ASAN_OPTIONS" ] && echo "settings set target.env-vars ASAN_OPTIONS=$ASAN_OPTIONS"
echo "process handle SIGUSR1 SIGUSR2 SIGPIPE -n false -p true -s false"
echo "process launch -o $O.out -e $O.err -- \"$W\""
} > $O.lldb
start=$(date +%s)
# stop it, and repeat: lldb can swallow a SIGSTOP that arrives while it evaluates an expression
# (reloader.py's world loads and pointer events), and the run would never end
( for i in $(seq $((SEC*2))); do sleep 0.5; done; while pkill -STOP -f "^$EXE"; do sleep 2; done ) &
wd=$!
lldb --batch -s $O.lldb -o "thread backtrace all" -o "script reloader.report()" -o "process kill" > $O.lldb.log 2>&1
kill $wd 2>/dev/null; pkill -KILL -f "^$EXE" 2>/dev/null
el=$(( $(date +%s) - start ))
last=$(grep -o 'stop reason = .*' $O.lldb.log | tail -1)
if echo "$last" | grep -qE 'breakpoint [12]\.|SIGABRT|EXC_'; then res="CRASH:$last"
elif grep -q "exited with status" $O.lldb.log; then res="EXIT:$(grep -o 'exited with status = [-0-9]*' $O.lldb.log | tail -1)"
else res=alive-stopped; fi
mal=$(grep -h -m1 -o "malloc: \*\*\*.*" $O.err $O.out 2>/dev/null | head -1)
loads=$(grep -c '^RELOAD [0-9]* .* OK$' $O.lldb.log)
loadfail=$(grep -c '^RELOAD [0-9]* .* FAIL' $O.lldb.log)
ptr=$(grep '^POINTER events=' $O.lldb.log | tail -1)
ptrok=$(echo "$ptr" | sed -n 's/.*events=\([0-9]*\).*/\1/p'); ptrfail=$(echo "$ptr" | sed -n 's/.*failed=\([0-9]*\).*/\1/p')
harness=
if [ -n "$RELOAD_PERIOD" ]; then
  grep -q '^RELOADER armed' $O.lldb.log || harness="$harness HARNESS:reloader-not-armed"
  [ "$loadfail" = 0 ] || harness="$harness HARNESS:reload-failures=$loadfail"
  [ "${ptrfail:-0}" = 0 ] || harness="$harness HARNESS:pointer-failures=$ptrfail"
  [ -z "$RELOAD_POINTER" ] || [ "${ptrok:-0}" -gt 0 ] || harness="$harness HARNESS:no-pointer-events"
fi
trace=$(grep '^TRACE ' $O.lldb.log | tail -1 | sed 's/^TRACE //')
# malloc= stays the last field (corpus.sh matches 'malloc=none$')
echo "$(basename $O) elapsed=${el}s reloads=$loads reload-failures=$loadfail pointer-events=${ptrok:-0} pointer-failures=${ptrfail:-0}${trace:+ trace:$trace}$harness $res malloc=${mal:-none}"
