# Releasing FreeWRL Revival for Mac Silicon

This guide describes how to make a formal macOS Apple Silicon release. It covers the whole path,
from an approved commit to a published GitHub Release and the SourceForge mirror.

The process is deliberately safe and repeatable. A person, Ryan, makes every publish decision. The
workflow never publishes on its own.

## GitHub Actions policy: release validation only

GitHub Actions is a release-validation system, not a development test system.

- Normal development and PR QA run **locally**.
- Pushes and pull requests do **not** start GitHub Actions.
- Ryan explicitly starts formal release validation: a manual run of
  `.github/workflows/macos.yml` (macOS Release Validation, `workflow_dispatch`).
- Release validation runs from `master` for **one exact expected SHA** (`expected_sha`, 40 hex
  characters). The run fails at once if it is not on `master` or if `github.sha` differs from
  `expected_sha`.
- The build and ASan jobs use a standard `macos-15` runner (Apple
  Silicon).
- The minimum-OS runtime gate runs on the standard `macos-14` runner. This is the real proof that
  the app runs on the minimum supported macOS.
- `MACOS_MIN` remains `14.0`. The macOS 15 build runner does not change the product minimum.
- The draft release workflow accepts only the successful manual validation run for the same SHA.

Codemagic is separate and supplemental. It never publishes releases.

## The tag-versus-release model

A **tag** is an immutable Git label on one commit. A **release** is a GitHub object that carries
notes and downloadable assets and points at a tag.

The two are separate on purpose:

- The tag fixes the exact source the release was built from.
- The release build runs from that exact tagged commit, never from a moving branch head.
- The GitHub Release stays a **draft** until Ryan publishes it.

## Release principles (read first)

1. A published version tag is immutable.
2. Never move an existing version tag.
3. Never replace a published version with a different commit.
4. A correction gets a new version (for example `v6.8.0` then `v6.8.1`).
5. New formal releases use **annotated** Git tags.
6. A release must build from the exact tagged commit.
7. GitHub Actions is the final release build system, and it runs only when Ryan starts it.
8. Codemagic never publishes releases; it is supplemental only.
9. SourceForge is a mirror; it never gets a unique release commit.
10. Ryan publishes the final GitHub Release by hand.

## Tag and asset contract

New formal release tags use this form:

```
vMAJOR.MINOR.PATCH
```

Pre-release tags are allowed when needed:

```
vMAJOR.MINOR.PATCH-beta.N     (also -alpha.N, -rc.N)
```

`VERSION` is the tag without the leading `v`, for example `6.8.0` or `6.8.0-beta.1`.

The macOS Apple Silicon asset name is fixed:

```
FreeWRL-VERSION-macOS-arm64.zip
```

Example only (do not create this version now): `FreeWRL-6.8.0-macOS-arm64.zip`.

Each release also carries:

- `SHA256SUMS.txt` — the archive SHA-256, in `shasum -a 256 -c` format.
- `release-manifest.json` — a small machine-readable record for the future Downloads page.

GitHub attaches source `zip` and `tar.gz` archives automatically. We do not duplicate those.

> **Historical note.** The 2026-09 betas used the older names `v6.7.0-macos-beta.1` /
> `v6.7.0-macos-beta.2` and assets like `FreeWRL-6.7.0-macos-arm64-beta.2.zip`. Those tags and
> releases are **immutable** and are **not** renamed. The contract above applies to new releases.

## Version truth

The macOS application version comes from one source:

- `freex3d/src/buildversion.h` → `FW_BUILD_VERSION_STR` (currently `6.7.0`).

That value drives the built app on macOS (`freex3d/src_aqua/fwVersion.c` →
`libFreeWRL_get_version` in `ui/common.c`). The release validator checks the tag version against
this file **at the tagged commit**.

The Desktop app's `OSX_gui/FreeWRL-Desktop/FreeWRL/FreeWRL-Info.plist` sets
`CFBundleShortVersionString` to the same value as `FW_BUILD_VERSION_STR`. When you change the
version in `buildversion.h`, change the plist in the same commit. The `source-version-identity`
check in `tools/macos-release/test-release.sh` fails when the two values differ.

Some other version strings in the tree are stale and are **not** authoritative:

- `freex3d/configure.ac` (`AC_INIT ... 4.3.0`) — Linux autotools only, unused on macOS.
- `freex3d/versions/FREEWRL` (`5.0.0`) — stale.

**Built-app version gate.** The release workflow also reads `CFBundleShortVersionString` from the
**built** `FreeWRL.app` and requires it to equal the tag version (core `MAJOR.MINOR.PATCH`, so
`v6.8.0-beta.1` expects `6.8.0`). This inspects the real build artifact, not the source plist. It
runs `tools/macos-release/check-app-version.sh`. This gate is the final artifact check: if drift in
the sources or in the build settings gives the app a version that differs from the tag, the release
stops.

## Step-by-step release procedure

### 1. Finish local development QA

- Development and PR QA are done locally. Nothing on GitHub Actions is used for this.
- You chose the version. Do not assume the next number; pick it deliberately.
- You are on macOS 14 (Sonoma) or newer on Apple Silicon for any local checks.

### 2. Merge the approved candidate to master

The commit to release must be on `master` and reviewed.

### 3. Record the exact master SHA

```sh
git fetch origin
git rev-parse origin/master
```

Write down the full 40-char SHA. This is `expected_sha` for every later step.

### 4. Run release validation (manual)

Run the **macOS Release Validation** workflow (`.github/workflows/macos.yml`) by hand:

- branch: `master`
- `expected_sha`: the full 40-char SHA from step 3

The workflow fails at the start unless `expected_sha` is 40 hex characters, the run is on `master`,
and `github.sha` equals `expected_sha`. It has one fixed test contract and no profile selector:

- `build` on `macos-15`: host container tests, dependency build, Release build, package,
  package verify (every `minos` is `14.0`), doctypes, Debug build;
- `runtime` on `macos-14`: smoke fixtures, world-replacement cycles, texture stress, runtime GATE,
  crash count, allocator-abort count;
- `asan` on `macos-15`: Debug AddressSanitizer build, world replacement, texture lifetime, ASan
  classification, Total = 0.

### 5. Require the validation run to pass

Every job must succeed. If any job fails, do not release. Fix the problem, merge to `master`, and
start again from step 3 with the new SHA.

### 6. Record the validation run ID

Write down the run ID of the successful validation run.

The release workflow reads the run from the GitHub Actions run API and refuses it unless **all** of
these are true (`tools/macos-release/check-ci-run.sh`):

- `conclusion` is `success`;
- `head_sha` equals the full 40-char `expected_sha`;
- `event` is `workflow_dispatch`;
- `head_branch` is `master`;
- `path` is `.github/workflows/macos.yml` (the workflow file, not only its display name).

A `push` run and a `pull_request` run are **not** release evidence.

### 7. Create the annotated tag on that exact SHA

```sh
git tag -a v6.8.0 -m "FreeWRL Revival for Mac Silicon 6.8.0" <expected_sha>
git push origin v6.8.0
```

Use an **annotated** tag (`-a`). A lightweight tag is rejected. `v6.8.0` is an example only.

### 8. Verify the tag

```sh
tools/macos-release/verify-release.sh --tag v6.8.0 --expected-sha <full-40-char-sha>
```

This proves the tag exists, is annotated, peels to the expected commit, is reachable from
`origin/master`, agrees with `buildversion.h`, and that the release files are present. It is
read-only.

### 9. Run the draft release workflow (manual)

Run the **macOS Release (draft)** workflow (`.github/workflows/release-macos.yml`) with:

- `tag` — the annotated tag, e.g. `v6.8.0`
- `expected_sha` — the full 40-char commit SHA
- `ci_run_id` — the run ID of the successful manual validation run from step 6
- `prerelease` — `true` for a beta/rc, otherwise `false`

The release job runs on `macos-15` (macOS 15) with `MACOS_MIN=14.0`. It does not repeat the
macOS 14 runtime tests; the validation run in step 4 already proved them.

The workflow re-proves everything in step 8, verifies the validation run against the contract in
step 6, builds from the exact tag, packages, runs package verification and the document-type gate,
checks the **built app's** `CFBundleShortVersionString` equals the tag version, names the asset to
the contract, generates the checksums and manifest, verifies them against the archive bytes, and
creates a **DRAFT** release. It does not publish.

### 10. Review and publish the draft (Ryan only)

- Open the draft release on GitHub.
- Confirm the asset name, the notes, the version, the commit, and the minimum macOS.
- Confirm the draft claims no code signing, no notarization, and no Intel support unless a real,
  proven signing/notarization step produced them.
- Download the archive and `SHA256SUMS.txt`, then run `shasum -a 256 -c SHA256SUMS.txt`. Confirm
  the SHA-256 in `release-manifest.json` equals the value in `SHA256SUMS.txt`.
- Ryan edits the final notes and publishes the GitHub Release by hand. The workflow never
  publishes.

### 11. Mirror master and the exact release tag to SourceForge

Follow the manual procedure in the SourceForge section below.

## Tag immutability and rollback

- **Never move a published tag.** Never force-push a tag.
- A published release is immutable. Do not replace its commit.
- To correct a released version, create a **new** version:
  - a patch fix → next PATCH (e.g. `v6.8.0` → `v6.8.1`);
  - build the new version through this same process.
- If a draft is wrong, delete the **draft** (it was never published) and start again with a new
  tag if the tag was also wrong. Do not reuse a tag that already points at published content.

## SourceForge mirror procedure (manual)

SourceForge is a mirror. It is **not** automated from GitHub Actions. After Ryan publishes an
approved GitHub Release, do these steps by hand:

1. Verify GitHub `master` and the release tag are what you expect.
2. Verify the release tag peels to the published commit.
3. Fast-forward the SourceForge `master` if it is behind:
   ```sh
   git push sourceforge-mirror master
   ```
4. Push the exact annotated release tag to SourceForge (no `--force`, no `+` refspec):
   ```sh
   git push sourceforge-mirror refs/tags/v6.8.0
   ```
5. Confirm the **peeled** SourceForge tag commit equals the release commit and the GitHub/local
   peeled tag commit.

   An annotated tag ref (`refs/tags/v6.8.0`) points at a **tag object**, not at the commit. The
   `refs/tags/v6.8.0^{}` entry is the **peeled** commit. `git ls-remote --tags REMOTE v6.8.0`
   prints only the tag-object line, so it does not prove the commit. Ask for the `^{}` ref:
   ```sh
   TAG=v6.8.0
   EXPECTED=<full-40-char-release-commit>
   LOCAL=$(git rev-parse "refs/tags/$TAG^{commit}")
   GH=$(git ls-remote origin "refs/tags/$TAG^{}" | cut -f1)
   SF=$(git ls-remote sourceforge-mirror "refs/tags/$TAG^{}" | cut -f1)
   echo "expected=$EXPECTED local=$LOCAL github=$GH sourceforge=$SF"
   [ -n "$SF" ] && [ "$SF" = "$EXPECTED" ] && [ "$SF" = "$LOCAL" ] && [ "$SF" = "$GH" ] \
     && echo "SourceForge tag OK" || echo "MISMATCH: stop, do not force anything"
   ```
   All four values must be the same 40-char SHA. An empty `sourceforge` value means the tag is
   missing or is lightweight (a lightweight tag has no `^{}` entry); stop.

Rules:

- Never create a SourceForge-only release commit.
- Never force-push to SourceForge (no `--force`, no `+` refspec), for `master` or a tag.
- If the SourceForge peeled commit differs, stop and investigate. Do not move or re-push the tag.
- The mirror only carries the modern release tags, not the historical upstream tag set.

## Future website Downloads contract

Do not edit the website from this repository. The future `freewrl.com` / `freewrl.org` Downloads
page can read a release entirely from the GitHub Releases API:

- the release **tag** and **name**;
- the release **notes**;
- the macOS archive `FreeWRL-VERSION-macOS-arm64.zip`;
- `SHA256SUMS.txt`;
- `release-manifest.json`.

Because the asset name and the manifest are stable and machine-readable, the website never has to
guess a package filename. That is why the asset contract matters.

## What the release process does NOT claim

The current macOS build is ad-hoc signed only. Release notes must not claim:

- code signing with a Developer ID;
- notarization;
- Intel (x86_64) support;
- any compatibility that CI did not prove.

If a future release adds real Developer ID signing and notarization (see
`tools/macos-package/package.sh` `-s`/`-r`), update this guide and the notes to match what the
build actually produced.
