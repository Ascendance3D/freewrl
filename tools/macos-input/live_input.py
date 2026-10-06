#!/usr/bin/env python3
"""Native macOS real-input baseline for FreeWRL (SDL3 migration QA). Test tooling only.

Usage: live-input.sh APP OUTDIR [--require-access] [--sessions main,quit-q,quit-cmdq,stringsensor]

It starts FreeWRL under lldb with tools/macos-ci/run.sh (one instance at a time), posts real
events with fwinput (CGEventPost), and reads what the engine received from the CALL lines of the
traced C functions (TRACE_CALLS, tools/macos-ci/reloader.py). The trace points are libFreeWRL
functions, not Cocoa methods, so the same test can measure a later SDL frontend.

Pointer positions are points relative to the FreeWRL view (origin at its top left). The view
rectangle on screen comes from the window bounds and the engine's drawable size: the view fills
the window width and sits on the window's bottom edge, so nothing depends on the height of the
URL strip above it (it goes away with the SDL frontend).

Each case prints one line:  LIVE <case> <STATUS> <detail>
  PASS                 the engine got what the input contract (FWKeyEvents.h, libFreeWRL) says
  KNOWN_NATIVE_DEFECT  the native frontend does something else; recorded, not fixed here
  SKIP_PERMISSION      a macOS permission (Screen Recording) is missing for this check
  FAIL_HARNESS         the test itself could not run or observe the case
The last line is LIVEINPUT harness=PASS|FAIL_HARNESS ... Exit 0 unless the harness failed
(1), or with --require-access when posting events is not allowed (3). Without Accessibility
(post event) access it prints SKIP_ACCESSIBILITY_PERMISSION and exits 0, so a hosted CI runner
does not fail only for that.
"""
import os, re, struct, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RUN = os.path.join(ROOT, "tools", "macos-ci", "run.sh")
TESTS = os.path.join(ROOT, "freewrl", "tests")

# libFreeWRL values (libFreeWRL.h, ui/common.h, X11 event numbers the engine uses)
KEYPRESS, KEYDOWN, KEYUP = 1, 2, 3
ACTION = 10  # an action key arrives as KEYDOWN/KEYUP + 10
F1_KEY, UP_KEY, DOWN_KEY, LEFT_KEY, RIGHT_KEY = 1, 17, 18, 19, 20
ALT_KEY, CTL_KEY, SFT_KEY = 30, 31, 32
PRESS, RELEASE, MOTION = 4, 5, 6
VIEWER_EXAMINE, VIEWER_WALK = 1, 2
# macOS virtual key codes (US layout)
VK = {"a": 0, "b": 11, "e": 14, "h": 4, "k": 40, "n": 45, "q": 12, "v": 9, "w": 13,
      "space": 49, "return": 36, "backspace": 51, "left": 123, "right": 124, "down": 125,
      "up": 126, "f1": 122, "shift": 56, "ctrl": 59, "alt": 58, "cmd": 55}
TRACED = ("fwl_do_keyPress0,fwl_handle_mouse,fwl_setScreenDim1,fwl_setDensityFactor:f,"
          "fwl_set_viewer_type,fwl_toggle_headlight,fwl_Next_ViewPoint,fwl_doQuit,fwl_clearWorld,"
          "fwl_commandline,handleButtonRelease,fwl_setShift,showConsoleText,sendKeyToKeySensor")
HUD_BUTTONS = 21  # the bottom menu bar (statusbarHud.c mainbar_linux): WALK first, OPTIONS last

results = []


def say(line):
    print(line, flush=True)


def record(case, status, detail):
    results.append((case, status))
    say("LIVE %s %s %s" % (case, status, detail))


class Tool:
    def __init__(self, path):
        self.path = path

    def __call__(self, *args, check=True):
        r = subprocess.run([self.path] + [str(a) for a in args], capture_output=True, text=True)
        if check and r.returncode != 0:
            raise RuntimeError("fwinput %s: %s" % (" ".join(map(str, args)), r.stderr.strip()))
        return r


class Session:
    """one FreeWRL under run.sh/lldb, with the traced calls read from its lldb log"""

    def __init__(self, app, out, name, world, seconds, tool):
        self.name, self.tool, self.prefix = name, tool, os.path.join(out, name)
        self.exe = os.path.realpath(os.path.join(app, "Contents", "MacOS", "FreeWRL"))
        env = dict(os.environ, TRACE_CALLS=TRACED)
        for k in ("RELOAD_PERIOD", "RELOAD_PATHS", "RELOAD_POINTER", "TRACE_SENSOR", "FRAME_STATS"):
            env.pop(k, None)
        self.proc = subprocess.Popen([RUN, app, world, str(seconds), self.prefix], env=env,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.pid = None
        self.result = ""

    def calls(self):
        out = []
        if not os.path.exists(self.prefix + ".lldb.log"):
            return out  # run.sh has not started lldb yet: no calls so far
        with open(self.prefix + ".lldb.log", errors="replace") as f:
            for line in f:
                m = re.match(r"CALL (\S+) t=([0-9.]+) ?(.*)$", line.rstrip("\n"))
                if m:
                    args = [float(a) if "." in a or "e" in a else int(a) for a in m.group(3).split()]
                    out.append((m.group(1), float(m.group(2)), args))
        return out

    def between(self, t0, t1, name=None):
        return [c for c in self.calls() if t0 <= c[1] <= t1 and (name is None or c[0] == name)]

    def last(self, name):
        c = [x for x in self.calls() if x[0] == name]
        return c[-1][2] if c else None

    def wait_ready(self, timeout=60):
        """the window is on screen and the engine has its drawable size and density"""
        end = time.time() + timeout
        while time.time() < end:
            if self.pid is None:
                r = subprocess.run(["pgrep", "-f", "^" + self.exe], capture_output=True, text=True)
                if r.stdout.split():
                    self.pid = int(r.stdout.split()[0])
            if self.pid and self.last("fwl_setScreenDim1") and self.last("fwl_setDensityFactor"):
                w = self.tool("window", self.pid, check=False)
                if w.returncode == 0:
                    time.sleep(4)  # let the world finish loading
                    return True
            if self.proc.poll() is not None:
                return False
            time.sleep(0.5)
        return False

    def geometry(self):
        """view rectangle in screen points, the density, and the drawable size in pixels"""
        x, y, w, h = map(int, self.tool("window", self.pid).stdout.split()[1:5])
        bw, bh = self.last("fwl_setScreenDim1")[:2]
        d = float(self.last("fwl_setDensityFactor")[0])
        vw, vh = bw / d, bh / d
        return {"wx": x, "wy": y, "ww": w, "wh": h, "bw": bw, "bh": bh, "d": d, "vw": vw, "vh": vh,
                "ox": x, "oy": y + h - vh}

    def stop(self):
        """end the run as run.sh's watchdog does (SIGSTOP), then wait for its result line"""
        if self.proc.poll() is None:
            subprocess.run(["pkill", "-STOP", "-f", "^" + self.exe])
        try:
            out, _ = self.proc.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            subprocess.run(["pkill", "-KILL", "-f", "^" + self.exe])
            out, _ = self.proc.communicate()
        self.result = (out or "").strip().splitlines()[-1] if (out or "").strip() else ""
        return self.result

    def exited_within(self, seconds):
        end = time.time() + seconds
        while time.time() < end:
            r = subprocess.run(["pgrep", "-f", "^" + self.exe], capture_output=True, text=True)
            if not r.stdout.strip():
                return True
            time.sleep(0.25)
        return False


class Driver:
    """posts events at view-relative points (points, origin top left of the FreeWRL view)"""

    def __init__(self, tool, g):
        self.tool, self.g = tool, g

    def at(self, vx, vy):
        return self.g["ox"] + vx, self.g["oy"] + vy

    def move(self, vx, vy):
        self.tool("move", *self.at(vx, vy))

    def click(self, vx, vy):
        self.tool("click", *self.at(vx, vy))

    def drag(self, vx1, vy1, vx2, vy2, steps=8):
        self.tool("drag", *(self.at(vx1, vy1) + self.at(vx2, vy2)), steps)

    def scroll(self, vx, vy, dy):
        self.tool("scroll", *(self.at(vx, vy) + (dy,)))

    def focus(self, pid):
        """FreeWRL must be the active application for key events; a click on the title bar
        reaches no FreeWRL handler. Returns False when it was not (logged)."""
        front = self.tool("frontmost").stdout.split()[-1]
        if front == str(pid):
            return True
        say("FOCUS FreeWRL was not frontmost (pid %s was); clicking its title bar" % front)
        self.tool("click", self.g["wx"] + self.g["ww"] / 2.0, self.g["wy"] + 8)
        time.sleep(0.6)
        if self.tool("frontmost").stdout.split()[-1] != str(pid):
            self.tool("activate", pid)
            time.sleep(0.6)
        return False

    def view_focus(self, pid):
        """make the FreeWRL view the key target: a click in the scene, as a user does. At launch
        the URL field above the view holds the keyboard focus (launch-key-focus case)."""
        self.focus(pid)
        self.click(self.g["vw"] / 2.0, self.g["vh"] / 2.0)
        time.sleep(0.5)

    def key(self, name, action="tap", mods="-", repeat=False):
        self.tool("key", VK[name], action, mods, *(["repeat"] if repeat else []))

    def modifier(self, name, action):
        self.tool("modifier", VK[name], action)

    def capture(self, path, vx, vy, w, h):
        x, y = self.at(vx, vy)
        r = subprocess.run(["screencapture", "-x", "-t", "bmp", "-R",
                            "%d,%d,%d,%d" % (round(x), round(y), round(w), round(h)), path],
                           capture_output=True)
        return r.returncode == 0 and os.path.exists(path)


FOCUS = []  # the Driver and pid of the running main session, for step()


def step(sess, action, settle=0.8):
    """run action, wait for the app to take it; returns the calls the engine got meanwhile"""
    if FOCUS:
        FOCUS[0].focus(FOCUS[1])
    t0 = time.time()
    action()
    time.sleep(settle)
    return sess.between(t0 - 0.05, time.time())


def keys(calls):
    return [tuple(c[2][:2]) for c in calls if c[0] == "fwl_do_keyPress0"]


def mice(calls):
    return [tuple(c[2][:4]) for c in calls if c[0] == "fwl_handle_mouse"]


def named(calls, name):
    return [c[2] for c in calls if c[0] == name]


def bmp_pixels(path):
    """(width, height, rows of (r, g, b)) of an uncompressed 24/32-bit BMP (screencapture -t bmp)"""
    with open(path, "rb") as f:
        data = f.read()
    off, = struct.unpack_from("<I", data, 10)
    w, h, _, bpp, comp = struct.unpack_from("<iiHHI", data, 18)
    if bpp not in (24, 32) or comp not in (0, 3):
        raise ValueError("BMP %d bpp compression %d" % (bpp, comp))
    step_ = bpp // 8
    stride = (w * step_ + 3) & ~3
    rows = []
    for r in range(abs(h)):
        base = off + r * stride
        rows.append([(data[base + i * step_ + 2], data[base + i * step_ + 1], data[base + i * step_])
                     for i in range(w)])
    if h > 0:
        rows.reverse()
    return w, abs(h), rows


def band_diff(a, b):
    """mean absolute channel difference of two equal-size captures, 0..255"""
    wa, ha, ra = bmp_pixels(a)
    wb, hb, rb = bmp_pixels(b)
    w, h = min(wa, wb), min(ha, hb)
    tot = 0
    for y in range(h):
        for x in range(w):
            pa, pb = ra[y][x], rb[y][x]
            tot += abs(pa[0] - pb[0]) + abs(pa[1] - pb[1]) + abs(pa[2] - pb[2])
    return tot / float(3 * w * h) if w and h else -1.0


def hud_layout(g):
    """bottom menu bar button size in pixels and rows, as statusbarHud.c updateSBHRows/update_density"""
    d, w, n = g["d"], g["bw"], HUD_BUTTONS
    nominal = int(d * 32)
    if w >= nominal * n:
        return nominal, 1
    if w // n >= (nominal * 3) // 4:
        return w // n, 1
    return min(nominal, w // ((n + 1) // 2)), 2


def button_point(g, index, bz, rows):
    """view point (points) of the centre of menu bar button index, first row at the bottom"""
    rowlen = (HUD_BUTTONS + 1) // rows if rows > 1 else HUD_BUTTONS
    row, col = index // rowlen, index % rowlen
    px, py_up = col * bz + bz / 2.0, row * bz + bz / 2.0
    return px / g["d"], g["vh"] - py_up / g["d"]


def near(a, b, tol):
    return abs(a - b) <= tol


def main_session(app, out, tool, seconds, screen_ok):
    world = os.path.join(TESTS, "1.wrl")
    s = Session(app, out, "main", world, seconds, tool)
    if not s.wait_ready():
        record("main-launch", "FAIL_HARNESS", "no window or no fwl_setScreenDim1/fwl_setDensityFactor call (%s)" % s.stop())
        return
    g = s.geometry()
    drv = Driver(tool, g)
    # Retina: the drawable is in backing pixels, the view in points
    say("GEOMETRY window=%d,%d %dx%d pt view=%gx%g pt drawable=%dx%d px density=%g" % (
        g["wx"], g["wy"], g["ww"], g["wh"], g["vw"], g["vh"], g["bw"], g["bh"], g["d"]))
    ok = near(g["vw"], g["ww"], 1.0) and g["vh"] <= g["wh"]
    record("retina-geometry", "PASS" if ok else "FAIL_HARNESS",
           "logical view %gx%g pt, backing %dx%d px, density %g, window %dx%d pt" % (
               g["vw"], g["vh"], g["bw"], g["bh"], g["d"], g["ww"], g["wh"]))
    # activate through the title bar: a click there reaches no FreeWRL handler
    tool("click", g["wx"] + g["ww"] / 2.0, g["wy"] + 8)
    time.sleep(0.6)
    cx, cy = g["vw"] / 2.0, g["vh"] / 2.0
    FOCUS[:] = [drv, s.pid]
    # keyboard focus at launch, before any click in the view
    c = step(s, lambda: drv.key("k"))
    k = keys(c)
    record("launch-key-focus", "PASS" if (ord("k"), KEYPRESS) in k else "KNOWN_NATIVE_DEFECT",
           "a key typed right after launch: engine keys %s%s" % (
               k, "" if k else " (the URL field below the title bar holds the keyboard focus "
               "until the view is clicked; that strip goes away with the SDL frontend)"))
    step(s, lambda: drv.move(cx, cy), 0.5)  # enter the view first: the pointer comes from the title bar

    # pointer: move, click, drag, and the point-to-pixel conversion
    c = step(s, lambda: drv.move(100, 100))
    hit = [m for m in mice(c) if m[0] == MOTION and near(m[2], 100 * g["d"], 2) and near(m[3], 100 * g["d"], 2)]
    record("pointer-move", "PASS" if hit else "FAIL_HARNESS",
           "view (100,100) pt -> engine %s (expected %g,%g px)" % (mice(c)[-1:] or "none", 100 * g["d"], 100 * g["d"]))
    record("retina-pointer", "PASS" if hit else "FAIL_HARNESS",
           "pointer x,y scale by density %g into drawable pixels, origin top left" % g["d"])
    c = step(s, lambda: drv.click(cx, cy))
    m = mice(c)
    ok = any(e[0] == PRESS and e[1] == 1 for e in m) and any(e[0] == RELEASE and e[1] == 1 for e in m)
    record("pointer-click", "PASS" if ok else "FAIL_HARNESS", "events %s" % m)
    c = step(s, lambda: drv.drag(cx, cy, cx + 80, cy, 8), 1.0)
    m = mice(c)
    drags = [e for e in m if e[0] == MOTION and e[1] == 1]
    ok = any(e[0] == PRESS for e in m) and len(drags) >= 3 and any(e[0] == RELEASE for e in m)
    record("pointer-drag", "PASS" if ok else "FAIL_HARNESS",
           "press, %d button-1 motions, release; x %s -> %s px" % (len(drags), drags[0][2] if drags else "-", drags[-1][2] if drags else "-"))

    # bottom HUD (statusbarHud.c). Default: status bar and menu bar both pinned (common.c), so the
    # icon row shows without hover. A release on the menu bar off every button unpins the menu
    # bar; then the non-hover state is the status bar alone, hovering the bar shows the icon row
    # over it, and leaving hides the row again. The default window is exactly 21 buttons wide, so
    # the test widens it first (a real window resize) to reach an empty part of the menu bar.
    caps = os.path.join(out, "hud")
    os.makedirs(caps, exist_ok=True)

    def layout():
        bz, rows = hud_layout(g)
        sb = 16 * max(1, int(g["d"] + 0.5))  # status bar height, pixels
        return bz, rows, sb, (sb + bz * rows) / g["d"]

    def shot(name, band_h):
        path = os.path.join(caps, name + ".bmp")
        return path if screen_ok and drv.capture(path, 0, g["vh"] - band_h, g["vw"], band_h) else None

    def hit(case, index, fn, want, y_up_px, bz, rows, restore):
        bx = button_point(g, index, bz, rows)[0]
        by = g["vh"] - y_up_px / g["d"]
        step(s, lambda: drv.move(bx, by), 0.4)
        c = step(s, lambda: drv.click(bx, by), 1.0)
        rel, eff = named(c, "handleButtonRelease"), named(c, fn)
        ok = rel and any(e[:len(want)] == want for e in eff)
        record(case, "PASS" if ok else "FAIL_HARNESS",
               "button %d at view (%g,%g) pt: handleButtonRelease %s, %s %s" % (
                   index, bx, by, rel[-1:] or "none", fn, eff[-1:] or "none"))
        if restore:  # SHIFT and OPTIONS are toggles
            step(s, lambda: drv.click(bx, by), 0.8)

    bz, rows, sb, band_h = layout()
    say("HUD button=%d px rows=%d statusbar=%d px band=%g pt" % (bz, rows, sb, band_h))
    step(s, lambda: drv.move(cx, cy), 1.0)
    pinned = shot("default-pinned", band_h)
    hit("hud-pinned-hit-left", 0, "fwl_set_viewer_type", [VIEWER_WALK], sb + bz / 2.0, bz, rows, False)
    step(s, lambda: drv.move(cx, cy), 0.6)

    # resize: wider by 64 pt, through the window system
    old_bw = g["bw"]
    t0 = time.time()
    tool("resize", s.pid, g["ww"] + 64, g["wh"])
    time.sleep(1.5)
    dims = [a for a in named(s.between(t0, time.time()), "fwl_setScreenDim1")]
    g.update(s.geometry())
    drv.g = g
    cx, cy = g["vw"] / 2.0, g["vh"] / 2.0
    ok = g["bw"] == old_bw + int(64 * g["d"]) and bool(dims)
    record("resize", "PASS" if ok else "FAIL_HARNESS",
           "window %dx%d pt; drawable %d -> %d px wide (fwl_setScreenDim1 %s)" % (
               g["ww"], g["wh"], old_bw, g["bw"], dims[-1][:2] if dims else "not called"))
    bz, rows, sb, band_h = layout()
    empty_x = (HUD_BUTTONS * bz + (g["bw"] - HUD_BUTTONS * bz) / 2.0) / g["d"]
    if g["bw"] - HUD_BUTTONS * bz < bz / 2:
        record("hud-unpin", "FAIL_HARNESS", "no empty menu bar area after the resize")
        say("RESULT main: %s" % s.stop())
        return
    ey = g["vh"] - (sb + bz / 2.0) / g["d"]
    step(s, lambda: drv.move(empty_x, ey), 0.4)
    c = step(s, lambda: drv.click(empty_x, ey), 1.0)
    rel = named(c, "handleButtonRelease")
    record("hud-unpin", "PASS" if rel else "FAIL_HARNESS",
           "release on the empty menu bar at view (%g,%g) pt: handleButtonRelease %s (toggles the menu bar pin)" % (
               empty_x, ey, rel[-1:] or "not called"))
    step(s, lambda: drv.move(cx, cy), 0.3)
    step(s, lambda: drv.move(cx + 2, cy + 2), 1.2)
    away1 = shot("collapsed-1", band_h)
    step(s, lambda: drv.move(cx, g["vh"] - 4), 0.3)
    step(s, lambda: drv.move(cx + 2, g["vh"] - 4), 1.2)
    hover = shot("expanded", band_h)
    # hovered, the icon row sits on the bottom edge (the status bar is hidden under it)
    targets = (("left", 0, "fwl_set_viewer_type", [VIEWER_WALK], False),
               ("center", HUD_BUTTONS // 2, "fwl_setShift", [1], True),
               ("right", HUD_BUTTONS - 1, "showConsoleText", [0], True))
    for label, index, fn, want, restore in targets:
        hit("hud-hit-%s" % label, index, fn, want, bz / 2.0, bz, rows, restore)
    step(s, lambda: drv.move(cx, cy), 0.3)
    step(s, lambda: drv.move(cx + 3, cy + 3), 1.2)
    away2 = shot("collapsed-2", band_h)
    cases = ("hud-default-pinned", "hud-collapsed", "hud-hover-expanded", "hud-leave-collapsed")
    if not screen_ok:
        for case in cases:
            record(case, "SKIP_PERMISSION", "Screen Recording not granted: no band capture")
    elif not (pinned and away1 and hover and away2):
        for case in cases:
            record(case, "FAIL_HARNESS", "screencapture failed")
    else:
        d_pin = band_diff(pinned, away1)
        d_hover = band_diff(away1, hover)
        d_back = band_diff(away1, away2)
        say("HUD band change (0..255): pinned->unpinned %.2f, unpinned->hover %.2f, unpinned->after-leave %.2f"
            % (d_pin, d_hover, d_back))
        record("hud-default-pinned", "PASS" if d_pin > 3.0 else "FAIL_HARNESS",
               "default launch shows the icon row without hover (menu bar pinned); unpinning changes the band %.2f" % d_pin)
        record("hud-collapsed", "PASS" if d_pin > 3.0 else "FAIL_HARNESS",
               "unpinned, pointer in the scene: status bar only (%s)" % away1)
        record("hud-hover-expanded", "PASS" if d_hover > 3.0 else "FAIL_HARNESS",
               "hover on the status bar shows the icon row: band change %.2f (%s)" % (d_hover, hover))
        record("hud-leave-collapsed", "PASS" if d_back < d_hover / 3.0 else "FAIL_HARNESS",
               "pointer back in the scene: band returns to the collapsed image, change %.2f" % d_back)

    # keys; a printable key: KEYDOWN and KEYPRESS on key down, KEYUP on key up (FWKeyEvents.h)
    def printable(case, name, ch, effect=None, want=None):
        c = step(s, lambda: drv.key(name))
        k = keys(c)
        ok = (ch, KEYDOWN) in k and (ch, KEYPRESS) in k and (ch, KEYUP) in k
        detail = "engine keys %s" % k
        if effect:
            eff = named(c, effect)
            ok = ok and bool(eff) and (want is None or any(e[:1] == [want] for e in eff))
            detail += ", %s %s" % (effect, eff or "not called")
        record(case, "PASS" if ok else "FAIL_HARNESS", detail)

    printable("key-e", "e", ord("e"), "fwl_set_viewer_type", VIEWER_EXAMINE)
    printable("key-w", "w", ord("w"), "fwl_set_viewer_type", VIEWER_WALK)
    printable("key-h", "h", ord("h"), "fwl_toggle_headlight")
    printable("key-h-restore", "h", ord("h"), "fwl_toggle_headlight")
    printable("key-v", "v", ord("v"), "fwl_Next_ViewPoint")
    printable("key-e-restore", "e", ord("e"), "fwl_set_viewer_type", VIEWER_EXAMINE)
    # Space opens the ':' command line; Backspace edits it; Return runs it
    c = step(s, lambda: drv.key("space"))
    k = keys(c)
    record("key-space", "PASS" if (32, KEYPRESS) in k else "FAIL_HARNESS", "engine keys %s" % k)
    c = step(s, lambda: drv.key("backspace"))
    k = keys(c)
    if (8, KEYPRESS) in k:
        record("key-backspace", "PASS", "engine keys %s ('\\b', the command line deletes)" % k)
    elif any(t == KEYPRESS for _, t in k):
        record("key-backspace", "KNOWN_NATIVE_DEFECT",
               "engine keys %s: Backspace arrives as %s, not '\\b' (8), so the ':' command line "
               "does not delete (MainLoop.c fwl_do_keyPress0 keywait)" % (k, [x for x, t in k if t == KEYPRESS]))
    else:
        record("key-backspace", "FAIL_HARNESS", "engine keys %s" % k)
    c = step(s, lambda: drv.key("return"))
    k = keys(c)
    ok = (13, KEYPRESS) in k and named(c, "fwl_commandline")
    record("key-return", "PASS" if ok else "FAIL_HARNESS",
           "engine keys %s, fwl_commandline %s" % (k, "called" if named(c, "fwl_commandline") else "not called"))
    # action keys: arrows and F1 should arrive as UP_KEY.. / F1_KEY with KEYDOWN+10 / KEYUP+10
    for name, code in (("left", LEFT_KEY), ("right", RIGHT_KEY), ("up", UP_KEY), ("down", DOWN_KEY), ("f1", F1_KEY)):
        c = step(s, lambda: drv.key(name))
        k = keys(c)
        case = "key-arrow-%s" % name if name != "f1" else "key-f1"
        if (code, KEYDOWN + ACTION) in k and (code, KEYUP + ACTION) in k:
            record(case, "PASS", "engine keys %s" % k)
        elif k:
            record(case, "KNOWN_NATIVE_DEFECT",
                   "engine keys %s, expected (%d,%d) and (%d,%d): FWGLView sends (char) of the Cocoa "
                   "function-key character" % (k, code, KEYDOWN + ACTION, code, KEYUP + ACTION))
        else:
            record(case, "KNOWN_NATIVE_DEFECT", "no key reached the engine")
    # modifiers alone: SHIFT/CTRL/ALT should arrive as SFT_KEY/CTL_KEY/ALT_KEY (FreeWRL keeps
    # SHIFT/CTRL state from them); Command has no X3D action key
    for name, code in (("shift", SFT_KEY), ("ctrl", CTL_KEY), ("alt", ALT_KEY), ("cmd", None)):
        c = step(s, lambda: (drv.modifier(name, "down"), time.sleep(0.2), drv.modifier(name, "up")))
        k = keys(c)
        case = "key-modifier-%s" % name
        if code is None:
            record(case, "PASS" if not k else "KNOWN_NATIVE_DEFECT", "engine keys %s (none expected)" % k)
        elif (code, KEYDOWN + ACTION) in k and (code, KEYUP + ACTION) in k:
            record(case, "PASS", "engine keys %s" % k)
        else:
            record(case, "KNOWN_NATIVE_DEFECT",
                   "engine keys %s, expected (%d,%d) and (%d,%d): FWGLView has no flagsChanged: "
                   "handler" % (k, code, KEYDOWN + ACTION, code, KEYUP + ACTION))
    # held key: one key down, three auto-repeat key downs, then the release
    ch = ord("k")
    drv.focus(s.pid)
    t0 = time.time()
    drv.key("k", "down")
    for _ in range(3):
        time.sleep(0.15)
        drv.key("k", "down", repeat=True)
    time.sleep(0.5)
    t_rel = time.time()
    drv.key("k", "up")
    time.sleep(0.8)
    c = s.between(t0 - 0.05, time.time())
    k = [(x, t, when) for (fn, when, a) in c if fn == "fwl_do_keyPress0" for x, t in [tuple(a[:2])]]
    downs = [x for x in k if x[0] == ch and x[1] == KEYDOWN]
    ups = [x for x in k if x[0] == ch and x[1] == KEYUP]
    rel_ok = len(ups) == 1 and ups[0][2] >= t_rel - 0.05
    record("key-held-release", "PASS" if rel_ok else "FAIL_HARNESS",
           "KEYUP %d time(s), %.2f s after the first key down, after the release" % (len(ups), (ups[0][2] - t0) if ups else -1))
    record("key-repeat", "PASS" if len(downs) == 1 else "KNOWN_NATIVE_DEFECT",
           "%d KEYDOWN and %d KEYPRESS for 1 press + 3 auto-repeats (held-key state wants 1 KEYDOWN; "
           "dllFreeWRL_onKey drops only Win32-style repeats, bit 30)" % (
               len(downs), len([x for x in k if x[0] == ch and x[1] == KEYPRESS])))
    # wheel: the engine takes wheel as buttons 4/5 (X11), or nothing reaches it
    c = step(s, lambda: drv.scroll(cx, cy, -3), 1.0)
    w = [m for m in mice(c) if m[1] in (4, 5)]
    record("wheel", "PASS" if w else "KNOWN_NATIVE_DEFECT",
           "wheel events in engine: %s%s" % (w or "none", "" if w else " (FWGLView has no scrollWheel: handler)"))
    # Command+N: a menu chord: KEYDOWN only, no KEYPRESS (so 'n' does not clear the world)
    c = step(s, lambda: drv.key("n", "tap", "cmd"), 1.0)
    k = keys(c)
    cleared = named(c, "fwl_clearWorld")
    ok = (ord("n"), KEYPRESS) not in k and not cleared and s.proc.poll() is None
    record("key-cmd-n", "PASS" if ok else "FAIL_HARNESS",
           "engine keys %s, fwl_clearWorld %s, app %s" % (k, "called" if cleared else "not called",
                                                          "running" if s.proc.poll() is None else "gone"))
    FOCUS[:] = []
    say("RESULT main: %s" % s.stop())


def quit_session(app, out, tool, case, keyspec):
    s = Session(app, out, case, os.path.join(TESTS, "1.wrl"), 60, tool)
    if not s.wait_ready():
        record(case, "FAIL_HARNESS", "not ready (%s)" % s.stop())
        return
    drv = Driver(tool, s.geometry())
    drv.view_focus(s.pid)
    t0 = time.time()
    tool("key", VK[keyspec[0]], "tap", keyspec[1])
    gone = s.exited_within(10)
    calls = s.between(t0 - 0.05, time.time())
    res = s.stop()
    quit_calls = named(calls, "fwl_doQuit")
    record(case, "PASS" if gone else "FAIL_HARNESS",
           "app %s; fwl_doQuit %s; engine keys %s; run.sh: %s" % (
               "exited" if gone else "still running", "called" if quit_calls else "not called",
               keys(calls), res))


def stringsensor_session(app, out, tool):
    world = os.path.join(TESTS, "JohnCarlson", "stringSensor.x3dv")
    s = Session(app, out, "stringsensor", world, 60, tool)
    if not s.wait_ready():
        record("stringsensor", "FAIL_HARNESS", "not ready (%s)" % s.stop())
        return
    drv = Driver(tool, s.geometry())
    drv.view_focus(s.pid)
    t0 = time.time()
    for name in ("a", "b", "return"):
        tool("key", VK[name], "tap")
        time.sleep(0.4)
    time.sleep(0.6)
    c = s.between(t0 - 0.05, time.time())
    got = [tuple(a[:2]) for a in named(c, "sendKeyToKeySensor")]
    want = [(97, KEYPRESS), (98, KEYPRESS), (13, KEYPRESS)]
    ok = all(w in got for w in want)
    record("stringsensor", "PASS" if ok else "FAIL_HARNESS",
           "sendKeyToKeySensor got %s (wants KEYPRESS for a, b, Return)" % got)
    say("RESULT stringsensor: %s" % s.stop())


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    app, out = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    opts = argv[2:]
    require = "--require-access" in opts
    sessions = ["main", "quit-q", "quit-cmdq", "stringsensor"]
    if "--sessions" in opts:
        sessions = opts[opts.index("--sessions") + 1].split(",")
    seconds = 150
    os.makedirs(out, exist_ok=True)
    tool_path = os.path.join(out, "fwinput")
    r = subprocess.run(["swiftc", "-O", os.path.join(HERE, "fwinput.swift"), "-o", tool_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        say("LIVEINPUT harness=FAIL_HARNESS fwinput did not build: %s" % r.stderr.strip()[-400:])
        return 1
    tool = Tool(tool_path)
    if tool("access", check=False).returncode != 0:
        say("SKIP_ACCESSIBILITY_PERMISSION: this process may not post events (System Settings > "
            "Privacy & Security > Accessibility). No case ran.")
        say("LIVEINPUT harness=SKIP access=denied")
        return 3 if require else 0
    screen_ok = tool("screen-access", check=False).returncode == 0
    say("LIVEINPUT access=granted screen-recording=%s app=%s" % ("granted" if screen_ok else "denied", app))
    if subprocess.run(["pgrep", "-x", "FreeWRL"], capture_output=True).returncode == 0:
        say("LIVEINPUT harness=FAIL_HARNESS another FreeWRL is running; run one at a time")
        return 1
    try:
        if "main" in sessions:
            main_session(app, out, tool, seconds, screen_ok)
        if "quit-q" in sessions:
            quit_session(app, out, tool, "quit-q", ("q", "-"))
        if "quit-cmdq" in sessions:
            quit_session(app, out, tool, "quit-cmd-q", ("q", "cmd"))
        if "stringsensor" in sessions:
            stringsensor_session(app, out, tool)
    except Exception as e:  # a harness fault, not a FreeWRL result
        record("harness", "FAIL_HARNESS", "%s: %s" % (type(e).__name__, e))
        subprocess.run(["pkill", "-KILL", "-x", "FreeWRL"])
    n = {k: sum(1 for _, s in results if s == k) for k in ("PASS", "KNOWN_NATIVE_DEFECT", "SKIP_PERMISSION", "FAIL_HARNESS")}
    harness = "FAIL_HARNESS" if n["FAIL_HARNESS"] else "PASS"
    say("LIVEINPUT harness=%s pass=%d known-native-defects=%d skip-permission=%d fail-harness=%d" % (
        harness, n["PASS"], n["KNOWN_NATIVE_DEFECT"], n["SKIP_PERMISSION"], n["FAIL_HARNESS"]))
    return 1 if n["FAIL_HARNESS"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
