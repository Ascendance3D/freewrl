# Security policy

## Supported versions

| Branch or release | Security fixes |
| --- | --- |
| `master` | Yes. Fixes land here first. |
| FreeWRL 6.7 line (`v6.7.0-rc.1` and later 6.7.x releases) | Yes, through a new release built from `master`. |
| `macos-arm64` (historical 2020 Mac port) | No. It is kept only for reference. |
| Older tags and pre-releases (`v6.7.0-macos-beta.*`) | No. Use the latest 6.7 release. |

This fork maintains the macOS Apple Silicon build and the Linux autotools build. Other platform
build files come from upstream FreeWRL and this fork does not maintain them.

## Report a vulnerability privately

Do not open a public issue, discussion or pull request for a vulnerability.

Use GitHub private vulnerability reporting:
<https://github.com/Ascendance3D/freewrl/security/advisories/new>

This fork has no separate security email address.

## What to include

- The FreeWRL version or commit SHA.
- The operating system and CPU architecture.
- The affected component or source file, if you know it.
- Steps to reproduce, and a minimal VRML or X3D file when it is safe to share.
- The impact you expect, for example a crash, memory corruption, or file or network access.
- Any crash log or sanitizer output.

## What happens next

A maintainer will try to acknowledge the report and assess it. This is a volunteer project, so we
cannot promise a fixed response time or fix date.

We will discuss the fix and the disclosure timing with you in the private advisory. When a fix is
released, we will publish a GitHub security advisory and credit you if you want credit.

## Coordinated disclosure

Do not publish details of an unpatched vulnerability. Please give us reasonable time to release a
fix first.

If the problem is also in the original FreeWRL code, we may share the details privately with the
upstream FreeWRL project on SourceForge so that it can fix it too.

## Accepted CodeQL Findings

GitHub CodeQL code scanning runs on `master` and on pull requests. This section records the
CodeQL security alerts that we reviewed and accepted instead of fixing in source. We dismiss each
accepted alert in GitHub with the reason and comment given here.

Source fixes come first. For example, PR #74 fixed alert #43 (`cpp/integer-multiplication-cast-to-long`
in `stbi__convert_format16`, `freex3d/src/lib/opengl/stb_image.h`) with a checked allocation. We
do not dismiss an alert that a source change can fix at low risk.

An accepted finding is not permanently ignored. Review the accepted findings again when one of these
changes:

- platform support (for example, if Windows becomes supported);
- vendored code (stb_image, SpiderMonkey, SGI libnurbs, cson);
- input trust (for example, if a local or user-supplied input becomes remote-controlled);
- build configuration (for example, if a file that is not built today enters a supported build).

If a later scan reopens an alert or reports it at a new location, review it again. Do not dismiss
it only because this table lists it.

Owner decision: Ryan (repository owner), 2026-10-03. Verified at `d315491d4` and confirmed still
valid at `add03a583` after PR #74. All alerts below are C/C++ (`/language:c-cpp`).

### A. Component_Core macro false positives

- Alerts: #69 to #88 (20 alerts).
- Rule: `cpp/use-after-free`.
- Location: `freex3d/src/lib/scenegraph/Component_Core.c`, lines 315 to 335 (the `CMD_MULTI`,
  `CMD_MSFI32` and `CMD_MSFL` field-copy macros).
- Reason: `FREE_IF_NZ` frees the pointer and sets it to `NULL`. `MALLOC` then assigns a new buffer
  before `memcpy` writes to it. No code reads the freed pointer. ROUTE copies allocate new buffers
  through `shallow_copy_field`, so the source and the target do not share a buffer.
- GitHub dismissal reason: false positive.
- Review trigger: a change to these macros, `FREE_IF_NZ`, `MALLOC` or `shallow_copy_field`.

### B. Other free-then-reassign false positives

- Alerts: #66, #67, #68, #89, #90, #91, #92, #93, #94, #95 (10 alerts).
- Rule: `cpp/use-after-free`.
- Locations: `REINITIALIZE_SORTED_NODES_FIELD` users in `Component_Grouping.c`,
  `Component_CAD.c` and `Component_Networking.c` (`compile_Inline`); KeyDevice initialization in
  `Component_KeyDevice.c`; `fwl_tmpFileLocation` in `main/MainLoop.c`.
- Reason: the code frees a pointer and then assigns a new value before any read. The
  `fwl_tmpFileLocation` caller passes a buffer that is not aliased. No code reads a freed pointer.
- GitHub dismissal reason: false positive.
- Review trigger: a change to these functions or to the macro.

### C. Float precision only

- Alerts: #45, #55, #56 (3 alerts).
- Rule: `cpp/integer-multiplication-cast-to-long`.
- Locations: `Component_HAnim.c:2551`, `Component_Text.c:4107`, `Component_Text.c:4131`.
- Reason: these are float-by-float products that the compiler promotes to double. They are not
  integer products, so they cannot wrap. No memory size comes from the result. The only effect is
  precision, not memory safety.
- GitHub dismissal reason: false positive.
- Review trigger: a change that makes these operands integers or uses the result as a size.

### D. Non-production code and tests

- Alerts: #104, #125, #126 (3 alerts).
- Rules: `cpp/use-after-free` (#104), `cpp/command-line-injection` (#125, #126).
- Locations: `tools/c-tests/test_eai_reply.c` (unit-test harness);
  `linux_appimage/linuxsolibbundler/src/Utils.cpp` (local AppImage packaging tool).
- Reason: these programs are not in a release binary. The packaging tool runs only on the
  maintainer's machine with the maintainer's own arguments.
- GitHub dismissal reason: used in tests.
- Review trigger: shipping either program, or running the packaging tool on input that is not trusted.

### E. Unsupported platform (Windows only)

- Alerts: #37, #59, #60, #61, #62, #63, #64, #65, #110, #111, #112, #124 (12 alerts).
- Rules: `cpp/redundant-null-check-simple` (#37), `cpp/wrong-type-format-argument` (#59 to #65),
  `cpp/toctou-race-condition` (#110 to #112), `cpp/unsigned-difference-expression-compared-zero`
  (#124).
- Locations: `freex3d/src/SSR/` (SSR server and its `cson` copy), `freex3d/src/libsound/libsound.cpp`,
  `freex3d/src_windows/freeWRLEAITest/`.
- Reason: only the Visual Studio projects build this code. The supported macOS and Linux builds do
  not build it.
- GitHub dismissal reason: won't fix.
- Review trigger: Windows becomes a supported platform, or a supported build starts to compile
  one of these files.

### F. Vendored code

- Alerts: #41, #42, #58, #96, #97, #98, #99, #100, #101, #102, #103 (11 alerts).
- Rules: `cpp/integer-multiplication-cast-to-long` (#41, #42), `cpp/wrong-type-format-argument`
  (#58), `cpp/use-after-free` (#96 to #103).
- Locations: `freex3d/src/lib/opengl/stb_image.h` (#41, #42); `freewrl/JS/js1.8/src/js.c` (#58,
  SpiderMonkey 1.8 shell); `freex3d/src/libnurbs/` (#96 to #103, SGI libnurbs internals).
- Reason: this is third-party code that this fork does not change. FreeWRL does not reach the
  stb_image path for #41. `stbi__mad3sizes_valid` guards #42. No build compiles the SpiderMonkey
  1.8 shell. The libnurbs alerts are in vendor internals.
- GitHub dismissal reason: won't fix.
- Review trigger: an update of the vendored library, or a new FreeWRL call path into it.

### G. Dead code

- Alerts: #46, #47 (2 alerts).
- Rule: `cpp/integer-multiplication-cast-to-long`.
- Location: `freex3d/src/lib/scenegraph/Component_Lighting.c`, lines 1057 and 1058, inside
  `if (0)` at line 1053.
- Reason: the code never executes.
- GitHub dismissal reason: won't fix.
- Review trigger: a change that enables this block.

### H. Owner-accepted low risk

- Alerts: #38, #39, #54, #113, #114, #115 (6 alerts).
- Rules: `cpp/integer-multiplication-cast-to-long` (#38, #39, #54), `cpp/toctou-race-condition`
  (#113, #114, #115).
- Locations: `freex3d/src/lib/main/Snapshot.c` (window-size snapshot math);
  `Component_Interpolation.c:176` (interpolator key-count math); `freex3d/src/lib/io_files.c`
  (local check-then-use on files that the user opens or on FreeWRL's own temporary files).
- Reason: the input is local and bounded by the window size, the scene's key count, or the local
  file system. The owner accepts the risk and tracks it as backlog risk.
- GitHub dismissal reason: won't fix.
- Review trigger: any of these inputs becomes remote-controlled.
