# Metal Backend Decision Document

## 1. OpenGL Surface Inventory
The current OpenGL surface used on macOS is restricted to OpenGL 4.1 core, as Apple stopped updating OpenGL and deprecated it. FreeWRL routes these calls through a compatibility layer.

### Distinct GL Entry Points
A survey of `freex3d/src/lib/opengl/*.c` identifies 72 standard OpenGL entry points used in the renderer (excluding internal aliases like `fw_core_...`). Key files handling these are:
- `GLCoreCompat.c`: Overrides core functionality to manage state and track bound attributes (e.g. `fw_core_glVertexAttribPointer`, `fw_core_glBindTextureUnit`, `fw_core_glEndDrawBatch`).
- `OpenGL_Utils.c`: Includes fallback fixed-function emulation routines, matrix management, and `glCreateProgram` calls.
- `RenderTextures.c` / `LoadTextures.c` / `Textures.c`: Handle texture creation (`glGenTextures`), binding, and framebuffers (`glGenFramebuffers` mapped across scenegraph components like `Component_CubeMapTexturing.c`).

### VBO Streaming & FBO
- VBO streaming heavily relies on `glGenBuffers`, `glBindBuffer` (with `GL_ARRAY_BUFFER` and `GL_ELEMENT_ARRAY_BUFFER`), and `glBufferData`.
- Scene components frequently allocate FBOs (`glGenFramebuffers`) for cube maps, texture projectors, and shadow maps (e.g., `freex3d/src/lib/scenegraph/Component_VolumeRendering.c`).

### Shaders and Uniforms
- `Compositing_Shaders.c`: Contains the monolithic "ubershader" generator strings.
- Employs approx 128 `#ifdef` blocks and 174 uniform definitions (e.g., `fw_ModelViewMatrix`, `fw_LightSource`).
- Features a heavily parameterized design dynamically plugging in string chunks (e.g., `shaderPrintf`, `plug_fragment_texture_apply`).

### HUD
- Engine UI rendered through `freex3d/src/lib/ui/statusbarHud.c` and `CursorDraw.c`, which utilize `glDrawElements`/`glDrawArrays` and close their batches explicitly with `fw_core_glEndDrawBatch()`.

## 2. Options

### A. ANGLE (GLES/GL-to-Metal)
- **Concept**: Drop in Google's ANGLE library underneath the existing OpenGL 4.1 code.
- **Trade-offs**: Extremely low effort for the core engine code. However, ANGLE emulates GLES, which might restrict features like Compute Shaders (SSBOs) depending on the exact version targeted (GLES 3.1+ required for Compute), and might not neatly sidestep the wide-line limitation natively.

### B. MoltenGL-style / GL-on-Metal (Baseline)
- **Concept**: Maintain the current architecture where Apple’s `GLCoreCompat` layer internally translates OpenGL 4.1 to Metal.
- **Trade-offs**: Deprecated by Apple. Dead ends at OpenGL 4.1, permanently locking out GPU HAnim skinning (needs GL 4.3 SSBOs) and wide lines (clamped to 1px).

### C. Native Metal Abstraction
- **Concept**: Build an internal `fw_renderer_...` abstraction. The Metal backend implements this abstraction. Shaders are translated from GLSL to MSL via `glslang` and `SPIRV-Cross`.
- **Trade-offs**: High risk/cost. Translating the highly dynamic `#ifdef`-heavy `Compositing_Shaders.c` string generator to ahead-of-time (or just-in-time) SPIR-V compilation is complex. It gives total control but introduces huge maintenance overhead.

### D. SDL3 GPU API
- **Concept**: Use the SDL3 GPU API scaffold (`freex3d/src/sdl3/FreeWRL_SDL3.c`) already present in the repo.
- **Trade-offs**: SDL3 GPU abstracts Metal (macOS), Vulkan (Linux/Win), and D3D12. It provides modern graphics and compute capabilities out of the box. It requires adapting FreeWRL's renderer to a modern Command Buffer / Pipeline layout rather than a state-machine layout, representing a medium-to-high rewrite effort but offering the best long-term multi-platform solution.

## 3. Metal Benefits and Risks

### Benefits (What Metal gives back)
- **GPU HAnim Skinning**: Access to Compute Shaders or native Shader Storage Buffer Objects (`GL_SHADER_STORAGE_BUFFER`), bypassing the OpenGL 4.3 requirement (currently unavailable under Apple's 4.1 ceiling).
- **Wide Lines**: By utilizing Metal graphics pipelines, FreeWRL can natively render or emulate wide lines, bypassing the forward-compatible GL 4.1 1-pixel limit.
- **Performance/Modernization**: Removes the deprecated GL layer overhead entirely.

### Risks
- **Linux GL Path**: Linux must keep the GL path (or migrate to SDL3 Vulkan). Branching the renderer risks dual-maintenance.
- **`pp<File>` Multi-instance rule**: The engine uses global state context per-thread via `pthread_setspecific` in `iglobal.c` (accessed via `gglobal()`). A modern backend must be strictly careful not to bleed state across contexts or instances.
- **Visual Testing**: The CI workflow (`tools/visual-test/compare.sh`) relies on matching pixels. Metal rasterization differences might slightly alter pixels, requiring baseline updates.
- **Packaging/Signing Impact**: Transitioning from Apple's framework to SDL3 GPU or native Metal requires updating `tools/macos-package/package.sh` for any new binary dependencies (e.g., SPIRV-Cross, glslang) and maintaining Developer ID signing (`-r`).

## 4. Phased Recommendation

To minimize risk and enable independent verification, the transition to the **SDL3 GPU API** (Option D) is recommended over a raw Metal abstraction.

**Phase 1: Renderer Abstraction (Linux Testable)**
- Extract the 72 distinct GL calls inside `freex3d/src/lib/opengl/*.c` into a pure abstract interface (e.g. `fw_render_bind_buffer()`).
- Point the GL backend to this interface.
- *Verification*: `tools/visual-test/compare.sh` on Linux/macOS passes (no regressions).

**Phase 2: Shader Toolchain (Linux Testable)**
- Integrate `glslang` and `SPIRV-Cross` into the build toolchain.
- Refactor `Compositing_Shaders.c` so its dynamically assembled strings can be compiled into SPIR-V.
- *Verification*: Output SPIR-V blobs compile successfully on Linux.

**Phase 3: SDL3 GPU Backend (macOS focus)**
- Implement the abstracted `fw_render_*` interface using the SDL3 GPU API within the existing `FreeWRL_SDL3.c` scaffold.
- Load the SPIR-V/MSL translated shaders.
- *Verification*: Boot the SDL3 scaffold on macOS and match the visual test suite.

**Phase 4: Unlock Limits (macOS/Linux)**
- Move HAnim CPU skinning to GPU using SDL3 Compute pipelines (SSBO equivalent).
- Implement wide-line rendering in the new pipeline.
- *Verification*: HAnim performance test and line width visual test.

### Open Questions for the Owner
- Is transitioning entirely to SDL3 GPU (deprecating direct OpenGL on Linux eventually) acceptable, or must the legacy GL 4.1 path be maintained alongside SDL3 GPU indefinitely?
- Does the dynamic string concatenation in `Compositing_Shaders.c` have to remain dynamic at runtime, or can we pre-compile the permutations offline?
- Are we comfortable adding `glslang` and `SPIRV-Cross` to the macOS packaging script (`tools/macos-deps/build.sh`)?
