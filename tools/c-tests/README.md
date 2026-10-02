# Host-only C tests

Small C17 tests that compile real FreeWRL library sources into a plain command-line
program. They never start FreeWRL, create an NSApplication or OpenGL context, play
audio or load a world, so they are safe to run locally and take a few seconds.

```sh
tools/c-tests/run-containers.sh                  # routine run, also in CI (build job)
tools/c-tests/run-containers.sh --known-defects  # plus the reproducers in known_defects/
tools/c-tests/run-bounds.sh                      # bounds and data-safety tests (Linux and macOS)
```

## Containers

`run-containers.sh` compiles `freex3d/src/lib/scenegraph/Vector.c` and
`freex3d/src/lib/list.c` unchanged, with the Mac app's `config.h`
(`OSX_gui/FreeWRL-Desktop/FreeWRL/config.h`), so the allocator macros resolve to
`malloc`/`realloc`/`calloc`/`free` and `ASSERT` compiles to nothing, as in the shipped
app. The tests link against those objects; nothing is reimplemented.

- `test_vector.c`: Vector and Stack construction, growth, get/set/back, pop, element
  removal (first, middle, last, invalid), clear, shrink, releaseData, delete, testVector.
- `test_list.c`: singly linked `s_list_t`, the `ml_enqueue`/`ml_dequeue` queue (FIFO:
  enqueue at the head, dequeue from the tail), payload-freeing deletes
  (`ml_delete2`, `ml_delete_all2`, `cdl_delete2`, `cdl_delete_all2`), and the circular
  doubly linked `cd_list_t`.

The tests record current behavior, including quirks (for example `ml_delete` cannot
remove the head, and `ml_insert` before a non-head item returns the item, not the list).
A change in behavior should be a deliberate change to the test.

Vector pointer lifetime: a pointer from `vector_get_ptr` or `stack_top_ptr` is valid only
until the next operation that may reallocate `Vector.data` (a push that grows, shrink,
releaseData, clear, testVector, delete). Whether a reallocation moves the block is up
to the allocator, so the tests read values back through a fresh lookup and never compare
addresses.

## Bounds and data safety

`run-bounds.sh` tests library functions that cannot be compiled on their own, because
their source files need OpenGL, the scene graph and the global state. `extract.awk`
copies each function unchanged out of the real source file, and each test file
declares only the types and test doubles that the function uses. If a function is
renamed or removed, the extraction fails and the run stops. It does not use a
`config.h`, so it runs on Linux and macOS (`CC` defaults to `cc`).

- `test_hanim.c`: `parse_float_values` (`Component_HAnim.c`): spaces, commas, tabs,
  newlines, negative and decimal values, malformed tokens and missing values (0.0),
  a last token without a separator, a 200-character token, a count below 1.
- `test_texture.c`: the GeneratedTexture blank texture (`LoadTextures.c`): the empty
  default size, one value, zero, negative and overflowing sizes are rejected with no
  allocation; valid sizes give black opaque pixels.
- `test_shader_plug.c`: shader PLUG compositing (`Compositing_Shaders.c`): plug names,
  parameter lists, plugs and shader parts longer than the old fixed buffers, malformed
  `void PLUG_` declarations and `/* PLUG: */` points, `AddDefine0`, `AddVersion0`,
  `AddExtension`. Results are compared with the exact expected text.
- `test_eai_reply.c`: the EAI GETNODEPARENTS reply (`EAIEventsIn.c`) with
  `outBufferCat` (`EAIHelpers.c`): no parents, errors, widest handles, replies larger
  than the old 8192-byte buffer, allocation failures.
- `test_tempfile.c`: `fw_temp_file_create` and `fw_temp_dir_create` (`io_files.c`):
  mode 0600 files and 0700 directories, unique names, `$TMPDIR` order, failures that
  leave no file.
- `test_pick_ray.c`: the picking-pass ray stack, `push_ray` and `pop_ray`
  (`RenderFuncs.c`), with the real `Vector.c` functions and `Vector.h` stack macros:
  each pop restores the parent's ray, the outermost pop does not read below the stack,
  100 levels through reallocation, a pop with nothing pushed.
- `test_sensor_lifetime.c`: pointing-device sensors freed with their world:
  `setSensitive`, `unRegisterSensitiveNode`, `freeContainerNode` and `sendSensorEvents`
  (`MainLoop.c`) with `gc_broto_instance` (`CParseParser.c`). A world replaced while its
  PROTO SphereSensor is hovered and pressed, PROTO declarations, an Inline unload that
  keeps the other sensors working, one node of several unregistered, the scene root freed
  apart from its nodes on world replacement (`ProdCon.c`, and at exit) while a touch holds
  it, the Group that holds EAI-created nodes freed after they moved. The `do_*Sensor`
  doubles read the sensor node, so a stale call is an AddressSanitizer heap-use-after-free.

## Sanitizers

The test binaries (and, for `run-containers.sh`, the two production objects) are built with
`-fsanitize=address,undefined -fno-sanitize-recover=all`; any report fails the run.
This applies only to the test programs, not to the FreeWRL build. LeakSanitizer is not
available with Apple clang on arm64 macOS, so there leaks are not checked; on Linux it
runs as part of AddressSanitizer.

## Known defects

`known_defects/` holds reproducers for behavior that looks wrong and has not been fixed.
They are not part of the routine run. Each exits 42 when its defect reproduces normally
and 0 once it no longer does (then review and retire it); `--known-defects` reports
either. Any other status, such as a sanitizer report, crash or signal, is an unexpected
failure and makes the command exit nonzero.

- `cdl_insert.c`: `cdl_insert` into a non-empty circular list corrupts the forward links
  (the new item is never reachable going forward, and walking the ring from the head
  can loop forever). `cd_list_t` has no callers in the engine.
