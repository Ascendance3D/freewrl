import lldb, os, time
# lldb Python module for run.sh: world replacement, pointer events and sensor-handler tracing
# from a breakpoint on fw_frontend_frame_hook (libFreeWRL; the frontend calls it once per frame,
# before it draws). It is a C symbol, so nothing here depends on a frontend's method names.
#   RELOAD_PERIOD=N          every N frames load the next RELOAD_PATHS world through
#   RELOAD_PATHS=a:b:c       dllFreeWRL_onLoad, which is what File > Open does
#   RELOAD_POINTER=X,Y       (with RELOAD_PERIOD) drive the pointer as FWGLView does, through
#                            dllFreeWRL_onMouse (backing pixels from the top left of the view),
#                            so the picking pass runs without a real cursor. In each period
#                            the pointer hovers near X,Y, presses the left button, drags, and
#                            lets go 10 frames into the next period, so each world replacement
#                            happens while the pointer is over (and pressing) whatever sensor
#                            is under X,Y
#   TRACE_SENSOR=do_X        count the calls of that sensor handler (do_SphereSensor, ...) by
#                            event: hover, press, drag, release, leave (run.sh sets its breakpoint)
#   FRAME_STATS=1            time each frame hook hit; report() prints the frame count and cadence
#   TRACE_CALLS=fn[:f],...   (run.sh sets the breakpoints) print each call of these C functions
#                            with its first four arguments: from debug info when the dSYM is
#                            found, else from registers (":f": the first argument is a float)
# Prints, into the lldb log run.sh reads:
#   RELOADER armed ...       first frame with fwctx: the settings, the fwctx address, the time
#   RELOAD n world OK|FAIL: error
#   POINTER events=n failed=m   every period
#   TRACE handler calls=n hover=.. press=.. drag=.. release=.. leave=..   at the end (report)
#   CALL fn t=epoch a0 a1 a2 a3     each traced call; t is the Unix time in seconds
#   FRAMES total=n window10s=m ...  at the end (report), with FRAME_STATS: frames in the 10 s
#                            that start 5 s after the first frame, and the frame interval
#                            median, 95th percentile and maximum in that window, in ms, and
#                            first_t, the Unix time of the first frame
# The app's context pointer is read from the global fwctx through the symbol table, and the
# calls are made with casts, so this works on a packaged Release app without its dSYM (the
# expression `fwctx` alone needs debug info, and failed silently before).
PERIOD = int(os.environ.get("RELOAD_PERIOD", "0"))
PATHS = [p for p in os.environ.get("RELOAD_PATHS", "").split(":") if p]
POINTER = [int(v) for v in os.environ.get("RELOAD_POINTER", "").split(",") if v]
TRACE = os.environ.get("TRACE_SENSOR", "")
FRAME_STATS = bool(os.environ.get("FRAME_STATS"))
FLOAT_CALLS = {c[:-2] for c in os.environ.get("TRACE_CALLS", "").split(",") if c.endswith(":f")}
frame_times = []
MOTION, PRESS, RELEASE, MAPNOTIFY = 6, 4, 5, 19
st = {"n": 0, "loads": 0, "mouse": 0, "mouse_fail": 0, "stopped": 0, "fwctx": None, "fwctx_err": ""}
STOPPED = "stopped"
tr = {"calls": 0, "hover": 0, "press": 0, "drag": 0, "release": 0, "leave": 0}

def fwctx(frame):
    """the app's libFreeWRL context: the pointer held by the global fwctx (FWGLView.m), read
    through the symbol table; None until the GL view has created it"""
    if st["fwctx"] is None:
        process = frame.GetThread().GetProcess()
        target = process.GetTarget()
        err = lldb.SBError()
        sym = None
        for m in target.module_iter():
            s = m.FindSymbol("fwctx")
            if s.IsValid():
                sym = s
                break
        if sym is None:
            st["fwctx_err"] = "no symbol fwctx"
            return None
        v = process.ReadPointerFromMemory(sym.GetStartAddress().GetLoadAddress(target), err)
        if not err.Success():
            st["fwctx_err"] = str(err)
            return None
        if not v:
            st["fwctx_err"] = "fwctx is NULL"
            return None
        st["fwctx"] = v
    return st["fwctx"]

def call(frame, expr):
    """evaluate a void call; True on success, STOPPED when run.sh's watchdog ended the run
    (SIGSTOP) while the call ran (the run's end, not a fault), else lldb's error text"""
    v = frame.EvaluateExpression("((void)%s, (int)1)" % expr)
    e = v.GetError()
    if e.Success() and v.GetValueAsSigned() == 1:
        return True
    err = (str(e).strip() or "no value").replace("\n", " ")
    if "interrupted" in err and "SIGSTOP" in err:
        st["stopped"] += 1
        return STOPPED
    return err

def mouse(frame, ctx, action, button, x, y):
    r = call(frame, "dllFreeWRL_onMouse((void*)0x%x, %d, %d, %d, %d)" % (ctx, action, button, x, y))
    if r is True:
        st["mouse"] += 1
    elif r != STOPPED:
        st["mouse_fail"] += 1
        if st["mouse_fail"] <= 3:
            print("POINTER FAIL: %s" % r, flush=True)

def pointer(frame, ctx, phase):
    x, y = POINTER
    press = PERIOD - 20
    if phase == 10:
        mouse(frame, ctx, RELEASE, 1, x + 40, y)
    elif phase == press:
        mouse(frame, ctx, PRESS, 1, x, y)
    elif phase > press and phase % 2 == 0:
        mouse(frame, ctx, MOTION, 1, x + 2 * (phase - press), y)
    elif phase < press and phase % 3 == 0:
        mouse(frame, ctx, MOTION, 0, x + phase % 7, y)

def cb(frame, bp_loc, extra_args, internal_dict):
    st["n"] += 1
    if not frame_times:
        st["first_frame"] = time.time()
    if FRAME_STATS or not frame_times:
        frame_times.append(time.monotonic())
    ctx = fwctx(frame)
    if ctx is None:
        if st["n"] == 1:
            print("RELOADER waiting for fwctx: %s" % st["fwctx_err"], flush=True)
        return False
    if not st.get("armed"):
        st["armed"] = True
        print("RELOADER armed: period=%d paths=%d pointer=%s trace=%s fwctx=0x%x t=%.3f" % (
            PERIOD, len(PATHS), ",".join(str(v) for v in POINTER) or "-", TRACE or "-", ctx,
            time.time()), flush=True)
    if PERIOD > 40 and len(POINTER) == 2:
        pointer(frame, ctx, st["n"] % PERIOD)
    if PERIOD and st["n"] % PERIOD == 0:
        if PATHS:
            p = PATHS[st["loads"] % len(PATHS)]
            st["loads"] += 1
            r = call(frame, 'dllFreeWRL_onLoad((void*)0x%x, (char*)"%s")' % (ctx, p))
            print("RELOAD %d %s %s" % (st["loads"], os.path.basename(p),
                "OK" if r is True else "STOPPED (run ended)" if r == STOPPED else "FAIL: " + r), flush=True)
        print("POINTER events=%d failed=%d stopped=%d" % (st["mouse"], st["mouse_fail"], st["stopped"]), flush=True)
    return False

def trace(frame, bp_loc, extra_args, internal_dict):
    """do_*Sensor(void *ptr, int ev, int but1, int over): arguments in x1..x3 at entry (arm64)"""
    reg = lambda n: frame.FindRegister(n).GetValueAsUnsigned() & 0xffffffff
    ev, but1, over = reg("x1"), reg("x2"), reg("x3")
    tr["calls"] += 1
    if ev == PRESS:
        tr["press"] += 1
    elif ev == RELEASE:
        tr["release"] += 1
    elif ev == MOTION and but1:
        tr["drag"] += 1
    elif ev == MAPNOTIFY and over:
        tr["hover"] += 1
    elif ev == MAPNOTIFY:
        tr["leave"] += 1
    return False

def _int32(v):
    v &= 0xffffffff
    return v - (1 << 32) if v & 0x80000000 else v

def _debug_args(frame):
    """the first four arguments from debug info (dSYM), or None; right at inlined call sites too"""
    out = []
    vs = frame.GetVariables(True, False, False, True)
    for i in range(min(4, vs.GetSize())):
        v = vs.GetValueAtIndex(i)
        if v.GetType().GetCanonicalType().GetBasicType() in (lldb.eBasicTypeFloat, lldb.eBasicTypeDouble):
            s = v.GetValue()
            if s is None:
                return None
            out.append("%g" % float(s))
        else:
            err = lldb.SBError()
            n = v.GetValueAsSigned(err)
            if not err.Success():
                return None
            out.append(str(n))
    return out or None

def calls(frame, bp_loc, extra_args, internal_dict):
    """a TRACE_CALLS function at entry. run.sh names each breakpoint after its function, since
    an optimized build inlines some (the stop is then in a frame of the caller or an inlined
    callee). The arguments come from that function's frame through debug info, else from
    x0..x3 (s0 for a ":f" float) as the arm64 calling convention passes them."""
    names = lldb.SBStringList()
    bp_loc.GetBreakpoint().GetNames(names)
    name = names.GetStringAtIndex(0) if names.GetSize() else (frame.GetFunctionName() or "?").split("(")[0]
    thread, args = frame.GetThread(), None
    for i in range(min(8, thread.GetNumFrames())):
        f = thread.GetFrameAtIndex(i)
        if (f.GetFunctionName() or "").split("(")[0] == name:
            args = _debug_args(f)
            break
        if not f.IsInlined():
            break
    if args is None and name in FLOAT_CALLS:
        args = ["%g" % frame.FindRegister("s0").GetData().GetFloat(lldb.SBError(), 0)]
    elif args is None:
        args = [str(_int32(frame.FindRegister("x%d" % i).GetValueAsUnsigned())) for i in range(4)]
    print("CALL %s t=%.3f %s" % (name, time.time(), " ".join(args)), flush=True)
    return False

def frame_report():
    t = frame_times
    if len(t) < 2:
        print("FRAMES total=%d window10s=0" % st["n"], flush=True)
        return
    lo, hi = t[0] + 5.0, t[0] + 15.0
    w = [x for x in t if lo <= x < hi]
    gaps = sorted((b - a) * 1000.0 for a, b in zip(w, w[1:]))
    pick = lambda q: gaps[min(len(gaps) - 1, int(q * len(gaps)))] if gaps else -1.0
    complete = t[-1] >= hi
    print("FRAMES total=%d window10s=%d%s p50_ms=%.1f p95_ms=%.1f max_ms=%.1f first_t=%.3f" % (
        st["n"], len(w), "" if complete else "(short-run)", pick(0.5), pick(0.95),
        gaps[-1] if gaps else -1.0, st.get("first_frame", 0.0)), flush=True)

def report():
    if FRAME_STATS:
        frame_report()
    if TRACE:
        print("TRACE %s calls=%d hover=%d press=%d drag=%d release=%d leave=%d" % (
            TRACE, tr["calls"], tr["hover"], tr["press"], tr["drag"], tr["release"], tr["leave"]), flush=True)

def __lldb_init_module(debugger, internal_dict):
    pass
