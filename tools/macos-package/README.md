# macOS standalone packaging

Builds a `FreeWRL.app` for Apple Silicon that runs on macOS 14 Sonoma and newer
without Homebrew: the three non-Apple libraries it links are built from source
for macOS 14 and embedded.

```sh
tools/macos-package/package.sh                   # libraries, Release build, package, ad-hoc sign, verify
tools/macos-package/package.sh -z                # ... and zip it (prints the SHA-256)
tools/macos-package/package.sh -s "Developer ID Application" -r -z   # Developer ID, hardened runtime
tools/macos-package/package.sh -s "Developer ID Application" -r --notarize  # ... notarized, stapled, zipped
tools/macos-package/verify.py --macos 14.0 FreeWRL.app   # the portability gate on its own
```

Output goes to `./macos-package-out` (`-o` to change). `-t` sets the oldest
macOS (default and supported floor: 14.0). `-D <prefix>` reuses libraries
already built by `tools/macos-deps/build.sh` for that macOS; `-a <app>`
packages an existing Release build instead of building one. The signing
identity is any `codesign -s` value; the default `-` is ad-hoc.

Needs only Xcode (its command line tools) and network access for the source
archives. Homebrew is not used.

## Document-type routing (mandatory before distributing a build)

Finder double-click and `open -a FreeWRL world.wrl` route a world to FreeWRL
through LaunchServices, not on argv. Two things must both hold or the routed
open fails with "FreeWRL cannot open files in the … file format": the
`CFBundleDocumentTypes` extensions must be bare (`wrl`, not `.wrl`), and the app
delegate must implement `application:openURLs:` to hand the document to
`dllFreeWRL_onLoad`. CI runs the static half automatically
(`tools/macos-ci/doctypes.sh`, in the build job).

The live open needs a GUI login session, which CI runners do not have, so run it
by hand on the packaged app before signing/notarizing any build for release:

```sh
tools/macos-ci/launchservices.sh macos-package-out/FreeWRL.app   # expect LAUNCHSERVICES 7/7
```

It opens `.wrl/.wrz/.wrlz`, `.x3d/.x3dz`, `.x3dv/.x3dvz` through `open -a`, one
FreeWRL at a time, and fails unless each routed document reaches the loader and
renders. Do not ship a build that has not passed 7/7.

## What it does

1. `tools/macos-deps/build.sh -t 14.0`: downloads FreeType 2.14.3, ODE 0.16.6
   and freealut 1.1.0, checks each archive's SHA-256, and builds them with
   `-mmacosx-version-min=14.0` into a private prefix (ODE: double precision,
   its internal libccd; freealut: against Apple's `OpenAL.framework`). Writes
   `share/freewrl-deps/packages.tsv` (package, version, libraries, source URL,
   SHA-256) and each package's license files.
2. `xcodebuild` Release, arm64, `MACOSX_DEPLOYMENT_TARGET=14.0`,
   `FW_DEPS=<prefix>` (skipped with `-a`).
3. `bundle.py`: walks the executable's dependencies, copies every library
   outside `/usr/lib` and `/System/Library` into `Contents/Frameworks`
   (libfreetype.6, libode.8, libalut.0 for the current build), and rewrites
   install names to `@rpath/<name>`; the run paths are
   `@executable_path/../Frameworks` (executable) and `@loader_path`
   (Frameworks). Copies each package's license files to
   `Contents/Resources/ThirdPartyLicenses/`, writes `MANIFEST.tsv`
   (binary → package, version) and `LICENSES.tsv` (license file → package,
   version, source archive and SHA-256), and sets `LSMinimumSystemVersion` to
   the newest minimum macOS of any binary in the bundle. It never lowers a
   binary's minimum macOS: that comes from the compiler and linker. (The script
   still knows how to embed a `dlopen`ed plugin set under `Contents/PlugIns`;
   the current build links no such library, so none is copied.)
4. License texts of code compiled into FreeWRL (FreeWRL, Duktape, libtess,
   stb_image), copied verbatim from the source tree.
5. Signs inside out: each dylib, then the app.
6. `verify.py --macos 14.0` and `codesign --verify --deep --strict`.
7. With `--notarize` (`-n`): submits a zip of the app with `notarytool --wait`,
   fails unless Apple answers `Accepted` (the log is saved as
   `notary-log.json`), staples the ticket, runs `stapler validate` and
   `spctl --assess`, and only then writes the final zip. Needs `-s` with a
   Developer ID Application identity and `-r`.

See [THIRD-PARTY.md](THIRD-PARTY.md) for the embedded libraries and their licenses.

## Images

Textures are decoded by stb_image (compiled into FreeWRL, `HAVE_IMLIB2` is off
in the macOS `config.h`): JPEG, PNG, GIF (first frame), BMP, TGA, PSD, HDR and
PNM. TIFF and WebP are not decoded on macOS; such a texture logs
`failed to load image` and the shape is drawn untextured. DDS, web3dit, NRRD
and `.vol` keep FreeWRL's own loaders. Fixtures:
`freewrl/tests/regression/texture_formats.wrl`, `texture_formats_stb.wrl`,
`texture_unsupported_mac.wrl`.

## Notarization credentials

Read from the environment, checked before the build starts, never printed:

- `NOTARY_KEYCHAIN_PROFILE`: a profile saved with `xcrun notarytool store-credentials`; or
- `NOTARY_KEY_ID` and `NOTARY_ISSUER` (or `APPLE_API_KEY_ID` and `APPLE_API_ISSUER`):
  an App Store Connect API key, with `NOTARY_KEY` pointing to its `.p8` file
  (default `~/.appstoreconnect/private_keys/AuthKey_<key ID>.p8`).
- `NOTARY_ENV_FILE`: a shell file that sets any of these, read first.

```sh
NOTARY_ENV_FILE=~/.config/notary.env tools/macos-package/package.sh \
    -s "Developer ID Application: <name> (<team>)" -r --notarize
```

Notarization is never run in CI: it needs credentials, and pull requests run
untrusted code.

## verify.py

Fails if any Mach-O in the bundle

- has a dependency, install name or run path that points outside the bundle
  (other than Apple's `/usr/lib` and `/System/Library`) or at Homebrew,
  `/usr/local`, MacPorts, `/sw`, the source tree, a temporary or home directory;
- isn't arm64/macOS, or needs a newer macOS than `LSMinimumSystemVersion` or
  than `--macos`;
- is a library the macOS build no longer uses (Imlib2, FFmpeg, OpenAL Soft);

or if `LSMinimumSystemVersion` is newer than `--macos`, FreeType, ODE or
freealut is not embedded, the fonts, license manifests or FreeType's
`LICENSE.TXT`/`FTL.TXT` are missing, an embedded package or a component
compiled into FreeWRL has no license file in `LICENSES.tsv`, or `LICENSES.tsv`
lists a file that isn't there. Paths that only appear as strings inside a
binary are warnings (`__FILE__` names in FreeWRL's asserts); nothing opens
them at run time. The unpackaged Release build fails it, which CI checks as a
negative control.

## Hardened runtime

Needs a real signing identity. With an ad-hoc signature there is no Team ID, so
library validation rejects every bundled dylib ("mapping process and mapped
file (non-platform) have different Team IDs") and the app doesn't start. Signed
with one Developer ID identity, everything shares a Team ID and no entitlements
are needed: FreeWRL uses no JIT or writable-executable memory (Duktape is an
interpreter), loads no libraries signed by others, and reads no `DYLD_`
variables. CI tests the ad-hoc package without the hardened runtime.
