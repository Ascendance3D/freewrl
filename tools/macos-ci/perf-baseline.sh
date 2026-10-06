#!/bin/bash
# perf-baseline.sh APP OUTDIR [WORLD] [RUNS]
# Simple native performance baseline for frontend comparisons (SDL3 migration). Measures, it does
# not judge: compare only numbers from the same world on the same Mac. One FreeWRL at a time.
# Each run (default 3) prints:
#   PERF run=N ready_s=  launch to the first frame with the libFreeWRL context (fwctx) set, the
#                        point where the frontend can load a world (dllFreeWRL_onLoad)
#        first_frame_s=  launch to the first fw_frontend_frame_hook call
#        frames10s=      frames in the 10 s that start 5 s after the first frame, and the frame
#        p50_ms= p95_ms= max_ms=  interval median, 95th percentile and maximum in that window
# These run under lldb (run.sh, FRAME_STATS=1): a breakpoint per frame costs time, the same for
# any frontend that calls fw_frontend_frame_hook. Then, without lldb:
#   IDLE cpu_mean= cpu_max= samples=  CPU % of the app, 1 s top samples taken 15 s after
#        rss_mb=                       launch, with no input (the world animates if it has to)
H=$(cd "$(dirname "$0")" && pwd); R=$(cd "$H/../.." && pwd)
APP=${1:?usage: perf-baseline.sh APP OUTDIR [WORLD] [RUNS]} OUT=${2:?usage: perf-baseline.sh APP OUTDIR [WORLD] [RUNS]}
W=${3:-$R/freewrl/tests/1.wrl} N=${4:-3}
mkdir -p "$OUT"
APP=$(cd "$APP" && pwd -P) || exit 1
EXE=$APP/Contents/MacOS/FreeWRL
if pgrep -x FreeWRL >/dev/null; then echo "perf-baseline: FreeWRL is already running; run one at a time" >&2; exit 2; fi
unset RELOAD_PERIOD RELOAD_PATHS RELOAD_POINTER TRACE_SENSOR TRACE_CALLS
echo "PERF world=$(basename "$W") app=$APP macOS=$(sw_vers -productVersion) $(sysctl -n machdep.cpu.brand_string)"
for i in $(seq "$N"); do
	o=$OUT/perf-$i
	t0=$(python3 -c 'import time; print("%.3f" % time.time())')
	res=$(FRAME_STATS=1 "$H/run.sh" "$APP" "$W" 25 "$o")
	armed=$(sed -n 's/^RELOADER armed.* t=\([0-9.]*\)$/\1/p' "$o.lldb.log" | head -1)
	frames=$(grep '^FRAMES ' "$o.lldb.log" | tail -1)
	python3 - "$i" "$t0" "${armed:-0}" "$frames" "$res" <<'EOF'
import re, sys
i, t0, armed, frames, res = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
f = dict(re.findall(r"(\w+)=([-0-9.]+)", frames))
first = float(f.get("first_t", 0))
bad = "" if re.search(r"alive-stopped|EXIT:exited with status = 9 ", res) and "CRASH" not in res else " RUN:" + res
print("PERF run=%s ready_s=%.2f first_frame_s=%.2f frames10s=%s p50_ms=%s p95_ms=%s max_ms=%s%s" % (
    i, armed - t0 if armed else -1, first - t0 if first else -1, f.get("window10s", "-"),
    f.get("p50_ms", "-"), f.get("p95_ms", "-"), f.get("max_ms", "-"), bad))
EOF
done
"$EXE" "$W" > "$OUT/idle.out" 2> "$OUT/idle.err" &
pid=$!
sleep 15
# top's first sample has no interval behind it: keep the last 10 of 11
samples=$(top -l 11 -s 1 -pid $pid -stats cpu 2>/dev/null | awk '$1 ~ /^[0-9]+([.][0-9]+)?$/ { print $1 }' | tail -10 | tr '\n' ' ')
rss=$(ps -o rss= -p $pid 2>/dev/null | tr -d ' ')
{ kill $pid; sleep 1; kill -9 $pid; wait $pid; } 2>/dev/null
python3 - "$samples" "${rss:-0}" <<'EOF'
import sys
v = [float(x) for x in sys.argv[1].split()]
print("IDLE cpu_mean=%.1f cpu_max=%.1f samples=%d rss_mb=%.0f" % (
    sum(v) / len(v) if v else -1, max(v) if v else -1, len(v), int(sys.argv[2]) / 1024.0))
EOF
