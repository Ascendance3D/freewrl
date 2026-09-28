# tools/macos-ci

The macOS CI harness that `.github/workflows/macos.yml` runs (each script documents itself in its
header), and a light local check to run before `git push`.

## Light local pre-push check

```sh
tools/macos-ci/prepush-light.sh
```

Run it from any directory in the repository before you push. It takes a few seconds. In the
default mode it does not start FreeWRL. It never pushes, merges, fetches or changes a remote, and
it does not install a git hook. GitHub Actions remains the final gate: this check finds common
mistakes before a CI round trip, it does not replace CI.

It first prints the repository root, the branch, the HEAD commit, the base, the number of changed
files and the working tree state. It then prints one line per check:

- `PASS <check>: ...`: the check ran and found no problem.
- `FAIL <check>: ...`: the check found a problem. One indented line per problem follows.
- `SKIP <check>: <reason>`: the check did not run. The reason tells why: a tool is missing, there
  is nothing in scope, or you did not ask for it. A skip does not fail the result.

The summary names the checks that ran and the checks that were skipped. The last line is
`RESULT: PASS` or `RESULT: FAIL`. The exit status is 0 if no check failed, 1 if a check failed,
and 2 for a usage error.

"Changed" means the files that differ between the working tree and the merge-base with
`origin/master` (else `master`; set another base with `--base REF`), plus untracked files. The
base is your local ref: run `git fetch` first for a current comparison. The checks read the
working tree, so they also see changes that you did not commit and that `git push` does not send.
The header says when the tree is dirty.

### Default checks

| Check | What it checks |
|---|---|
| `shell-syntax` | `bash -n` on every `tools/**/*.sh` script and every changed shell script (a script whose `#!` line names `sh` or `zsh` is parsed by that shell). Each script under `tools/` must have mode 100755 in git. |
| `fixture-xml` | Each changed `.x3d` regression fixture is well-formed XML (Python standard library; the DTD is not downloaded). |
| `fixture-metadata` | For each changed regression fixture: the X3D `profile` plus its `<component>` declarations include the component of every node used (for example, a `Script` needs `Immersive` or `Full`, not `Interchange`; a node that is in no X3D component of the checker's table, such as a FreeWRL extension, needs `Full`); every element is a node that FreeWRL knows; `version` agrees with the DOCTYPE; the description (`<meta name='description'>`, or the header comment of a `.wrl`) has a `Pass:` clause; every marker that the Pass clause or the fixture's `freewrl/tests/regression/README` entry names is a marker that the fixture prints; the README lists the fixture. |
| `fixture-script` | For each changed regression fixture: every `Browser.<name>` in a Script exists on the duktape `Browser` object (`jsVRMLBrowser_duk.c`); every success marker (a string such as `X_DONE`, `X_OK` or `X_PASS`) is checked by a CI script, and is printed only after a check of the result, or directly by the event handler whose event is the result. |
| `marker-contract` | For every fixture that `smoke.sh` (`run NAME WORLD MARKER`) or `suite.sh` (`texrun NAME-i WORLD` with `grep -c "MARKER"`) runs: the fixture exists; it prints the marker (or the engine source prints it, for example `Skinning Method: CPU`); it does not print that marker unconditionally at load time; if it prints a success marker, the script checks that exact marker; its Pass clause quotes the text that the script greps for. A log line that the engine prints (not the fixture) must be in the engine source instead; the Pass clause need not quote it. Every repository path that the scripts build from `$H`, `$R`, `$SRC`, `$T` or `$G` exists. This check always covers every entry, changed or not. |
| `host-c-tests` | `tools/c-tests/run-containers.sh`, the host-only C tests of the CI build job. SKIP if `clang` (or `$CC`) cannot run. |
| `doctypes` | `tools/macos-ci/doctypes.sh` on the source `FreeWRL-Info.plist`. CI runs it on the built app; give `--app path/to/FreeWRL.app` to do the same. SKIP without `plutil` (not macOS) or `python3`. |

The three `fixture-*` checks cover every regression fixture instead of only the changed ones
when you give `--all`, when a file they all read changed (the regression `README`,
`jsVRMLBrowser_duk.c`, `GeneratedCode.c` or `fixtures.py`), or when a regression fixture was
deleted or renamed. When no fixture is in scope, they report SKIP. The four fixture checks need Python 3.6 or later and report SKIP without it.

These rules catch the mistakes made in PR #25: a fixture that called `Browser.createNode` (a
member of `Browser.currentScene`, not of `Browser`); a success marker printed whether or not the
result was right; a Script under the `Interchange` profile; a Pass clause or README entry that no
longer matches the fixture; a CI script and a fixture that disagree on a marker.

### What it does not check

- It does not build or package FreeWRL, and it does not run `verify.py`, the smoke fixtures, the
  world-replacement and texture stress, or AddressSanitizer. CI does.
- It does not test C or Objective-C changes, except through the host-only container tests.
- The profile check uses components, not component levels.
- The Script checks are static. Apart from the `Browser.<name>` check, they cannot tell that a
  call fails at run time. `--runtime` runs a fixture.
- It does not run `shellcheck`, and it does not check the workflow YAML.

### Optional runtime check

```sh
tools/macos-ci/prepush-light.sh --runtime --app path/to/FreeWRL.app freewrl/tests/regression/duktape_defnames.x3d
```

`--runtime` starts FreeWRL. It first prints a warning. It runs only the 1 to 3 fixtures that you
name, one at a time, each for 25 seconds (`--seconds N`, 5 to 120), under lldb through `run.sh`.
It does not start if a FreeWRL process is already running, or if a default check failed. It
fails a fixture on a crash or allocator abort, a load, shader, GL or Script error (the `BAD`
pattern of `smoke.sh`), a missing marker (the markers the CI scripts check, else the fixture's
own success markers), or an AddressSanitizer report (use a Debug build with AddressSanitizer for
that). The logs of a failed run stay in a temporary directory that the output names. The default
mode never runs it.

### Optional git hook

The script does not install a hook. To run the default checks before every push, install it
yourself:

```sh
printf '#!/bin/sh\nexec tools/macos-ci/prepush-light.sh\n' > .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

`git push --no-verify` skips the hook for one push.
