#!/usr/bin/env python3
"""Native Linux X11 smoke and real-input baseline for FreeWRL (SDL3 migration QA). Test tooling
only: Xvfb, xdotool and gdb are test dependencies, never FreeWRL runtime dependencies.

Usage: x11-input-baseline.sh BUILD OUTDIR [--sessions main,quit-q]
  BUILD   an Autotools build directory (freex3d/ after ./configure --with-target=x11 && make):
          it runs BUILD/src/bin/freewrl through BUILD/libtool, under gdb

Each session starts its own Xvfb server (no window manager), runs FreeWRL under gdb with
fwtrace_gdb.py tracing libFreeWRL functions, and posts real X input through XTEST (xdotool).
The trace points are libFreeWRL functions, so a later SDL frontend can be measured the same way.
Pointer positions are window pixels: with no window manager the X window is the GL drawable.

Each case prints one line:  X11 <case> <STATUS> <detail>
  PASS                 the engine got what the input contract says
  KNOWN_NATIVE_DEFECT  the X11 frontend does something else; recorded, not fixed here
  FAIL_HARNESS         the test could not run or observe the case
then X11INPUT harness=PASS|FAIL_HARNESS ... Exit 0 unless the harness failed (1); exit 2 when a
test program is missing.
"""
import ctypes, ctypes.util, os, re, shutil, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "freewrl", "tests")

KEYPRESS, KEYDOWN, KEYUP, ACTION = 1, 2, 3, 10
F1_KEY, UP_KEY, DOWN_KEY, LEFT_KEY, RIGHT_KEY = 1, 17, 18, 19, 20
ALT_KEY, CTL_KEY, SFT_KEY = 30, 31, 32
PRESS, RELEASE, MOTION = 4, 5, 6
VIEWER_EXAMINE, VIEWER_WALK = 1, 2
TRACED = ("fwl_do_keyPress0,fwl_handle_mouse,fwl_setScreenDim1,fwl_set_viewer_type,"
          "fwl_toggle_headlight,fwl_Next_ViewPoint,fwl_doQuit,handle")
results = []


def say(line):
    print(line, flush=True)


def record(case, status, detail):
    results.append((case, status))
    say("X11 %s %s %s" % (case, status, detail))


def run(*cmd, env=None, check=False):
    return subprocess.run(list(cmd), capture_output=True, text=True, env=env, check=check)


class Session:
    def __init__(self, build, out, name, world, env):
        self.name, self.env, self.prefix = name, env, os.path.join(out, name)
        self.log = open(self.prefix + ".gdb.log", "w")
        self.t_launch = time.time()
        cmd = [os.path.join(build, "libtool"), "--mode=execute", "gdb", "-q", "-batch",
               "-x", os.path.join(HERE, "fwtrace_gdb.py"),
               "-ex", "run > %s.out 2> %s.err" % (self.prefix, self.prefix),
               "-ex", "python report()", "-ex", "kill",
               "--args", os.path.join(build, "src", "bin", "freewrl"), world]
        self.proc = subprocess.Popen(cmd, stdout=self.log, stderr=subprocess.STDOUT, env=env,
                                     start_new_session=True)
        self.wid = None

    def text(self, suffix=".gdb.log"):
        try:
            with open(self.prefix + suffix, errors="replace") as f:
                return f.read()
        except OSError:
            return ""

    def calls(self):
        out = []
        for line in self.text().splitlines():
            m = re.match(r"CALL (\S+) t=([0-9.]+) ?(.*)$", line)
            if m:
                out.append((m.group(1), float(m.group(2)), [int(a) if re.match(r"^-?\d+$", a) else a
                                                             for a in m.group(3).split()]))
        return out

    def between(self, t0, t1):
        return [c for c in self.calls() if t0 <= c[1] <= t1]

    def last(self, name):
        c = [x for x in self.calls() if x[0] == name]
        return c[-1][2] if c else None

    def pid(self):
        r = run("pgrep", "-n", "-x", "freewrl|lt-freewrl")
        return int(r.stdout.split()[0]) if r.stdout.split() else None

    def find_window(self):
        """the FreeWRL top-level window: the largest viewable child of the root window (the X11
        frontend sets no window name, and this Xvfb server shows nothing else)"""
        best = None
        for line in run("xwininfo", "-root", "-children", env=self.env).stdout.splitlines():
            m = re.match(r"\s+(0x[0-9a-f]+) .*?(\d+)x(\d+)\+-?\d+\+-?\d+", line)
            if not m:
                continue
            if "IsViewable" not in run("xwininfo", "-id", m.group(1), env=self.env).stdout:
                continue
            area = int(m.group(2)) * int(m.group(3))
            if best is None or area > best[0]:
                best = (area, m.group(1), int(m.group(2)), int(m.group(3)))
        return best

    def size(self):
        w = self.find_window()
        return (w[2], w[3]) if w else (0, 0)

    def wait_ready(self, timeout=60):
        end = time.time() + timeout
        while time.time() < end:
            if self.proc.poll() is not None:
                return False
            w = self.find_window()
            if w:
                self.wid = str(int(w[1], 16))
                time.sleep(4)  # let the world load
                return True
            time.sleep(0.5)
        return False

    def xdo(self, *args):
        return run("xdotool", *[str(a) for a in args], env=self.env)

    def stop(self):
        """SIGINT stops the program in gdb; gdb then prints the frame report and kills it"""
        p = self.pid()
        if self.proc.poll() is None and p:
            os.kill(p, signal.SIGINT)
        try:
            self.proc.wait(timeout=60)
        except subprocess.TimeoutExpired:
            os.killpg(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
        self.log.close()

    def gone_within(self, seconds):
        end = time.time() + seconds
        while time.time() < end:
            if self.proc.poll() is not None or "exited" in self.text() or "exited normally" in self.text():
                return True
            if "[Inferior 1 (process" in self.text():
                return True
            time.sleep(0.25)
        return False


def step(sess, action, settle=0.8):
    t0 = time.time()
    action()
    time.sleep(settle)
    return sess.between(t0 - 0.05, time.time())


def keys(c):
    return [tuple(a[:2]) for n, _, a in c if n == "fwl_do_keyPress0"]


def mice(c):
    return [tuple(a[:4]) for n, _, a in c if n == "fwl_handle_mouse"]


def named(c, name):
    return [a for n, _, a in c if n == name]


def send_wm_delete(display, wid):
    """what a window manager's close button sends: a WM_PROTOCOLS / WM_DELETE_WINDOW message"""
    x = ctypes.cdll.LoadLibrary(ctypes.util.find_library("X11"))
    x.XOpenDisplay.restype = ctypes.c_void_p
    x.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x.XInternAtom.restype = ctypes.c_ulong
    x.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]

    class XClientMessageEvent(ctypes.Structure):
        _fields_ = [("type", ctypes.c_int), ("serial", ctypes.c_ulong), ("send_event", ctypes.c_int),
                    ("display", ctypes.c_void_p), ("window", ctypes.c_ulong),
                    ("message_type", ctypes.c_ulong), ("format", ctypes.c_int), ("l", ctypes.c_long * 5)]

    class XEvent(ctypes.Union):
        _fields_ = [("xclient", XClientMessageEvent), ("pad", ctypes.c_long * 24)]

    x.XSendEvent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_long,
                             ctypes.POINTER(XEvent)]
    d = x.XOpenDisplay(display.encode())
    if not d:
        return False
    ev = XEvent()
    ev.xclient.type = 33  # ClientMessage
    ev.xclient.window = int(wid)
    ev.xclient.message_type = x.XInternAtom(d, b"WM_PROTOCOLS", 0)
    ev.xclient.format = 32
    ev.xclient.l[0] = x.XInternAtom(d, b"WM_DELETE_WINDOW", 0)
    ok = x.XSendEvent(d, int(wid), 0, 0, ctypes.byref(ev)) != 0
    x.XFlush(d)
    x.XCloseDisplay(d)
    return ok


def window_stddev(env, wid, path):
    """colour standard deviation of the window image, 0..1 (0 = one flat colour)"""
    # the root window: GLX output is not in the FreeWRL window's own backing store under Xvfb
    geo = run("xdotool", "getwindowgeometry", str(wid), env=env).stdout
    m = re.search(r"Position: (-?\d+),(-?\d+).*?Geometry: (\d+)x(\d+)", geo, re.S)
    if not m:
        return -1.0
    x, y, w, h = m.groups()
    r = run("import", "-window", "root", "-crop", "%sx%s+%s+%s" % (w, h, x, y), path, env=env)
    if r.returncode != 0:
        return -1.0
    r = run("convert", path, "-format", "%[fx:standard_deviation]", "info:")
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


def start_xvfb():
    r, w = os.pipe()
    xvfb = subprocess.Popen(["Xvfb", "-displayfd", str(w), "-screen", "0", "1280x1024x24", "-nolisten", "tcp"],
                            pass_fds=(w,), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.close(w)
    num = b""
    while not num.endswith(b"\n"):
        ch = os.read(r, 1)
        if not ch:
            break
        num += ch
    os.close(r)
    return xvfb, ":" + num.decode().strip()


def main_session(build, out):
    xvfb, display = start_xvfb()
    env = dict(os.environ, DISPLAY=display, TRACE_CALLS=TRACED, FRAME_FN="fv_swapbuffers",
               FREEWRL_GL_IDENTITY="1")
    s = Session(build, out, "main", os.path.join(TESTS, "1.wrl"), env)
    try:
        if not s.wait_ready():
            record("launch", "FAIL_HARNESS", "no FreeWRL window or no fwl_setScreenDim1 call")
            return
        name = run("xdotool", "getwindowname", s.wid, env=env).stdout.strip()
        record("launch", "PASS", "window %s on Xvfb %s, window name %s" % (
            s.wid, display, repr(name) if name else "none (the X11 frontend sets no title)"))
        pid = s.pid()
        maps = ""
        if pid:
            with open("/proc/%d/maps" % pid) as f:
                maps = f.read()
        glx = "libGLX" in maps or "libGL.so" in maps
        record("native-x11-glx", "PASS" if glx else "FAIL_HARNESS",
               "process maps %s; no SDL library: %s" % ("libGLX/libGL" if glx else "no GLX library",
                                                         "libSDL" not in maps))
        ident = [l for l in s.text(".err").splitlines() if l.startswith("GL_IDENTITY")]
        say(ident[0] if ident else "GL_IDENTITY (none)")
        w, h = s.size()
        sd = window_stddev(env, s.wid, os.path.join(out, "render.png"))
        if sd > 0.02:
            record("render", "PASS", "window %sx%s px, image standard deviation %.3f" % (w, h, sd))
        elif sd < 0:
            record("render", "FAIL_HARNESS", "screen capture failed (ImageMagick import)")
        else:
            # control: a plain GLX program on the same server shows whether capture works here
            gears = subprocess.Popen(["glxgears"], env=env, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL) if shutil.which("glxgears") else None
            control = -1.0
            if gears:
                time.sleep(3)
                r = run("xwininfo", "-root", "-children", env=env).stdout
                g = [l.split()[0] for l in r.splitlines() if "glxgears" in l]
                control = window_stddev(env, int(g[0], 16), os.path.join(out, "glxgears.png")) if g else -1.0
                gears.terminate()
            if control > 0.02:
                record("render", "KNOWN_NATIVE_DEFECT",
                       "FreeWRL presents frames (fv_swapbuffers runs) but its %sx%s px window stays "
                       "one flat colour (deviation %.3f), even the Background clear colour; glxgears "
                       "on the same Xvfb renders (deviation %.3f), so capture works" % (w, h, sd, control))
            else:
                record("render", "FAIL_HARNESS", "flat FreeWRL window (%.3f) and no working glxgears "
                       "control (%.3f): cannot tell FreeWRL from the capture" % (sd, control))
        err = s.text(".err") + s.text(".out")
        bad = re.findall(r"failed to load.*|Script error.*", err)
        record("world-load", "FAIL_HARNESS" if bad else "PASS",
               "1.wrl: %s" % (bad[0] if bad else "no load or script error in the log"))
        cx, cy = w // 2, h // 2
        s.xdo("mousemove", "--window", s.wid, cx, cy)
        time.sleep(0.5)
        c = step(s, lambda: s.xdo("mousemove", "--window", s.wid, 100, 100))
        m = mice(c)
        moved = [e for e in m if e[0] == MOTION and e[2:] == (100, 100)]
        record("pointer-move", "PASS" if moved else "FAIL_HARNESS",
               "window (100,100) px -> engine %s" % m[-1:])
        c = step(s, lambda: (s.xdo("mousemove", "--window", s.wid, cx, cy), s.xdo("click", 1)))
        m = mice(c)
        ok = any(e[0] == PRESS and e[1] == 1 for e in m) and any(e[0] == RELEASE and e[1] == 1 for e in m)
        record("pointer-click", "PASS" if ok else "FAIL_HARNESS", "events %s" % m)

        def drag():
            s.xdo("mousedown", 1)
            for i in range(1, 9):
                s.xdo("mousemove", "--window", s.wid, cx + 10 * i, cy)
                time.sleep(0.03)
            s.xdo("mouseup", 1)
        c = step(s, drag, 1.0)
        m = mice(c)
        drags = [e for e in m if e[0] == MOTION]
        ok = any(e[0] == PRESS for e in m) and len(drags) >= 3 and any(e[0] == RELEASE for e in m)
        record("pointer-drag", "PASS" if ok else "FAIL_HARNESS",
               "press, %d motions, release; motion button field %s (the engine keeps the pressed "
               "button from ButtonPress)" % (len(drags), sorted({e[1] for e in drags})))

        # the button field of hover motion (no button down) should be 0
        hover = [e for e in mice(s.calls()) if e[0] == MOTION]
        odd = sorted({e[1] for e in hover if e[1] not in (0, 1, 2, 3)})
        record("pointer-motion-button", "PASS" if not odd else "KNOWN_NATIVE_DEFECT",
               "button field of %d motion events: %s" % (len(hover), "all 0..3" if not odd else
               "%s: fwCommonX11.c reads event.xbutton.button from a MotionNotify, where XMotionEvent "
               "has is_hint and padding" % odd))

        def printable(case, k, effect, want=None):
            c = step(s, lambda: s.xdo("key", k))
            kk = keys(c)
            types = sorted({t for _, t in kk})
            eff = named(c, effect)
            ok = types == [KEYPRESS, KEYDOWN, KEYUP] and eff and (want is None or any(e[:1] == [want] for e in eff))
            record(case, "PASS" if ok else "FAIL_HARNESS", "engine keys %s, %s %s" % (kk, effect, eff or "not called"))

        printable("key-e", "e", "fwl_set_viewer_type", VIEWER_EXAMINE)
        printable("key-w", "w", "fwl_set_viewer_type", VIEWER_WALK)
        printable("key-h", "h", "fwl_toggle_headlight")
        printable("key-v", "v", "fwl_Next_ViewPoint")
        printable("key-e-restore", "e", "fwl_set_viewer_type", VIEWER_EXAMINE)
        # KEYPRESS timing: the character should arrive on key down, as KEYDOWN does. The key is
        # held 0.4 s, under the X server's auto-repeat delay (660 ms on Xvfb), whose synthetic
        # KeyRelease would otherwise look like a KEYPRESS during the hold
        t0 = time.time()
        s.xdo("keydown", "k")
        time.sleep(0.4)
        t_rel = time.time()
        s.xdo("keyup", "k")
        time.sleep(0.8)
        c = s.between(t0 - 0.05, time.time())
        kp = [(n, t, a) for n, t, a in c if n == "fwl_do_keyPress0"]
        press = [t for _, t, a in kp if a[1] == KEYPRESS]
        down = [t for _, t, a in kp if a[1] == KEYDOWN]
        if press and down and press[0] < t_rel:
            record("key-keypress-timing", "PASS", "KEYPRESS %.2f s after key down, before the release" % (press[0] - t0))
        elif press and down:
            record("key-keypress-timing", "KNOWN_NATIVE_DEFECT",
                   "KEYDOWN %.2f s after key down, but KEYPRESS only %.2f s after it, on the release "
                   "(fwCommonX11.c handle_Xevents sends KEYPRESS on KeyRelease)" % (down[0] - t0, press[0] - t0))
        else:
            record("key-keypress-timing", "FAIL_HARNESS", "engine keys %s" % [tuple(a[:2]) for _, _, a in kp])
        for name, k, code in (("arrow-left", "Left", LEFT_KEY), ("arrow-right", "Right", RIGHT_KEY),
                              ("arrow-up", "Up", UP_KEY), ("arrow-down", "Down", DOWN_KEY), ("f1", "F1", F1_KEY),
                              ("modifier-shift", "Shift_L", SFT_KEY), ("modifier-ctrl", "Control_L", CTL_KEY),
                              ("modifier-alt", "Alt_L", ALT_KEY)):
            c = step(s, lambda: s.xdo("key", k))
            kk = keys(c)
            ok = (code, KEYDOWN + ACTION) in kk and (code, KEYUP + ACTION) in kk
            record("key-" + name, "PASS" if ok else "KNOWN_NATIVE_DEFECT", "engine keys %s" % kk)
        for k in ("space", "Return"):
            step(s, lambda: s.xdo("key", k))  # leave the ':' command line closed
        # wheel: X11 sends buttons 4/5 as ButtonPress/ButtonRelease; the engine zooms on
        # MotionNotify with button 4/5 (MainLoop.c netweheel), seen here as handle() calls
        c = step(s, lambda: s.xdo("click", "--repeat", 3, "--delay", 100, 5), 1.2)
        m = [e for e in mice(c) if e[1] in (4, 5)]
        zoom = [a for a in named(c, "handle") if len(a) > 1 and a[1] in (4, 5)]
        if zoom:
            record("wheel", "PASS", "frontend events %s, viewer handle() wheel calls %d" % (m, len(zoom)))
        elif m:
            record("wheel", "KNOWN_NATIVE_DEFECT",
                   "frontend sends %s (ButtonPress/ButtonRelease with button 4/5); the engine's "
                   "wheel path takes MotionNotify with button 4/5, so handle() never gets it" % m)
        else:
            record("wheel", "FAIL_HARNESS", "no wheel event reached fwl_handle_mouse")
        # resize, as a window manager would do it
        c = step(s, lambda: s.xdo("windowsize", s.wid, 800, 600), 1.5)
        dims = named(c, "fwl_setScreenDim1")
        record("resize", "PASS" if any(d[:2] == [800, 600] for d in dims) else "FAIL_HARNESS",
               "fwl_setScreenDim1 %s" % (dims[-1][:2] if dims else "not called"))
        # window manager close button
        t0 = time.time()
        sent = send_wm_delete(display, s.wid)
        gone = s.gone_within(10)
        c = s.between(t0 - 0.05, time.time())
        record("wm-close", "PASS" if sent and gone and named(c, "fwl_doQuit") else "FAIL_HARNESS",
               "WM_DELETE_WINDOW sent: %s; fwl_doQuit %s; process %s" % (
                   sent, "called" if named(c, "fwl_doQuit") else "not called", "exited" if gone else "running"))
    finally:
        s.stop()
        xvfb.terminate()
    frames = re.findall(r"^FRAMES .*$", s.text(), re.M)
    first = re.search(r"first_t=([0-9.]+)", frames[-1]) if frames else None
    say("PERF startup first_frame_s=%.2f (launch through libtool/gdb) %s" % (
        float(first.group(1)) - s.t_launch if first else -1, frames[-1] if frames else "FRAMES none"))


def quit_session(build, out):
    xvfb, display = start_xvfb()
    env = dict(os.environ, DISPLAY=display, TRACE_CALLS="fwl_do_keyPress0,fwl_doQuit")
    s = Session(build, out, "quit-q", os.path.join(TESTS, "1.wrl"), env)
    try:
        if not s.wait_ready():
            record("q-quit", "FAIL_HARNESS", "not ready")
            return
        s.xdo("mousemove", "--window", s.wid, 50, 50)
        time.sleep(0.4)
        t0 = time.time()
        s.xdo("key", "q")
        gone = s.gone_within(10)
        c = s.between(t0 - 0.05, time.time())
        record("q-quit", "PASS" if gone and named(c, "fwl_doQuit") else "FAIL_HARNESS",
               "engine keys %s; fwl_doQuit %s; process %s" % (
                   keys(c), "called" if named(c, "fwl_doQuit") else "not called", "exited" if gone else "running"))
    finally:
        s.stop()
        xvfb.terminate()


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    build, out = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    sessions = ["main", "quit-q"]
    if "--sessions" in argv:
        sessions = argv[argv.index("--sessions") + 1].split(",")
    missing = [p for p in ("Xvfb", "xdotool", "gdb", "import", "convert") if not shutil.which(p)]
    if missing:
        say("DEPENDENCY missing test program(s): %s. Install them for this test only (Ubuntu: "
            "sudo apt install xvfb xdotool gdb imagemagick); they are not FreeWRL runtime "
            "dependencies." % " ".join(missing))
        return 2
    if not os.access(os.path.join(build, "libtool"), os.X_OK) or not os.path.exists(os.path.join(build, "src", "bin", "freewrl")):
        say("X11INPUT harness=FAIL_HARNESS %s is not a built Autotools tree (libtool, src/bin/freewrl)" % build)
        return 1
    os.makedirs(out, exist_ok=True)
    try:
        if "main" in sessions:
            main_session(build, out)
        if "quit-q" in sessions:
            quit_session(build, out)
    except Exception as e:
        record("harness", "FAIL_HARNESS", "%s: %s" % (type(e).__name__, e))
    n = {k: sum(1 for _, s in results if s == k) for k in ("PASS", "KNOWN_NATIVE_DEFECT", "FAIL_HARNESS")}
    say("X11INPUT harness=%s pass=%d known-native-defects=%d fail-harness=%d" % (
        "FAIL_HARNESS" if n["FAIL_HARNESS"] else "PASS", n["PASS"], n["KNOWN_NATIVE_DEFECT"], n["FAIL_HARNESS"]))
    return 1 if n["FAIL_HARNESS"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
