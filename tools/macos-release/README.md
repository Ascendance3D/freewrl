# tools/macos-release

Host-side helpers for the macOS Apple Silicon release process. They are small, use no network, and
never create tags, never create or edit releases, and never push. The full procedure is in
[`RELEASING.md`](../../RELEASING.md).

| Script | Purpose |
| --- | --- |
| `verify-release.sh` | Read-only validation of a release tag: syntax, exists, annotated, peels to the expected SHA, reachable from `origin/master`, agrees with `buildversion.h`, release files present. |
| `make-release-metadata.sh` | From the exact built archive, write `SHA256SUMS.txt` and `release-manifest.json`. SHA-256 comes from the archive bytes. `--selftest` runs built-in checks. |
| `check-ci-run.sh` | Pure, fail-closed decision on whether a run is formal-release evidence: success, exact 40-char commit, `workflow_dispatch` event, `master` branch, workflow file `.github/workflows/macos.yml` (the manual macOS Release Validation run). `push` and `pull_request` runs are refused. The release workflow feeds it facts from the Actions run API. |
| `check-app-version.sh` | Read `CFBundleShortVersionString` from the **built** app and require it to equal the tag version. Blocks a release whose app version does not match its tag. |
| `test-release.sh` | Focused tests for the scripts above, in throwaway repos and temp dirs. Creates no tags, no releases, touches no remote. |

## Quick use

```sh
# validate a tag before building (read-only)
tools/macos-release/verify-release.sh --tag v6.8.0 --expected-sha <40-char-sha>

# after a build, describe the exact archive
tools/macos-release/make-release-metadata.sh \
  --archive out/FreeWRL-6.8.0-macOS-arm64.zip \
  --version 6.8.0 --tag v6.8.0 --commit <40-char-sha> --out out

# run all release-infrastructure tests
tools/macos-release/test-release.sh
```

## The release build

GitHub Actions is a release-validation system only. Pushes and pull requests do not start it;
development QA runs locally.

1. Ryan runs `.github/workflows/macos.yml` (macOS Release Validation) by hand from `master` with
   `expected_sha`. It fails unless the run is on `master` and `github.sha` equals `expected_sha`.
   Build and ASan run on `macos-15` (macOS 15); the minimum-OS runtime gate runs on `macos-14`.
   `MACOS_MIN` stays `14.0`.
2. The release build runs in `.github/workflows/release-macos.yml`. It is manual-dispatch only and
   takes the ID of that successful validation run (checked by `check-ci-run.sh`). It builds from the
   exact annotated tag on `macos-15`, reuses `tools/macos-deps/build.sh`,
   `tools/macos-package/package.sh`, `tools/macos-package/verify.py` and `tools/macos-ci/doctypes.sh`,
   and creates a **draft** release. It never publishes; Ryan publishes by hand.

## Asset contract

```
FreeWRL-VERSION-macOS-arm64.zip     (VERSION has no leading v, e.g. 6.8.0 or 6.8.0-beta.1)
SHA256SUMS.txt
release-manifest.json
```

`release-manifest.json` fields: `project`, `version`, `tag`, `commit`, `platform`, `architecture`,
`minimum_macos`, `asset`, `sha256`.
