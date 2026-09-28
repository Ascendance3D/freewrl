# Releasing FreeWRL Revival for Mac Silicon

This guide describes how to make a formal macOS Apple Silicon release. It covers the whole path,
from an approved commit to a published GitHub Release and the SourceForge mirror.

The process is deliberately safe and repeatable. A person, Ryan, makes every publish decision. The
workflow never publishes on its own.

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
7. GitHub Actions is the final release build system.
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

Other version strings in the tree are stale and are **not** authoritative:

- `freex3d/configure.ac` (`AC_INIT ... 4.3.0`) — Linux autotools only, unused on macOS.
- `freex3d/versions/FREEWRL` (`5.0.0`) — stale.
- `OSX_gui/FreeWRL-Desktop/FreeWRL/FreeWRL-Info.plist` (`CFBundleShortVersionString 4.2`) — stale;
  the app's Info.plist short version does not track `buildversion.h`.

**Limitation.** The validator proves the tag agrees with `buildversion.h`. It does not repair the
stale Info.plist short version. If you want the app's displayed version to match, update
`buildversion.h` and, separately, the Info.plist, before you tag. That code change is out of scope
for the release infrastructure and belongs in a normal engine PR.

## Step-by-step release procedure

### 1. Prerequisites

- The commit to release is already on `master` and reviewed.
- You chose the version. Do not assume the next number; pick it deliberately.
- You are on macOS 14 (Sonoma) or newer on Apple Silicon for any local checks.

### 2. Confirm green CI

- Find the `macOS Apple Silicon CI` run for the exact commit.
- Confirm it succeeded: host container tests, build/package, package verify, doctypes, runtime,
  smoke, and the ASan gate (Total = 0).
- Note the **run ID**; the release workflow verifies it.

### 3. Create the annotated tag

```sh
git tag -a v6.8.0 -m "FreeWRL Revival for Mac Silicon 6.8.0" <commit>
git push origin v6.8.0
```

Use an **annotated** tag (`-a`). A lightweight tag is rejected.

### 4. Verify the tag before building

```sh
tools/macos-release/verify-release.sh --tag v6.8.0 --expected-sha <full-40-char-sha>
```

This proves the tag exists, is annotated, peels to the expected commit, is reachable from
`origin/master`, agrees with `buildversion.h`, and that the release files are present. It is
read-only.

### 5. Dispatch the release workflow

Run the **macOS Release (draft)** workflow (`.github/workflows/release-macos.yml`) with:

- `tag` — the annotated tag, e.g. `v6.8.0`
- `expected_sha` — the full 40-char commit SHA
- `ci_run_id` — the green CI run ID from step 2
- `prerelease` — `true` for a beta/rc, otherwise `false`

The workflow re-proves everything in step 4, verifies the CI run, builds from the exact tag,
packages, runs package verification and the document-type gate, names the asset to the contract,
generates the checksums and manifest, verifies them against the archive bytes, and creates a
**DRAFT** release. It does not publish.

### 6. Review the draft

- Open the draft release on GitHub.
- Confirm the asset name, the notes, the version, the commit, and the minimum macOS.
- Confirm the draft claims no code signing, no notarization, and no Intel support unless a real,
  proven signing/notarization step produced them.

### 7. Verify the assets and checksums

Download the archive and `SHA256SUMS.txt`, then:

```sh
shasum -a 256 -c SHA256SUMS.txt
```

Confirm the SHA-256 in `release-manifest.json` equals the value in `SHA256SUMS.txt`.

### 8. Publish (Ryan only)

Ryan edits the final notes and publishes the GitHub Release by hand. The workflow never publishes.

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
4. Push the exact annotated release tag to SourceForge:
   ```sh
   git push sourceforge-mirror v6.8.0
   ```
5. Confirm the peeled SourceForge tag commit matches GitHub:
   ```sh
   git ls-remote --tags sourceforge-mirror v6.8.0
   ```

Rules:

- Never create a SourceForge-only release commit.
- Never force a SourceForge tag.
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
