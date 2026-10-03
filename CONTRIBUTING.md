# Contributing to the Ascendance Open Worlds FreeWRL fork

Thank you for helping. This repository is a modernization fork of FreeWRL. It is not the official
FreeWRL project; see the [fork notice](README.md#fork-notice).

## Scope

This fork maintains these targets on `master`:

- macOS 14 Sonoma and newer on Apple Silicon (arm64), built with Xcode.
- Linux, built with autotools (`freex3d/`).

The Android, iOS and Windows build files come from upstream FreeWRL. This fork does not build,
test or maintain them. Much of the engine code is conditional on platform defines, so do not
remove or break the code paths for other platforms.

Problems in FreeWRL itself can also go to the
[upstream FreeWRL project](https://sourceforge.net/projects/freewrl/).

## Branches and pull requests

1. `master` is the single canonical maintained trunk. Base all new work on the current `master`.
2. Create a short task branch from `master`, for example `feature-<topic>` or `fix-<topic>`.
3. Open a pull request against `master`. All changes go through a pull request.
4. After the pull request merges, delete the task branch.
5. Relevant fixes to FreeWRL itself are welcome upstream too, on the SourceForge project.

The `macos-arm64` branch is a historical reference. Do not base new work on it.

## Keep changes focused

- Make one logical change per pull request.
- Do not mix formatting changes, refactoring and behavior changes in one pull request.
- Write commit messages that say what changed and why.
- Do not commit build outputs, packaged apps, archives, `xcuserdata` or other local IDE state.
- Never commit secrets: no tokens, passwords, signing certificates, private keys or
  notarization credentials.

## Generated source

Node structs, field tables and dispatch tables are generated. Do not edit these files by hand:

- `freex3d/src/lib/scenegraph/GeneratedCode.c`
- `freex3d/src/lib/vrml_parser/Structs.h`
- `freex3d/src/lib/vrml_parser/NodeFields.h`
- `freex3d/src/libeai/GeneratedCode.c`

Edit `freex3d/codegen/*.pm` instead, then regenerate:

```sh
cd freex3d/codegen
perl VRMLC.pm
```

Commit the `.pm` change and the regenerated files together.

When you add a `.c` file, add it to `freex3d/src/lib/Makefile.sources` (Linux) and to
`OSX_gui/FreeWRL-Desktop/FreeWRL.xcodeproj` (macOS).

## Build and test

There is no unit test suite for the engine. Test by building and loading worlds.

- macOS: follow [Build instructions](README.md#macos-apple-silicon) in the README. Before you push,
  run the light local checks: `tools/macos-ci/prepush-light.sh` (see
  [`tools/macos-ci/README.md`](tools/macos-ci/README.md)).
- Linux: build with autotools as the README describes, and load sample worlds from
  `freewrl/tests/`.
- New OpenGL code must work on an OpenGL 4.1 core profile context. See
  [`MACOS-STATUS.md`](MACOS-STATUS.md).

In the pull request, say which platforms you built and tested, and how.

## Pull request checklist

The [pull request template](.github/PULL_REQUEST_TEMPLATE.md) asks for the purpose, scope, test
evidence, and the effect on generated files, security and documentation. Fill it in.

A maintainer reviews every pull request. Automated checks, for example CodeQL, must pass before
merge.

## Security issues

Do not report a vulnerability in a public issue or pull request. Follow
[SECURITY.md](SECURITY.md).

## Conduct

Everyone who takes part must follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

FreeWRL is licensed under the GNU Lesser General Public License, version 3 or later
([LICENSE](LICENSE)). By contributing, you agree that your contribution is offered under the same
license. Keep the existing copyright notices and attribution of the original FreeWRL authors.
