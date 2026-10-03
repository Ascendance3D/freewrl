# Xcode Cloud scripts

Xcode Cloud runs these scripts by name. They live next to `FreeWRL.xcodeproj`, and the
workflow uses the shared scheme `FreeWRL` (`FreeWRL.xcodeproj/xcshareddata/xcschemes`).

- `ci_post_clone.sh` runs the host-only container tests. It builds FreeType, ODE and
  freealut from their pinned sources for the project's `MACOSX_DEPLOYMENT_TARGET`. It then
  sets `FW_DEPS` to that prefix and `ARCHS = arm64` in the clone's `project.pbxproj`, because
  Xcode Cloud cannot pass build settings on the command line.
- `ci_post_xcodebuild.sh` checks the built `FreeWRL.app`: arm64 only, `minos` and
  `LSMinimumSystemVersion` equal to the deployment target, and the static document-type gate.
  It fails when a successful build action left no `FreeWRL.app` (or more than one) where
  Xcode Cloud puts it.

Xcode Cloud does not start FreeWRL. Smoke, runtime and ASan proof stay in
`.github/workflows/macos.yml`, and GitHub Actions stays the final gate.

## Workflow setup (once, in Xcode)

1. Open `OSX_gui/FreeWRL-Desktop/FreeWRL.xcodeproj` and choose
   Integrate > Create Workflow (or Product > Xcode Cloud > Create Workflow).
2. Product `FreeWRL`, scheme `FreeWRL`, team: your team. Grant access to
   `Ascendance3D/freewrl` on GitHub when asked.
3. Start condition: manual only (or branch changes on `master`). Environment: the latest
   release Xcode and macOS. Action: Build, platform macOS (Archive also works, but needs
   cloud signing).
4. Start a build from Xcode's Report navigator, or from App Store Connect > Xcode Cloud.
