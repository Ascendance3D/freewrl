# Metal Backend Decision Document

Design spike for issue #153. No renderer code. All counts below were taken at the head of this
branch; the commands are given so they can be re-run.

## 1. OpenGL Surface Inventory
On macOS FreeWRL runs on an OpenGL 4.1 core-profile context (Apple stopped at 4.1). The library was
written for compatibility-profile GL and GLES2, so `display.h` defines `FW_GL_CORE_PROFILE` on macOS
and redirects a set of `gl*` names to FreeWRL's own compatibility shim, `freex3d/src/lib/opengl/GLCoreCompat.c`
(e.g. `fw_core_glDrawArrays`, `fw_core_glDrawElements`, `fw_core_glLineWidth`, `fw_core_glBindTextureUnit`;
the redirects are the `#define glDrawArrays fw_core_glDrawArrays` block in `freex3d/src/lib/display.h`).

### Distinct GL Entry Points
**Total: 120 distinct GL entry points, called from 42 source files across all of `freex3d/src/lib`, in
about 1,550 call sites.** Only 76 of them occur in `opengl/`; 44 occur only outside it.

Method:
- Quick raw count (includes comments, headers and shader text, so it over-counts):
  `rg -o --no-filename -t c '\bgl[A-Z]\w*\s*\(' freex3d/src/lib | sed -E 's/[[:space:]]*\($//' | sort -u | wc -l` → 160.
- Filtered count (the 120): the same regex `(?<![\w.>])gl[A-Z]\w*\s*\(` run over every `.c`/`.cpp` file
  under `freex3d/src/lib` after removing C comments, string literals (so the GLSL in
  `Compositing_Shaders.c` is not counted) and `#if 0` blocks; `glX*`/`glew*` are dropped. Wrapper
  macros defined in `display.h` whose body is a direct `gl*` call are mapped to that call and counted
  where they are used: `FW_GL_*` (e.g. `FW_GL_TEXPARAMETERI` → `glTexParameteri`), `GLUNIFORM*`
  (→ `glUniform*`), and `CREATE_SHADER`/`SHADER_SOURCE`/`COMPILE_SHADER`/`ATTACH_SHADER`/
  `GET_SHADER_INFO`/`GET_UNIFORM`/`GET_ATTRIB`/`USE_SHADER`/... (→ `glCreateShader` etc.). Macros
  that call FreeWRL code instead (`FW_GL_BINDBUFFER` → `sendBindBufferToGPU`, the software matrix
  stack `FW_GL_PUSH_MATRIX` → `fw_glPushMatrix`, ...) are not counted as GL; the GL calls inside
  those functions are counted where they are written. `fw_core_gl*` definitions in `GLCoreCompat.c`
  are not counted separately (they are the same entry points).
- Not evaluated: `#ifdef` platform paths other than `#if 0`. The count is source-level, over all
  platform paths that still compile. 18 of the 120 are fixed-function names that only appear on
  non-core paths (`glBegin`, `glEnd`, `glVertex3d`, `glPushMatrix`, `glPopMatrix`, `glLoadIdentity`,
  `glLoadMatrixd`, `glRotatef`, `glTranslatef`, `glFogf`, `glFogfv`, `glFogi`, `glShadeModel`,
  `glPushAttrib`, `glPopAttrib`, `glRasterPos2i`, `glWindowPos2i`, `glDrawPixels`), e.g. under
  `#if defined(FW_GL_CORE_PROFILE) || defined(GL_ES_VERSION_2_0)` in `Component_HAnim.c` (`IGL`
  macro) or debug-only code in `Component_Geometry3D.c`. **About 102 are live on a core profile.**

Per directory (distinct entry points used in that directory; a name can count in several):

| Directory | Distinct GL entry points | Files | Call sites |
|---|---|---|---|
| `opengl/` | 76 | 7 | ~450 |
| `scenegraph/` | 71 | 23 | ~730 |
| `ui/` | 42 | 5 | 176 |
| `main/` | 34 | 2 | 110 |
| `x3d_parser/` | 8 | 1 | 40 |
| lib root (`display.c`) | 7 | 1 | 32 |
| `input/` | 5 | 1 | 10 |
| `world_script/` | 1 | 1 | 1 |
| `opencl/` | 1 | 1 | 1 |

Top files by distinct entry points (call sites in brackets):

| File | Distinct | Notes |
|---|---|---|
| `opengl/OpenGL_Utils.c` | 43 (317) | shader build `makeAndCompileShader`, context setup `fwl_initialize_GL` |
| `ui/statusbarHud.c` | 34 (101) | HUD: own GLSL program `esLoadProgram`/`init_ProgramObject`, `printString3`, `renderButtons` |
| `scenegraph/Component_VolumeRendering.c` | 34 (206) | FBO in `render_volumestyle`, `render_GENERIC_volume_data` |
| `main/MainLoop.c` | 32 (104) | stage FBOs `pushnset_framebuffer`, `new_contenttype_stagefbo`, `stage_resize` |
| `opengl/GLCoreCompat.c` | 31 (54) | core-profile shim, client-array streaming `upload_client_attribs` |
| `scenegraph/Component_Lighting.c` | 30 (82) | shadow maps `make_depth_buffer`, `make_depth_buffer_cube`, `generate_shadowmap_2D`, `generate_shadowmap_cube` |
| `ui/CursorDraw.c` | 19 (71) | `cursorDraw`, `fiducialDraw`, `line_draw` |
| `scenegraph/Component_Text.c` | 18 (110) | own GLSL program `initProgramObject`, `render_screentext0`, `dug9gui_DrawImage` |
| `scenegraph/Component_Texturing.c` | 17 (24) | `render_GeneratedTexture` FBO |
| `scenegraph/Component_HAnim.c` | 15 (68) | SSBO upload in `child_HAnimHumanoid`, `sendSkinningInfo` |
| `opengl/RenderTextures.c` | 13 (51) | `compile_checkerboard_texture2D`, `compile_checkerboard_textureCube` |
| `scenegraph/Component_CubeMapTexturing.c` | 12 (40) | `compile_GeneratedCubeMapTexture` FBO |

The 44 entry points that never appear in `opengl/` include all renderbuffer/framebuffer-attachment
calls (`glGenFramebuffers`, `glFramebufferTexture2D`, `glGenRenderbuffers`, `glRenderbufferStorage`,
`glFramebufferRenderbuffer`, `glReadBuffer`, `glDrawBuffer`), state calls (`glViewport`, `glCullFace`,
`glFrontFace`, `glColorMask`, `glDepthMask`), readback (`glReadPixels`, `glGetTexImage`), SSBO calls
(`glBindBufferBase`, `glMapBuffer`, `glUnmapBuffer`) and `glGenerateMipmap`. So an abstraction that
only covers `opengl/` would miss most FBO, readback and pipeline-state traffic.

### VBO Streaming & FBO
- Geometry VBOs: `glGenBuffers`/`glBufferData` in `Polyrep.c` `compile_polyrep`/`render_polyrep` and
  `StreamPoly.c` `stream_polyrep`; attribute binding goes through `FW_GL_*_POINTER` →
  `RenderFuncs.c` `sendAttribToGPU` and `FW_GL_BINDBUFFER` → `RenderFuncs.c` `sendBindBufferToGPU`;
  draws in `RenderFuncs.c` `reallyDrawOnce`.
- Client-memory vertex arrays (HUD, Text, cursor, Box, lines, points, 2D geometry, particles) are
  streamed into buffer objects at draw time by `GLCoreCompat.c` `upload_client_attribs`, called from
  `fw_core_glDrawArrays`/`fw_core_glDrawElements`; batches end in `fw_core_glEndDrawBatch`
  (called from `RenderFuncs.c` `clearDraw` and the direct-draw paths).
- FBOs (`glGenFramebuffers`/`glBindFramebuffer`): shadow maps `Component_Lighting.c`
  `make_depth_buffer`, `make_depth_buffer_cube`; generated cube maps
  `Component_CubeMapTexturing.c` `compile_GeneratedCubeMapTexture`; `Component_Texturing.c`
  `render_GeneratedTexture`; volume rendering `Component_VolumeRendering.c` `render_volumestyle`;
  layering stages `MainLoop.c` `pushnset_framebuffer`, `popnset_framebuffer`,
  `new_contenttype_stagefbo`, `stage_resize`.

### Shaders and Uniforms
**How programs are built.** There is no fixed program list. A shape asks for a program with a
`shaderflagsstruct` (`scenegraph/Component_Shape.h`: `base` bitmask, `effects`, `usershaders`,
`volume`, `depth`, `debug`), e.g. `Component_Shape.c` `child_Shape` → `getMyShaders`.
`OpenGL_Utils.c` `getMyShaders` looks the flags up in the per-instance cache
`ppOpenGL_Utils->myShaderTable` and, on a miss, `makeAndCompileShader` → `getSpecificShaderSource`
dispatches to one of four builders in `Compositing_Shaders.c`:
- `getSpecificShaderSourceCastlePlugs` (the ubershader, normal shapes),
- `getSpecificShaderSourceVolume` (volume rendering),
- `getSpecificShaderSourceDepth` (shadow depth pass),
- `getSpecificShaderSourceDebug` (debug quads),

or, for X3D user shaders (`ComposedShader`/`ProgramShader`, `Component_ProgrammableShaders.c`
`thread_compile_ComposedShader`, `thread_compile_ProgramShader`), to the older
`OpenGL_Utils.c` `getSpecificShaderSourceOriginal`. `ui/statusbarHud.c` (`esLoadProgram`,
`init_ProgramObject`) and `scenegraph/Component_Text.c` (`initProgramObject`) compile two more
standalone programs of their own.

The ubershader builder copies the generic templates (`getGenericVertex`/`getGenericFragment` →
`genericVertexGLES2`/`genericFragmentGLES2`), prepends a `#version` chosen at runtime from
`GL_SHADING_LANGUAGE_VERSION` (`get_GLSL_max_version`), inserts `#define`s for the requested flags
(`AddDefine`, 72 call sites, 44 distinct define names) and splices in "plug" snippets (`Plug`,
`EnableEffects`).

Counts (`opengl/Compositing_Shaders.c` unless noted):
- **Source templates:** 17 whole-shader templates (`genericVertexGLES2`, `genericFragmentGLES2`,
  `genericFragmentCube`, `volumeVertexGLES2`, `volumeFragmentGLES2`, `volumeBlendedFragmentGLES2`,
  `vertexDepth`, `vertexDepthParticle`, `fragDepth`, and 8 debug-quad shaders `vertexQuad` ...
  `fragmentQuadDepthCubeTee`) plus 25 `plug_*` snippet strings (lighting, fog, clip planes,
  texturing, 11 volume styles `plug_voxel_*`, ...). `OpenGL_Utils.c` holds about 40 more fragment
  strings for `getSpecificShaderSourceOriginal` (`vertPosDec`, `ADSLLightModel`, ...).
  Command: `rg -n '^(static )?(const )?(GLchar|char)\s*\*\s*\w+\s*=\s*"' freex3d/src/lib/opengl/Compositing_Shaders.c`.
- **Variant count is combinatorial, not a list.** The `base` mask has 34 flag bits
  (`NO_APPEARANCE_SHADER` 0x1 … `DISPLACER_SHADER` 0x200000000 in `Component_Shape.h`), of which
  29 are tested by `getSpecificShaderSourceCastlePlugs` (`DESIRE(whichOne.base, …)`); `volume`
  adds 4 data bits and 11 style values, and `effects`/`usershaders` add per-scene user code. Only
  the combinations a loaded world actually uses are compiled, lazily, so the number of programs
  depends on the scene (not measured here; Phase 2 logs it). The `#ifdef` surface inside the shader text: 126 lines matching
  `rg -c '^\s*#\s*if(def|ndef)?\b.*\\n' freex3d/src/lib/opengl/Compositing_Shaders.c`.
- **Uniforms:** 170 `uniform` declarations (113 distinct names, e.g. `fw_ModelViewMatrix`,
  `fw_ProjectionMatrix`) inside the shader strings of `Compositing_Shaders.c`; 49 (45 distinct) in
  `OpenGL_Utils.c`; 5 in `Component_Text.c` `vShaderStr`/fragment string; 2 in `statusbarHud.c`.
  Counted inside C string literals only, GLSL comments removed. All are plain default-block uniforms
  set one at a time with `glUniform*` / `GLUNIFORM*`.
- **Uniform blocks (UBOs): 0.** No `uniform Name { … }` block exists in any shader string. The only
  `GL_UNIFORM_BUFFER` code (a std140 `struct Lightbuf` upload in `Component_Lighting.c`
  `compile_SpotLight`) is commented out.
- **SSBOs: 6**, all in the `#ifdef SKINNING` section of `genericVertexGLES2`: `layout(std430,
  binding = 10..15)` blocks `BufferBlock1` (`PVW` skin weights), `BufferBlock2` (`PVI` joint
  indices), `BufferObject1` (`JT` joint matrices), `BufferObject2` (`JN` normal matrices),
  `BufferBlock3`/`BufferBlock4` (`dindex`/`displace`, under `#ifdef DISPLACER`). The CPU side binds
  them with `glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 10..15, …)` in `Component_HAnim.c`
  `child_HAnimHumanoid` and `sendSkinningInfo`. On macOS this path is off:
  `Component_HAnim.c` `vertexTransformMethod` returns CPU when `display.c` `rdr_caps_av_ssbo()` is
  false, which it always is on 4.1.

### HUD
- `ui/statusbarHud.c` (`printString3`, `renderButtons`, `statusbarHud_DrawCursor`) and
  `ui/CursorDraw.c` (`cursorDraw`, `fiducialDraw`) draw from client memory with
  `glDrawElements`/`glDrawArrays` and close their batches explicitly with `fw_core_glEndDrawBatch()`.
  The HUD uses its own program (`statusbarHud.c` `init_ProgramObject`); the cursor uses ubershader
  variants via `getMyShader(NO_APPEARANCE_SHADER)`/`getMyShader(ONE_TEX_APPEARANCE_SHADER)`.

## 2. Options

### A. ANGLE (GLES-to-Metal)
- **Concept**: Link Google's ANGLE and run the renderer on its Metal backend.
- **Trade-offs**: ANGLE exposes **OpenGL ES** (ES 2.0/3.0, with ES 3.1+ coverage depending on the
  backend) and **GLSL ES**, not desktop GL 4.1. It is not a drop-in under the current code:
  - GL calls: the desktop-only entry points in the inventory need replacements or removal, e.g.
    `glGetTexImage` (`Component_CubeMapTexturing.c` `render_ComposedCubeMapTexture`),
    `glMapBuffer` (→ `glMapBufferRange`; `Component_HAnim.c` `child_HAnimHumanoid`),
    `glGetBufferSubData` (`GLCoreCompat.c` `fw_core_glDrawElements`), `glDrawBuffer` (→
    `glDrawBuffers`; `Component_Lighting.c` `make_depth_buffer`), `glPointSize` (→ `gl_PointSize`;
    `OpenGL_Utils.c` `sendMaterialsToShader`), `glGetDoublev`, the 18 fixed-function names; and
    `GLCoreCompat.c`'s 4.5 shims would have to be re-done for ES.
  - Shaders: every template is GLSL with a runtime `#version` (`get_GLSL_max_version`); the depth
    and debug shaders are hard-coded `#version 330 core`; ES needs `#version 300 es`, precision
    qualifiers and no `layout(std430)` SSBOs below ES 3.1. The ubershader still has GLES2-era
    branches (`MOBILE`, `genericVertexGLES2`), but they are from the retired Android build and
    untested.
  - Context creation in the Cocoa frontend (`FWGLView.m`) and the SDL3 scaffold moves to EGL.
  - SSBO/GPU skinning would need ES 3.1 on ANGLE-Metal; wide lines are not solved (ES has no wide
    lines either).
- **Cost/risk**: medium. Effectively a GLES port of ~100 live entry points and all shaders, plus a
  large new binary dependency to build, sign and ship. Gains little over Option B beyond escaping
  Apple's deprecated framework.

### B. Apple's GL-on-Metal as today (Baseline)
- **Concept**: Keep rendering through Apple's system OpenGL framework (`OpenGL.framework`), which
  Apple implements on top of Metal ("4.1 Metal" in `GL_VERSION`). FreeWRL's own core-profile shim
  `GLCoreCompat.c` stays in place to make the compatibility-era renderer run on that 4.1 core context.
  (A MoltenGL-style commercial translator would be the same shape with a different vendor.)
- **Trade-offs**: No new work. Deprecated by Apple, capped at 4.1: no SSBOs (so GPU HAnim skinning
  stays off, `Component_HAnim.c` `vertexTransformMethod`) and 1-pixel lines
  (`GLCoreCompat.c` `fw_core_glLineWidth` clamps any width to 1 on the forward-compatible context).
  Risk is Apple removing the framework, with no date announced.

### C. Native Metal Abstraction
- **Concept**: Build an internal `fw_renderer_...` abstraction with a GL backend and a Metal backend.
  Shaders are translated from GLSL to MSL via `glslang` (GLSL → SPIR-V) and `SPIRV-Cross`
  (SPIR-V → MSL).
- **What the abstraction must cover**: the whole 120-entry-point surface above, not just `opengl/`:
  buffers/attributes (`RenderFuncs.c`, `Polyrep.c`, `StreamPoly.c`), textures (`Textures.c`,
  `RenderTextures.c`, `LoadTextures.c`), FBOs and readback (`MainLoop.c`, `Component_Lighting.c`,
  `Component_CubeMapTexturing.c`, `Component_Texturing.c`, `Component_VolumeRendering.c`),
  pipeline state (blend/depth/cull/color mask, scattered through `scenegraph/`), the HUD and Text
  programs, and per-draw uniforms (141 distinct names across `Compositing_Shaders.c` and
  `OpenGL_Utils.c`). Metal has no
  default-block uniforms, so per-draw uniforms must be packed into argument/constant buffers.
- **Shaders**: programs are assembled at runtime from flags (above), so either translate each new
  flag combination at runtime (link glslang + SPIRV-Cross into the app) or enumerate and precompile
  the combinations actually used (test corpus) with a runtime fallback. X3D user shaders
  (`Component_ProgrammableShaders.c`) are authored GLSL and can only be translated at runtime.
- **Trade-offs**: High risk/cost. Total control and access to compute/storage buffers, but two
  backends to maintain.

### D. SDL3 GPU API
- **Concept**: Port the renderer to the SDL3 GPU API (Metal on macOS, Vulkan on Linux, D3D12 on
  Windows). The existing scaffold `freex3d/src/sdl3/FreeWRL_SDL3.c` is only an SDL3 **window and
  OpenGL 4.1 core context** (`SDL_GL_SetAttribute` in its setup); it does not use the SDL GPU API
  yet. It would be the natural host for a GPU-API backend.
- **Trade-offs**: SDL GPU provides command buffers, pipelines and compute (storage buffers), so GPU
  skinning becomes possible. It requires moving FreeWRL from a state machine to pre-built pipeline
  objects (one per shader variant × blend/depth/cull state), and its shaders are SPIR-V/MSL/DXIL, so
  the same GLSL → SPIR-V → MSL toolchain as Option C (or SDL_shadercross) is needed. Medium-to-high
  rewrite effort, best long-term multi-platform outcome. It has no wide lines either.

## 3. Metal Benefits and Risks

### Benefits (What Metal gives back)
- **GPU HAnim Skinning**: Metal (and SDL GPU) have storage buffers and compute, so the existing SSBO
  design (6 std430 blocks at bindings 10–15 in `genericVertexGLES2`, uploaded by
  `Component_HAnim.c` `child_HAnimHumanoid`) maps onto Metal buffers; today it is off on macOS
  (`vertexTransformMethod`).
- **Wide Lines**: not given back. Metal has no line-width state (lines rasterize 1 pixel wide), and
  neither does the SDL3 GPU API. Line widths > 1 (`Component_Shape.c` `render_LineProperties`,
  `Component_ParticleSystems.c` `render_geom_particle`, `CursorDraw.c` `line_draw`) need
  emulation — expand each segment to a screen-space quad (two triangles) in a vertex shader,
  instancing pass, or compute — in **every** option, including staying on GL 4.1 core.
- **Performance/Modernization**: removes Apple's deprecated GL layer and the client-array streaming
  in `GLCoreCompat.c` `upload_client_attribs`; enables explicit command buffers and multithreaded
  encoding.

### Risks
- **Linux GL Path**: Linux must keep the GL path (or migrate to SDL3 Vulkan). Two backends risks
  dual maintenance.
- **`pp<File>` Multi-instance rule**: Module state lives in per-instance private structs reached via
  `gglobal()` (`iglobal.c` `gglobal`, current instance set with `pthread_setspecific` in
  `fwl_setCurrentHandle`). The shader cache is already per instance (`ppOpenGL_Utils->myShaderTable`);
  any new backend objects (device, pipeline cache, command queue) must follow the same rule.
- **Visual Testing**: `tools/visual-test/compare.sh` is a **local harness**, not a CI workflow: it
  renders worlds in FreeWRL and in X_ITE and scores them by normalized cross-correlation (default
  threshold 0.90). It runs on a developer machine. Metal rasterization differences may shift
  scores; a GL-vs-Metal FreeWRL comparison mode would be a useful addition. The macOS CI workflow
  `.github/workflows/macos.yml` builds, packages and runs `tools/macos-ci/` checks; it does not run
  the visual diff.
- **Packaging/Signing Impact**: new dylibs (SPIRV-Cross, glslang, ANGLE or SDL3 in the app bundle)
  must be built by `tools/macos-deps/build.sh`, copied and signed by `tools/macos-package/package.sh`
  (hardened runtime `-r`, notarization `-n`).

## 4. Phased Recommendation

To minimize risk and enable independent verification, the transition to the **SDL3 GPU API**
(Option D) is recommended over a raw Metal abstraction.

**Phase 1a: Renderer abstraction, `opengl/` and draw path (Linux testable)**
- Introduce `fw_render_*` for the 76 entry points used in `opengl/` plus the draw/attribute path in
  `scenegraph/RenderFuncs.c` (`sendAttribToGPU`, `sendBindBufferToGPU`, `reallyDrawOnce`),
  `Polyrep.c` and `StreamPoly.c`. GL backend only.
- *Verification*: Linux and macOS builds; `tools/visual-test/compare.sh` run locally shows no
  regressions; `rg` for raw `gl[A-Z]` calls in the converted files returns nothing.

**Phase 1b: FBO, readback and state (Linux testable)**
- Move the 44 entry points that live outside `opengl/` (framebuffers/renderbuffers, `glReadPixels`,
  `glGetTexImage`, viewport/cull/color-mask state) in `MainLoop.c`, `Component_Lighting.c`,
  `Component_CubeMapTexturing.c`, `Component_Texturing.c`, `Component_VolumeRendering.c`,
  `Component_TextureProjector.c`, `display.c` behind the interface. Split per component if a PR gets
  too large.
- *Verification*: shadow, cube-map, generated-texture, volume and layering worlds via the local
  visual harness; re-run the inventory command, which should report only the GL backend files.

**Phase 1c: HUD, Text and cursor (Linux testable)**
- Convert `ui/statusbarHud.c`, `ui/CursorDraw.c`, `scenegraph/Component_Text.c` (including their
  standalone programs) and remove the 18 fixed-function paths or confine them to the GL backend.
- *Verification*: HUD/Text worlds; macOS harness `tools/macos-ci/`.

**Phase 2: Shader toolchain (Linux testable)**
- Integrate `glslang` and `SPIRV-Cross`. Make `Compositing_Shaders.c` output compile to SPIR-V for
  every flag combination exercised by `freewrl/tests` (logging `shaderflagsstruct` values from
  `getMyShaders` gives the list); replace default-block uniforms with uniform blocks first, still on GL.
- *Verification*: all logged variants compile to SPIR-V and MSL on Linux; GL rendering unchanged.

**Phase 3: SDL3 GPU backend (macOS focus)**
- Implement `fw_render_*` with the SDL3 GPU API in the `FreeWRL_SDL3.c` frontend (currently a GL
  context only).
- *Verification*: boot `freewrl_sdl3` on macOS (`tools/macos-ci/sdl3-scaffold.sh`) and match the
  local visual harness.

**Phase 4: Unlock limits (macOS/Linux)**
- GPU HAnim skinning on SDL3 storage buffers (the six existing SSBO bindings).
- Wide lines by quad expansion. This can be done on the GL path first (Linux testable) since no
  option renders wide lines natively.
- *Verification*: HAnim performance test (`hanim_skin.x3d`) and a line-width visual test.

### Open Questions for the Owner
- Is transitioning entirely to SDL3 GPU (deprecating direct OpenGL on Linux eventually) acceptable,
  or must the legacy GL 4.1 path be maintained alongside SDL3 GPU indefinitely?
- Does the dynamic string concatenation in `Compositing_Shaders.c` have to remain dynamic at
  runtime, or can we pre-compile the permutations offline (with a runtime fallback for X3D user
  shaders, which can only be translated at runtime)?
- Are we comfortable adding `glslang` and `SPIRV-Cross` to the macOS dependency build
  (`tools/macos-deps/build.sh`) and the app bundle (`tools/macos-package/package.sh`)?
- Should wide-line emulation be done now on the GL path, independent of the backend decision?
