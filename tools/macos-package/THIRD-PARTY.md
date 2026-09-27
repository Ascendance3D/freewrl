# Third-party libraries in the macOS app

What the standalone `FreeWRL.app` built by `package.sh` contains and which
distribution materials it ships. This records measured facts. It is not legal
advice, and it does not claim that the package complies with any license.

In the app:

- `Contents/Frameworks/`: the three embedded libraries below, nothing else.
- `Contents/Resources/ThirdPartyLicenses/<package>/`: each package's license files.
- `MANIFEST.tsv`: every embedded binary → package and version.
- `LICENSES.tsv`: every license file → package, version and where it was copied
  from (source archive URL and SHA-256, or the file in FreeWRL's tree).

## Embedded libraries

Built from source by `tools/macos-deps/build.sh` for macOS 14.0 (arm64), from
the archives Homebrew's formulae use, each checked against a pinned SHA-256.
Copied into the app unmodified apart from install names and signatures.

| library | package | version | license | license files in the app | source archive (SHA-256) |
| --- | --- | --- | --- | --- | --- |
| libfreetype.6 | FreeType | 2.14.3 | FTL or GPL-2.0 (FreeType's choice of either) | `LICENSE.TXT`, `FTL.TXT`, `GPLv2.TXT` | `freetype-2.14.3.tar.xz` (`36bc4f1c…785a5f`) |
| libode.8 | ODE | 0.16.6 | LGPL-2.1-or-later OR BSD-3-Clause; its internal libccd is BSD-3-Clause | `COPYING`, `LICENSE.TXT`, `LICENSE-BSD.TXT`, `libccd-BSD-LICENSE` | `ode-0.16.6.tar.gz` (`c91a28c6…4513e8`) |
| libalut.0 | freealut | 1.1.0 | LGPL-2.0-only | `COPYING` | `freealut_1.1.0.orig.tar.gz` (`60d1ea87…8df44f`) |

FreeType is built with the system zlib and bzip2 only (no libpng, HarfBuzz or
Brotli). ODE is double precision with its bundled libccd. freealut links Apple's
`OpenAL.framework`, as FreeWRL does; OpenAL Soft is not used.

## LGPL-licensed libraries

freealut and ODE (under its LGPL option) are linked dynamically:
`Contents/Frameworks/libalut.0.dylib` and `libode.8.dylib`, loaded as
`@rpath/libalut.0.dylib` and `@rpath/libode.8.dylib`. The exact source archive
and SHA-256 of each is in `LICENSES.tsv`, and `tools/macos-deps/build.sh` shows
how they were configured and built.

Replacing an embedded library (tested with freealut on an earlier candidate):

- The dylib is a separate file. A user can swap in their own build of
  `libalut.0.dylib`, with install name `@rpath/libalut.0.dylib`.
- Doing so breaks the app's signature: `codesign --verify` reports "nested code
  is modified or invalid", and Gatekeeper refuses to open the app ("is damaged
  and can't be opened").
- Re-signed by the user (`codesign --force --deep -s - FreeWRL.app`), the app
  starts and maps the replacement library (seen with `lsof`). It is then no
  longer the Developer ID-signed, notarized app.

## Compiled into FreeWRL

- FreeWRL (LGPL-3.0-or-later, `freex3d/COPYING.LESSER` plus the GPL v3 it
  builds on, `freex3d/COPYING`)
- Duktape 2.0.0 (MIT), text from `duktape.c`
- libtess (SGI Free Software License B), text from `tess.c`
- stb_image 2.27 (MIT or public domain, at the user's choice), text from
  `stb_image.h`

Their texts are copied from the source tree by `package.sh`.

## Not in the app

Apple frameworks and `/usr/lib` libraries (OpenGL, OpenAL, Cocoa, libcurl,
libxml2, libz, libbz2, libc++) are not copied. Imlib2 and the libraries it
pulled in (X11, xcb, libpng, libjpeg-turbo, giflib, libtiff, libwebp, zstd, xz),
FFmpeg and OpenAL Soft are no longer linked; `verify.py` fails if any of them
appears.
