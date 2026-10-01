import lldb, os
PERIOD = int(os.environ.get("RELOAD_PERIOD", "0"))
PATHS = [p for p in os.environ.get("RELOAD_PATHS", "").split(":") if p]
# RELOAD_POINTER=X,Y (backing pixels from the top left of the view): drive the pointer as
# FWGLView does, through dllFreeWRL_onMouse, so the picking pass runs without a real cursor.
# In each period of RELOAD_PERIOD frames the pointer hovers near X,Y, presses the left button,
# drags, and lets go 10 frames into the next period, so each world replacement happens while
# the pointer is over (and pressing) whatever sensor is under X,Y.
POINTER = [int(v) for v in os.environ.get("RELOAD_POINTER", "").split(",") if v]
MOTION, PRESS, RELEASE = 6, 4, 5
st = {"n": 0, "loads": 0}
def mouse(frame, action, button, x, y):
    frame.EvaluateExpression('(int)dllFreeWRL_onMouse(fwctx, %d, %d, %d, %d)' % (action, button, x, y))
def pointer(frame, phase):
    x, y = POINTER
    press = PERIOD - 20
    if phase == 10:
        mouse(frame, RELEASE, 1, x + 40, y)
    elif phase == press:
        mouse(frame, PRESS, 1, x, y)
    elif phase > press and phase % 2 == 0:
        mouse(frame, MOTION, 1, x + 2 * (phase - press), y)
    elif phase < press and phase % 3 == 0:
        mouse(frame, MOTION, 0, x + phase % 7, y)
def cb(frame, bp_loc, extra_args, internal_dict):
    st["n"] += 1
    if PERIOD > 40 and len(POINTER) == 2:
        pointer(frame, st["n"] % PERIOD)
    if PERIOD and PATHS and st["n"] % PERIOD == 0:
        p = PATHS[st["loads"] % len(PATHS)]
        st["loads"] += 1
        v = frame.EvaluateExpression('(void)dllFreeWRL_onLoad(fwctx, (char*)"%s")' % p)
        err = v.GetError()
        print("RELOAD %d %s %s" % (st["loads"], os.path.basename(p), "" if err.Success() or "no value" in str(err) else err), flush=True)
    return False
def __lldb_init_module(debugger, internal_dict):
    pass
