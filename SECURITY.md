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
