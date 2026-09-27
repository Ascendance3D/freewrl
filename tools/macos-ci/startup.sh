#!/bin/bash
# startup.sh APP OUTDIR WORLD [STARTS] [SECONDS]
# Focused start-up check: start WORLD STARTS times (default 15), SECONDS each (default 14), one
# FreeWRL at a time, and report every crash. Made for the intermittent macOS 15 crash seen once
# in freewrl/tests/8.wrl about 7 s after launch (prep_Proto <- render_hier <-
# setup_viewpoint_part2): the run window must cover that point with margin. Prints one line per
# start and a STARTUP summary naming how many crashes had prep_Proto in their backtrace.
# Exit 1 on any crash (an allocator abort counts as one); a clean exit before the window is
# reported as an early exit and does not pass the gate either.
H=$(cd "$(dirname "$0")" && pwd)
APP=$1 OUT=$2 W=$3 N=${4:-15} SEC=${5:-14}; mkdir -p "$OUT"
name=$(basename "$W"); name=${name%.*}
crashes=0 proto=0 early=0
for ((i=1; i<=N; i++)); do
	f=$OUT/start-$name-$i
	res=$("$H/run.sh" "$APP" "$W" $SEC "$f")
	tag=""
	if echo "$res" | grep -qE 'CRASH:|malloc=[^n]'; then
		crashes=$((crashes + 1))
		grep -q 'prep_Proto' "$f.lldb.log" && { proto=$((proto + 1)); tag=" prep_Proto"; }
	elif echo "$res" | grep -qE 'EXIT:exited with status = [0-8] '; then
		early=$((early + 1)); tag=" early-clean-exit"
	fi
	echo "$res$tag"
done
echo "STARTUP $name: starts=$N window=${SEC}s crashes=$crashes prep_Proto-crashes=$proto early-clean-exits=$early"
if [ $crashes = 0 ] && [ $early = 0 ]; then echo "STARTUP PASS"; else echo "STARTUP FAIL"; exit 1; fi
