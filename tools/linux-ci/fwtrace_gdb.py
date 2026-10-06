# gdb Python module for x11_input_baseline.py: the Linux twin of tools/macos-ci/reloader.py's
# call tracing. Loaded with `gdb -x fwtrace_gdb.py`. Test tooling only.
#   TRACE_CALLS=fn,...   print each call of these C functions with up to four arguments
#                        (from debug info; "?" when optimized out):  CALL fn t=epoch a0 a1 ..
#   FRAME_FN=fn          count the calls of fn as frames (the X11 frontend's fv_swapbuffers);
#                        report() prints FRAMES total=n window10s=m p50_ms= p95_ms= max_ms=
#                        first_t= for the 10 s that start 5 s after the first frame
# The breakpoints never stop the program (stop() returns False).
import os, time
import gdb

frame_times = []
reported = []


def _args(frame):
    vals = []
    try:
        block = frame.block()
        while block is not None and block.function is None:
            block = block.superblock
        for sym in block or []:
            if not sym.is_argument:
                continue
            try:
                v = sym.value(frame)
                vals.append("%g" % float(v) if v.type.strip_typedefs().code == gdb.TYPE_CODE_FLT
                            else str(int(v)))
            except (gdb.error, ValueError, TypeError):
                vals.append("?")
            if len(vals) == 4:
                break
    except (gdb.error, RuntimeError):
        # no symbol information for this frame: print the call with the arguments read so far
        return vals
    return vals


class CallBreakpoint(gdb.Breakpoint):
    def __init__(self, name):
        super().__init__(name)
        self.fname = name
        self.silent = True

    def stop(self):
        print("CALL %s t=%.3f %s" % (self.fname, time.time(), " ".join(_args(gdb.newest_frame()))),
              flush=True)
        return False


class FrameBreakpoint(gdb.Breakpoint):
    def __init__(self, name):
        super().__init__(name)
        self.silent = True

    def stop(self):
        frame_times.append(time.time())
        return False


def report():
    """once: on program exit, or from `-ex "python report()"` after a stop"""
    if reported:
        return
    reported.append(1)
    t = frame_times
    if len(t) < 2:
        print("FRAMES total=%d window10s=0" % len(t), flush=True)
        return
    lo, hi = t[0] + 5.0, t[0] + 15.0
    w = [x for x in t if lo <= x < hi]
    gaps = sorted((b - a) * 1000.0 for a, b in zip(w, w[1:]))
    pick = lambda q: gaps[min(len(gaps) - 1, int(q * len(gaps)))] if gaps else -1.0
    print("FRAMES total=%d window10s=%d%s p50_ms=%.1f p95_ms=%.1f max_ms=%.1f first_t=%.3f" % (
        len(t), len(w), "" if t[-1] >= hi else "(short-run)", pick(0.5), pick(0.95),
        gaps[-1] if gaps else -1.0, t[0]), flush=True)


gdb.execute("set pagination off")
gdb.execute("set confirm off")
gdb.execute("set print thread-events off")
gdb.execute("set breakpoint pending on")
gdb.execute("handle SIGPIPE nostop noprint pass")
gdb.execute("handle SIGUSR1 SIGUSR2 nostop noprint pass")
for fn in [f for f in os.environ.get("TRACE_CALLS", "").split(",") if f]:
    CallBreakpoint(fn)
if os.environ.get("FRAME_FN"):
    FrameBreakpoint(os.environ["FRAME_FN"])
gdb.events.exited.connect(lambda event: report())
