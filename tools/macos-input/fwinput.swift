// fwinput: post real macOS input events (CGEventPost) for FreeWRL QA. Test tooling only: it is
// never built into FreeWRL.app. live-input.sh builds it into a scratch directory and drives it.
//
// Posting events needs the Accessibility (post event) permission for the process that runs the
// test (Terminal, an IDE, ...). `fwinput access` reports it and never asks for it.
//
// Coordinates are global screen points, origin at the top left of the main display, as
// CGWindowListCopyWindowInfo reports window bounds. live-input.sh converts view-relative points.
//
//   fwinput access                       ACCESS granted | ACCESS denied (exit 0 | 3)
//   fwinput screen-access                SCREEN granted | SCREEN denied (exit 0 | 3): Screen
//                                        Recording, for screencapture of window contents
//   fwinput window PID                   WINDOW x y w h of PID's largest on-screen window
//   fwinput activate PID                 bring PID's application to the front
//   fwinput frontmost                    FRONTMOST pid of the active application
//   fwinput resize PID W H               set the size of PID's first window (points), through
//                                        the Accessibility API, as a user drag of its corner does
//   fwinput key CODE down|up|tap [MODS] [repeat]   virtual key code; MODS: cmd,shift,ctrl,alt
//                                        or -; "repeat" marks a key down as an auto-repeat
//   fwinput modifier CODE down|up        a modifier key alone (a flagsChanged event)
//   fwinput move X Y | down X Y | up X Y | click X Y
//   fwinput drag X1 Y1 X2 Y2 STEPS       press at 1, move in STEPS steps, release at 2
//   fwinput scroll X Y DY                one wheel event of DY lines over X Y
//   fwinput text STRING                  type STRING (one key down/up per character)
import ApplicationServices
import AppKit
import Foundation

func fail(_ message: String, _ code: Int32 = 2) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(code)
}

let args = CommandLine.arguments
guard args.count >= 2 else { fail("usage: see the head of fwinput.swift") }
let source = CGEventSource(stateID: .hidSystemState)

func number(_ i: Int) -> Double {
    guard i < args.count, let v = Double(args[i]) else { fail("argument \(i): need a number") }
    return v
}
func post(_ event: CGEvent?) {
    guard let e = event else { fail("could not create the event") }
    e.post(tap: .cghidEventTap)
    usleep(15_000)
}
func flags(_ text: String) -> CGEventFlags {
    var f: CGEventFlags = []
    for m in text.split(separator: ",") {
        switch m {
        case "cmd": f.insert(.maskCommand)
        case "shift": f.insert(.maskShift)
        case "ctrl": f.insert(.maskControl)
        case "alt": f.insert(.maskAlternate)
        case "-": break
        default: fail("unknown modifier \(m)")
        }
    }
    return f
}
func mouse(_ type: CGEventType, _ x: Double, _ y: Double, _ button: CGMouseButton = .left) {
    post(CGEvent(mouseEventSource: source, mouseType: type, mouseCursorPosition: CGPoint(x: x, y: y),
                 mouseButton: button))
}
func key(_ code: Int, _ down: Bool, _ mods: CGEventFlags, repeating: Bool = false) {
    let e = CGEvent(keyboardEventSource: source, virtualKey: CGKeyCode(code), keyDown: down)
    e?.flags = mods
    if repeating { e?.setIntegerValueField(.keyboardEventAutorepeat, value: 1) }
    post(e)
}

switch args[1] {
case "access":
    if CGPreflightPostEventAccess() {
        print("ACCESS granted")
    } else {
        print("ACCESS denied")
        exit(3)
    }
case "screen-access":
    if CGPreflightScreenCaptureAccess() {
        print("SCREEN granted")
    } else {
        print("SCREEN denied")
        exit(3)
    }
case "window":
    let pid = Int(number(2))
    let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID)
        as? [[String: Any]] ?? []
    var best: CGRect? = nil
    for w in list where (w[kCGWindowOwnerPID as String] as? Int) == pid
        && (w[kCGWindowLayer as String] as? Int) == 0 {
        guard let b = w[kCGWindowBounds as String] as? NSDictionary,
              let r = CGRect(dictionaryRepresentation: b as CFDictionary) else { continue }
        if best == nil || r.width * r.height > best!.width * best!.height { best = r }
    }
    guard let r = best else { fail("no on-screen window for pid \(pid)", 4) }
    print("WINDOW \(Int(r.origin.x)) \(Int(r.origin.y)) \(Int(r.width)) \(Int(r.height))")
case "activate":
    guard let app = NSRunningApplication(processIdentifier: pid_t(number(2))) else { fail("no such pid", 4) }
    app.activate(options: [])
    usleep(300_000)
case "frontmost":
    print("FRONTMOST \(NSWorkspace.shared.frontmostApplication?.processIdentifier ?? -1)")
case "resize":
    let pid = pid_t(number(2))
    var size = CGSize(width: number(3), height: number(4))
    var value: CFTypeRef?
    let app = AXUIElementCreateApplication(pid)
    guard AXUIElementCopyAttributeValue(app, kAXWindowsAttribute as CFString, &value) == .success,
          let windows = value as? [AXUIElement], let win = windows.first,
          let axSize = AXValueCreate(.cgSize, &size) else { fail("no window for pid \(pid)", 4) }
    let err = AXUIElementSetAttributeValue(win, kAXSizeAttribute as CFString, axSize)
    guard err == .success else { fail("resize failed: AXError \(err.rawValue)", 4) }
    usleep(300_000)
case "key":
    guard args.count >= 4 else { fail("key CODE down|up|tap [MODS] [repeat]") }
    let code = Int(number(2))
    let mods = flags(args.count > 4 ? args[4] : "-")
    let repeating = args.count > 5 && args[5] == "repeat"
    switch args[3] {
    case "down": key(code, true, mods, repeating: repeating)
    case "up": key(code, false, mods)
    case "tap": key(code, true, mods); key(code, false, mods)
    default: fail("key: down, up or tap")
    }
case "modifier":
    let code = Int(number(2))
    let mask: CGEventFlags
    switch code {
    case 56, 60: mask = .maskShift
    case 59, 62: mask = .maskControl
    case 58, 61: mask = .maskAlternate
    case 55, 54: mask = .maskCommand
    default: fail("modifier: 54-62 only")
    }
    let down = args.count > 3 && args[3] == "down"
    let e = CGEvent(keyboardEventSource: source, virtualKey: CGKeyCode(code), keyDown: down)
    e?.type = .flagsChanged
    e?.flags = down ? mask : []
    post(e)
case "move": mouse(.mouseMoved, number(2), number(3))
case "down": mouse(.leftMouseDown, number(2), number(3))
case "up": mouse(.leftMouseUp, number(2), number(3))
case "click":
    mouse(.mouseMoved, number(2), number(3))
    mouse(.leftMouseDown, number(2), number(3))
    usleep(60_000)
    mouse(.leftMouseUp, number(2), number(3))
case "drag":
    let (x1, y1, x2, y2) = (number(2), number(3), number(4), number(5))
    let steps = max(1, Int(number(6)))
    mouse(.mouseMoved, x1, y1)
    mouse(.leftMouseDown, x1, y1)
    for i in 1...steps {
        let f = Double(i) / Double(steps)
        mouse(.leftMouseDragged, x1 + (x2 - x1) * f, y1 + (y2 - y1) * f)
        usleep(20_000)
    }
    mouse(.leftMouseUp, x2, y2)
case "scroll":
    mouse(.mouseMoved, number(2), number(3))
    post(CGEvent(scrollWheelEvent2Source: source, units: .line, wheelCount: 1,
                 wheel1: Int32(number(4)), wheel2: 0, wheel3: 0))
case "text":
    guard args.count >= 3 else { fail("text STRING") }
    for u in args[2].utf16 {
        var c = u
        for down in [true, false] {
            let e = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: down)
            e?.keyboardSetUnicodeString(stringLength: 1, unicodeString: &c)
            post(e)
        }
    }
default:
    fail("unknown command \(args[1])")
}
