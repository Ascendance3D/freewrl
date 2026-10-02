# FreeWRL on macOS (Apple Silicon): port status

Fork: https://github.com/Ascendance3D/freewrl. The Apple Silicon port is on the maintained `master` trunk (the single canonical branch; the old `develop` integration line was retired).
Base: upstream SourceForge `develop` @ `b3254b11e` (2024-04-20, "Version 6.7", FreeWRL 6.7.0).
Reference: branch `macos-arm64` ([PR #1](https://github.com/DJAscendance/freewrl/pull/1)), the Mac port of upstream `master` @ `e99ab4a00`.
Development and QA machine: physical MacBook Pro M1 (8 GB, Retina), macOS 27.0.1, Xcode 27.0. Pull requests that can affect macOS get local runtime QA on this machine before they merge: Release and Debug arm64 builds, the standalone package and `verify.py`, strict code-signature verification, the smoke suite, the LaunchServices suite and the host bounds tests. Formal release validation on GitHub's macOS 14 and 15 runners is manual only (see below). Last updated 2026-10-01.

Legend: ✅ verified (with evidence) · 🟡 changed or implemented, not verified · ⛔ unsupported on macOS · ❔ unresolved · ❌ broken

## Support policy

**Supported: macOS 15 Sequoia and newer on Apple Silicon.**

| | |
| --- | --- |
| supported | macOS 15 Sequoia, and newer macOS versions once release validation has run on them |
| architecture | arm64 only |
| not a release target | Intel (x86_64) Macs; macOS 14 Sonoma and older |
| local QA | pull requests that can affect macOS, on a physical Apple Silicon Mac, before merge |
| release validation | [`.github/workflows/macos.yml`](.github/workflows/macos.yml) (Node-24 Actions), manual `workflow_dispatch` only, started by Ryan from `master` for one exact SHA: the packaged app on GitHub's macOS 15 arm64 runners. Pushes and pull requests do not start it. See [`RELEASING.md`](RELEASING.md) |

Earlier development targeted macOS 13, then macOS 14. On 2026-10-02 the owner raised the minimum to macOS 15 Sequoia; release validation runs on the `macos-15` runner. Everything is built with `MACOSX_DEPLOYMENT_TARGET=15.0`; no binary is patched to claim an older macOS.

## Current status (2026-09-30)

| | item | evidence |
| --- | --- | --- |
| ✅ | Canonical trunk | `master` is the single maintained branch; the Apple Silicon work is merged into it |
| ✅ | Runtime gate (PR #15) | PASS on the CI runtime gate |
| 🟡 | AddressSanitizer | CI gate total 0 reports (PROTO lifetime, frustum-extent stack, vector, GLCore client attributes all clean). The 2026-10-01 physical-Mac release validation of `5b9b2d682` found 4 reports on the picking path, which CI never ran (no pointer): heap-use-after-free in `do_SphereSensor` (sensors kept in `SensorEvents` and the touch state after world replacement freed them) and a heap-buffer-overflow in `pop_ray` (pop before read). Fixed on `fix/macos-asan-picking-lifetime`, pending review: every node free path unregisters the node from the picking state (`unRegisterSensitiveNode`; container nodes such as the old scene root through `freeContainerNode`); `suite.sh` drives the pointer (`RELOAD_POINTER`) over `sensor_replace.wrl` and fails when a cycle replaced nothing or the harness faulted; `sensor-proof.sh` proves the SphereSensor handler path on `10.wrl` |
| — | macOS 14 runtime | no longer supported (minimum raised to macOS 15 on 2026-10-02); last PASS on the GitHub Actions arm64 runner |
| ✅ | macOS 15 runtime | PASS (GitHub Actions arm64 runner) |
| 🟡 | Package static verify | `verify.py --macos 15.0`, pending the first macOS 15-minimum validation run |
| ✅ | Physical Apple Silicon runtime QA | local QA on a physical M1 before merge; latest: PR #47, head `a0807a576`: builds, package verify, smoke 17/17, LaunchServices 7/7, host bounds tests 67/67 |
| ✅ | Public macOS prereleases | `v6.7.0-macos-beta.1` and `v6.7.0-macos-beta.2` are published; their notes state Developer ID signing and Apple notarization |
| 🟡 | First desktop release `v6.7.0` | still needs: Developer ID signed, hardened-runtime, notarized and stapled release packaging; release validation; the annotated tag; the draft release; publication. See [`RELEASING.md`](RELEASING.md) |

Texture decoder on macOS: **stb_image** (compiled in; `HAVE_IMLIB2` off). The packaged app links only FreeType, ODE and freealut and uses Apple's `OpenAL.framework`; it needs no Homebrew, Imlib2, FFmpeg or OpenAL Soft at run time. See [Standalone packaging](#standalone-packaging).

## macOS limits

- **OpenGL 4.1 core is the maximum.** Apple stopped at 4.1 and runs it on Metal ("4.1 Metal - 91.7"). FreeWRL creates a 4.1 core context; the library's core-profile path is `FW_GL_CORE_PROFILE`, mostly `freex3d/src/lib/opengl/GLCoreCompat.c`.
- **GPU HAnim skinning is unavailable.** It needs shader storage buffers (GL 4.3). HAnim uses its existing CPU skinning instead.
- **Wide lines are unavailable.** A forward-compatible core context only draws 1-pixel lines; larger `glLineWidth` values are clamped to 1 with one warning.
- **Apple has deprecated OpenGL.** It still ships and works on macOS 27; a Metal or ANGLE backend would be the long-term answer and is not started.

## Upstream lines

| line | commit | date | version | notes |
| --- | --- | --- | --- | --- |
| upstream `master` | `e99ab4a00` | 2020-02-21 | 4.4.0 | older stable line, unchanged since 2020 |
| upstream `develop` | `b3254b11e` | 2024-04-20 | 6.7.0 | active line; 951 commits ahead of `master`, which it fully contains |

## OpenGL 4.1 compatibility layer

Every emulated call, what it replaces and what happens when it can't be done. Evidence: the fixture and test worlds below run in a build with `FW_DEBUG_GL` (glGetError after every render stage) with no GL errors.

| | GL call (version) | FreeWRL caller | macOS replacement | state changed / restored | when impossible |
| --- | --- | --- | --- | --- | --- |
| ✅ | client-memory vertex/index arrays (not in core) | HUD, Text, cursor, Box, lines, points, particles | streamed into per-attribute VBOs at draw time | binds its stream buffers; restores `GL_ARRAY_BUFFER`; element binding put back to 0 | n/a |
| ✅ | default VAO (core requires one) | all drawing | one VAO bound at GL init | `renderQuad` restores it | n/a |
| ✅ | sampler/unit type conflicts (core rejects the draw) | ubershader `textureUnit[]`/`textureUnitCube[]` | unused samplers parked per type on spare top units at each shape | sampler uniforms of the current program | warns once if more than 256 programs or 64 samplers |
| ✅ | `glBindTextureUnit(unit, 0)` (4.5) | `RenderTextures.c` | unbinds 2D, cube and 3D on the unit | active texture unit saved and restored (checked in Debug) | non-zero texture asserts: GL 4.1 can't find its target; no caller passes one |
| ✅ | `glCheckNamedFramebufferStatus` (4.5) | generated cube map, generated texture, shadow maps | bind, `glCheckFramebufferStatus`, restore | draw **and** read framebuffer restored (checked in Debug) | n/a |
| ⛔ | `glGetTextureParameteriv` (4.5) | debug prints inside `if (0)` only | none (GL 4.1 can't query a texture's target) | none | warns once, asserts in Debug, returns 0 |
| ✅ | `glInvalidateBufferData` (4.3) | HAnim GPU-skinning cleanup | no-op: invalidation is only a hint | none | n/a (unreachable on macOS) |
| ✅ | `GL_ALPHA` / `GL_LUMINANCE` / `GL_LUMINANCE_ALPHA` textures (not in core) | Text glyphs, HUD atlases, grey PNGs | `GL_R8`/`GL_RG8` + swizzle | swizzle set on 2D and cube targets; reset to identity on normal uploads | n/a |
| ✅ | `glLineWidth` > 1 (not in forward-compatible core) | LineProperties, particles, cursor | clamped to the context range (1) | line width | one warning, lines draw 1 px |
| ✅ | fixed-function enables (`GL_TEXTURE_2D`, `GL_FOG`, texgen) | legacy calls | ignored; shaders do this work | none | n/a |
| ✅ | GLSL 330 depth/shadow shaders, ubershader at 410 | shadows, cube maps | run as-is on the 4.1 context | | no compile or link errors logged |

## Build

| | item | notes |
| --- | --- | --- |
| ✅ | Release arm64, clean | `xcodebuild -project OSX_gui/FreeWRL-Desktop/FreeWRL.xcodeproj -scheme FreeWRL -configuration Release ARCHS=arm64 CODE_SIGN_IDENTITY=- -derivedDataPath <dir> clean build` → exit 0 |
| ✅ | Debug arm64, clean | same with `-configuration Debug` → exit 0 |
| ✅ | Linked libraries | FreeType, ODE, freealut (from `FW_DEPS`: a `tools/macos-deps` prefix, or Homebrew for local development) and Apple frameworks; Imlib2 replaced by stb_image, openal-soft by `OpenAL.framework` |
| ✅ | Deployment target | 15.0 in every `FreeWRL.xcodeproj` configuration; built with `MACOSX_DEPLOYMENT_TARGET=15.0` |
| ✅ | Self-contained app | `tools/macos-package/package.sh`: macOS 15+, no Homebrew at run time. See [Standalone packaging](#standalone-packaging) |
| ✅ | ffmpeg no longer linked | it was linked but no symbol was imported (`MOVIETEXTURE_FFMPEG` is off); removed |

*Historical:* an earlier candidate linked Homebrew dylibs (ode, ffmpeg, openal-soft, freealut, imlib2, freetype) built for macOS 27 while the app targeted 13.0 (10 `ld` warnings), and was not distributable. That blocker is resolved: libraries are built from source for macOS 14 by `tools/macos-deps/build.sh` and embedded.

### Warnings (clean Release build)

| | before (`906c02a5f`) | after |
| --- | --- | --- |
| warning lines | 1113 | 1094 |
| unique warnings | 1055 | 1036 |

Unique warnings after: 1001 in FreeWRL code, 19 macOS OpenGL deprecation (`NSOpenGLView` and friends in `FWGLView`), 12 Xcode/linker (10 dylib deployment-target mismatches, 1 textured-window xib, 1 headermap), 4 vendored. None in generated code. Most are `-Wunused-variable` (485) and `-Wunreachable-code` (247).

Fixed on this branch (files the port touches): unsequenced `textrans[ntextrans++] = f(ntextrans)` (11, glTF), an out-of-bounds key read and two uninitialized variables in ParticleSystem ramps, uninitialized returns in three `dllFreeWRL_resitem_*` getters, an `fscanf` format mismatch, an implicit struct downcast, a missing `[super prepareOpenGL]`.

Left for upstream (outside port-touched code): `abs()` on floats in `LinearAlgebra.c` (8) and `Component_Geospatial.c` (1), uninitialized variables in `Component_RigidBodyPhysics.c` and `ConsoleMessage.c`, pointer-type mismatches in `Component_Geometry3D.c`/`Component_Text.c`/`X3DParser.c`, 91 `-Wshorten-64-to-32`. `Component_NURBS.c` includes `gl.h` next to `gl3.h` for Apple's GLU NURBS tessellator (intentional; NURBS not tested).

## Runtime (clean Release build)

Fixtures are in `freewrl/tests/regression/` (see its README); each states what a pass looks like.

| | item | evidence |
| --- | --- | --- |
| ✅ | tests/1.wrl, 2, 3, 6, 16, 49 | render; see the harness table |
| ✅ | Cybertown 002 over HTTP | renders; no parse, GL or download errors |
| ✅ | Classic VRML `ROUTE a.b TO c.d` | `route_dotted.wrl`: box turns green and moves, Script prints `ROUTE_OK color=0 1 0` |
| ✅ | Malformed ROUTEs | `route_malformed.wrl`: 4 "Routing problem" reports, a syntax error reported, no crash, scene renders |
| ✅ | X3D `<meta>` | `x3d_meta.x3d`: renders; crashed before this branch |
| ✅ | HAnim, CPU skinning | `hanim_skin.x3d` (harness 0.992): log `Skinning Method: CPU`, upper half of the bar bent 0.9 rad about the joint; `hanim_anim.x3d` captured mid-swing. No GL errors (an SSBO call would raise `GL_INVALID_ENUM` on 4.1); every SSBO call is behind `vertexTransformMethod() == GPU`, which is false without `rdr_caps.av_ssbo` |
| ✅ | LineProperties | `lineproperties.x3d`: four lines, the last dashed; one warning `line width 5 requested ... draw at 1`; no GL errors |
| ✅ | ComposedCubeMapTexture | six square faces sample correctly on a sphere; no GL errors |
| ❔ | GeneratedCubeMapTexture | `cubemap_generated.x3d`: the scene renders and the framebuffer reports complete with no GL errors, but the sphere shows no reflection (black). The `macos-arm64` (master) build also shows it black. Not resolved |
| ✅ | Shadows, spot and point light | `shadows_spot.x3d`, `shadows_point.x3d`: the box casts a shadow on the floor; no shader or GL errors; later frames render normally |
| 🟡 | Shadows, directional light | `shadows_directional.x3d`: renders with the box shadow, but floor areas outside the light's shadow map come out black. Upstream samples with `GL_CLAMP_TO_BORDER` and no border colour (depth 0 = in shadow); upstream describes directional shadows as partly working. Not a macOS issue, not redesigned |
| ✅ | Image formats | stb_image (Imlib2 is not used on macOS). `texture_formats.wrl`: JPEG, PNG, GIF; `texture_formats_stb.wrl`: BMP, TGA, PSD, PPM, HDR |
| ⛔ | TIFF, WebP textures | not decoded on macOS (stb_image has no decoder): `failed to load image`, the shape is drawn untextured, no crash (`texture_unsupported_mac.wrl`). No FreeWRL test world uses either format |
| ✅ | `.wrl`, `.x3d`, HTTP, Inline | tests/1.wrl and 1.x3d from disk; all harness worlds over HTTP; Inline in tests/16.wrl |
| ✅ | HUD layout | one row of 21 buttons at: Retina, 672-pt window (was two rows); Retina, 1200×800-pt window (full-size buttons, room to spare); non-Retina (app copy with `NSHighResolutionCapable` off), 672-px window |
| ✅ | HUD hit targets | drawing and hit testing use the same per-frame geometry; left, centre and right HUD buttons respond to real clicks on Retina, no hit offset (targeted QA on `32caaa36a`) |
| ✅ | Quit from the app menu / Apple event | clean exit, no crash report |
| ✅ | `q` key quit | the Cocoa bridge sent `keyDown:` as `KEYDOWN` only, so no `KEYPRESS` reached the hotkey switch (found by manual QA). Fixed: `keyDown:` now sends `KEYDOWN` then `KEYPRESS` (not for Command chords or arrow/function keys), as on Win32/X11. Physical `q` quit cleanly 3/3 times; `v`, `h`, `e`/`w` run once per press; Command+Q quits and Command+N triggers no hotkey (targeted QA on `32caaa36a`) |
| ✅ | Mouse picking and navigation on Retina, click tests 8 and 10 | picking lands on the visible object (no 2× offset); held-key navigation starts, holds and stops cleanly; test 8 TouchSensor and test 10 drag work (targeted QA on `32caaa36a`) |
| 🟡 | Sound | tests/50.wrl loads; audio output not verified |
| ✅ | Brightness vs master | explained, upstream; see below |
| 🟡 | HAnimHumanoid translation/rotation/scale | not applied: the node has no prep/fin render functions upstream (all platforms, both skinning methods). The fixtures place the viewpoint instead |

### Brightness

6.7 renders textured surfaces brighter than the `macos-arm64` (master) build. Measured with a lit box and headlight, same view, mean luminance:

| world | 6.7 (this branch) | master build | X_ITE |
| --- | --- | --- | --- |
| untextured, diffuseColor 0.8 | 0.194 | 0.212 | 0.140 |
| ImageTexture + default Material | 0.160 | 0.140 | 0.093 |

Two upstream `develop` changes explain it; neither is macOS-specific:

1. **Textures replace the diffuse colour.** The texture averages 0.66 grey. On 6.7 textured/plain = 0.82 = 0.66 / 0.8: the texture replaces the Material's diffuse colour (the VRML97 rule). On master and X_ITE the ratio is 0.66: the texture is multiplied by the default diffuse 0.8.
2. **All output is converted to sRGB.** The ubershader ends with `fragment_color.rgb = LINEARtoSRGB(fragment_color.rgb)` (upstream `d6e06eba9`, 2020-03-22, after `master`). Measured: Background `skyColor 0.2 0.2 0.3` is drawn as (123,123,148); LINEARtoSRGB of it is (124,124,149); X_ITE draws (51,51,76).

The macOS compatibility layer does not touch RGB textures or colour output. The shading style is not the cause: forcing Gouraud (`--shadingStyle 1`) is brighter still. Cybertown 002 mean luminance: 6.7 0.654, X_ITE 0.424 (same view); the master build measured 0.571 at a slightly different viewport height. Whether 6.7's sRGB output is intended is an upstream question; this branch does not change it.

## Visual harness

Clean Release build vs X_ITE (`tools/visual-test/compare.sh`); match = normalized cross-correlation, pass ≥ 0.90. Labels for known reference or animation limits come from `tools/visual-test/known.tsv`.

| world | match | result |
| --- | --- | --- |
| tests/1.wrl | 0.9948 | PASS |
| tests/2.wrl | 0.9538 | PASS |
| tests/3.wrl | 0.5604 | REFERENCE_INVALID (X_ITE rejects TextureCoordinateGenerator; the staircase also rotates) |
| tests/6.wrl | 0.8429 | NONDETERMINISTIC (animated) |
| tests/16.wrl | 0.9189 | PASS |
| tests/49.wrl | 0.4905 | NONDETERMINISTIC (text cycles) |
| Cybertown worlds/002/home.wrl | 0.9659 | PASS |
| regression/route_dotted.wrl | 0.9985 | PASS |
| regression/route_malformed.wrl | 0.5000 | REFERENCE_INVALID (X_ITE rejects the whole file at the deliberate syntax error; FreeWRL renders the scene) |
| regression/x3d_meta.x3d | 0.9993 | PASS |
| regression/hanim_skin.x3d | 0.9920 | PASS |
| regression/hanim_anim.x3d | 0.8310 | NONDETERMINISTIC (animated) |
| regression/lineproperties.x3d | 0.7535 | REGRESSION — expected: the width 5 and width 3 lines draw 1 px wide (macOS wide-line limit, ⛔); pattern and positions match |
| regression/cubemap_generated.x3d | 0.9405 | PASS on the score, but the sphere's reflection is missing in FreeWRL (❔ above); the black sphere is a small part of the frame |
| regression/shadows_directional.x3d | 0.8390 | REGRESSION — FreeWRL defect: black floor areas outside the shadow map, box shadow missing (upstream, 🟡 above) |
| regression/shadows_spot.x3d | 0.9602 | PASS |
| regression/shadows_point.x3d | 0.9596 | PASS |
| regression/texture_formats.wrl | 0.9665 | PASS |

Two REGRESSION rows remain on purpose: they are real differences from the reference, explained above, and not relabelled.

## Standalone packaging

The packaging tooling is complete and tested; see [`tools/macos-package/README.md`](tools/macos-package/README.md) and [`THIRD-PARTY.md`](tools/macos-package/THIRD-PARTY.md).

- `tools/macos-deps/build.sh` builds FreeType 2.14.3, ODE 0.16.6 (double precision, internal libccd) and freealut 1.1.0 from pinned source archives (each SHA-256 checked) for `MACOSX_DEPLOYMENT_TARGET=15.0`. freealut links Apple's `OpenAL.framework`.
- `tools/macos-package/package.sh` builds the Release arm64 app against those libraries, embeds the three non-Apple dylibs, rewrites install names, copies license payloads, signs (ad-hoc, or Developer ID with `-r` for the hardened runtime), runs `verify.py --macos 15.0`, and can notarize, staple and produce a zip with its SHA-256.
- `verify.py` fails if the bundle references Homebrew, `/usr/local`, MacPorts, the source tree or a temp/home path, needs a newer macOS than `--macos`, or embeds a library the build no longer uses (Imlib2, FFmpeg, OpenAL Soft). The unpackaged build fails it as a negative control.
- The packaged app needs no Homebrew, Imlib2, FFmpeg or OpenAL Soft at run time.

The macOS prereleases `v6.7.0-macos-beta.1` and `v6.7.0-macos-beta.2` are published; their notes state Developer ID signing and Apple notarization. The draft release workflow (`.github/workflows/release-macos.yml`) builds an ad-hoc signed app only. That ad-hoc output is not the planned macOS release asset: `v6.7.0` ships only a Developer ID signed, hardened-runtime, notarized and stapled app that `package.sh -s … -r --notarize` builds locally from the release tag (see [`RELEASING.md`](RELEASING.md)).

*Historical:* an earlier candidate embedded Homebrew bottles (Imlib2 and its X11/image loaders, and more) and required macOS 27 because those bottles were built for it. That design is obsolete: libraries are now built from source for macOS 14, textures are decoded by stb_image, and the app links only FreeType, ODE and freealut.

## Fixed on this branch (upstream bugs, all platforms)

- ROUTE parsing: since `7615eadcd` (Feb 2024) `node.field` lexed as one identifier, so every classic VRML ROUTE failed, and the error path aborted the parse thread (freeing uninitialized pointers).
- X3D `<meta>`: since `bfa0de411` (2023-07) any `.x3d` file with a `<meta name content>` tag crashed the parser (`content` read as `category`).
- Shadows: since `304e78bfc` (2023-12) every Shape rendered into a shadow map recursed until the stack overflowed.
- Missing prototypes, including four pointer-returning functions that an implicit declaration truncates on 64-bit targets.
- A variable defined in `Component_Shape.h` (duplicate symbol under clang's default `-fno-common`).

## Fixed on this branch (macOS frontend)

- Keyboard: `FWGLView` sent every key as `KEYDOWN` (a local `#define KeyPress 2`), never `KEYPRESS`, so every one-shot hotkey (`q`, viewer modes, `v`/`b` viewpoints, `h` headlight, `c` collision, the `:` command line, ...) and StringSensor did nothing. The mapping is in `FWKeyEvents.h`; `tools/key-events-test/run.sh` tests it.

## Next up

- [x] Verify `q`, picking, navigation, HUD clicks and tests 8/10 on Retina (targeted QA on `32caaa36a`, token `FREEWRL_6_7_MACOS_ARM64_GL41_KEYBOARD_AND_INTERACTION_QA_PASS`)
- [x] Standalone package for macOS 15+ with libraries built from source; see [Standalone packaging](#standalone-packaging)
- [ ] GeneratedCubeMapTexture: find why the generated faces sample black
- [ ] Directional light shadows outside the shadow map (upstream)
- [x] Publish a public macOS prerelease (`v6.7.0-macos-beta.1` and `v6.7.0-macos-beta.2`)
- [ ] Sign, notarize, validate, tag and publish the first desktop release `v6.7.0` (see [`RELEASING.md`](RELEASING.md))
- [ ] Port `MPEG_Utils_ffmpeg.c` to ffmpeg 5+ (MovieTexture)
