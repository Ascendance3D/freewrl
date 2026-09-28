#!/usr/bin/env python3
"""Failure-path and pass-path tests for fixtures.py.

Focus: the result-guard rule for success markers. A success marker (X_DONE, X_OK, ...) may be
accepted only when a result guard decides whether it prints. Being inside an event handler is not
enough: a handler runs whenever its event is delivered, whatever the value, so a marker it prints
unconditionally proves only that the event arrived, not that the result was right (PR #26 Copilot
finding). These tests pin that rule and its two required paths end to end through the real check
functions:

  failure path  a fixture prints EVENT_DONE inside an event handler with no result guard  -> FAIL
  pass path     a fixture prints the marker inside an event handler only after a guard     -> PASS

Standard library only; never starts FreeWRL, never uses the network. Run directly:

    tools/macos-ci/test_fixtures.py

Prints one PASS/FAIL line per case and a RESULT line; exits 0 when every case passes, 1 otherwise.
"""
import contextlib
import importlib.util
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("fixtures", os.path.join(HERE, "fixtures.py"))
fx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fx)

passed = 0
failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("PASS %s" % name)
    else:
        failed += 1
        print("FAIL %s%s" % (name, ": " + detail if detail else ""))


# ---------------------------------------------------------------------------------------------
# unit: Script.unverified, the locus of the result-guard rule

def unverified(js, handlers, marker):
    """The reason unverified gives for the first literal holding marker in js, or None."""
    s = fx.Script(js, 1, set(handlers))
    off = next(start for v, start, _ in s.strings if marker in v)
    return s.unverified(off)


def test_unverified():
    # an event handler name alone is not proof: an unconditional marker in a handler is unverified
    r = unverified("function hit(v){ print('EVENT_DONE'); }", ["hit"], "EVENT_DONE")
    check("unit/handler-unguarded is unverified", r is not None and "event handler" in r, repr(r))
    # a result guard inside the handler is proof (if / else / switch / catch, ?:, && or ||)
    check("unit/handler if-guard is verified",
          unverified("function hit(v){ if (v == 1) print('EVENT_DONE'); }", ["hit"], "EVENT_DONE") is None)
    check("unit/handler &&-guard is verified",
          unverified("function hit(v){ (v == 1) && print('EVENT_DONE'); }", ["hit"], "EVENT_DONE") is None)
    check("unit/handler ?:-guard is verified",
          unverified("function hit(v){ print(v == 1 ? 'EVENT_DONE' : 'no'); }", ["hit"], "EVENT_DONE") is None)
    # a nested block inside the handler still needs the guard, not just the handler
    check("unit/handler nested-if is verified",
          unverified("function hit(v){ for (var i=0;i<1;i++){ if (v) print('EVENT_DONE'); } }",
                     ["hit"], "EVENT_DONE") is None)
    # unchanged behaviour: load-time and non-handler functions were never proof
    check("unit/load-time is unverified",
          unverified("print('EVENT_DONE');", [], "EVENT_DONE") == "unconditionally at load time")
    r = unverified("function initialize(){ print('EVENT_DONE'); }", ["hit"], "EVENT_DONE")
    check("unit/non-handler function is unverified", r == "unconditionally in initialize()", repr(r))


# ---------------------------------------------------------------------------------------------
# end to end: a real fixture on disk, run through check_contract as a CI script's marker grep

FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<X3D profile='Immersive' version='4.0'>
<head><meta name='description' content='Event-handler marker test. Pass: prints EVENT_DONE when the hit value is correct.'/></head>
<Scene>
<Script DEF='S'>
  <field accessType='inputOnly' type='SFInt32' name='hit'/>
  <![CDATA[ecmascript:
%s
  ]]>
</Script>
</Scene>
</X3D>
"""

# hit() is the event handler for the inputOnly 'hit' field. The unguarded body prints the marker on
# every event; the guarded body prints it only when the delivered value is the expected result.
UNGUARDED = "    function hit(v) { print('EVENT_DONE'); }"
GUARDED = "    function hit(v) { if (v == 42) print('EVENT_DONE'); }"


@contextlib.contextmanager
def fixture_file(body):
    fd, path = tempfile.mkstemp(suffix=".x3d")
    try:
        os.write(fd, (FIXTURE % body).encode("utf-8"))
        os.close(fd)
        yield path
    finally:
        os.unlink(path)


def run_contract(path):
    """Run check_contract for one CI entry that greps EVENT_DONE in `path`; return (failed?, output)."""
    entry = fx.Entry("smoke.sh", 1, "evt", path, "EVENT_DONE", None)
    fx.failed = False
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fx.check_contract([entry], [], 0)
    return fx.failed, buf.getvalue()


def test_end_to_end():
    with fixture_file(UNGUARDED) as path:
        did_fail, out = run_contract(path)
        f = fx.Fixture(path)
        wired = "hit" in f.scripts[0].handlers  # the field really is parsed as an event handler
        check("e2e/handler is recognised", wired)
        check("e2e/failure-path unguarded handler marker -> FAIL",
              did_fail and "proves only that the script ran" in out, out.strip())
    with fixture_file(GUARDED) as path:
        did_fail, out = run_contract(path)
        check("e2e/pass-path guarded handler marker -> PASS", not did_fail, out.strip())


def main():
    test_unverified()
    test_end_to_end()
    print()
    print("RESULT: %s (%d passed, %d failed)" % ("PASS" if failed == 0 else "FAIL", passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
