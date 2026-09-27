# Host-only C tests

Small C17 tests that compile real FreeWRL library sources into a plain command-line
program. They never start FreeWRL, create an NSApplication or OpenGL context, play
audio or load a world, so they are safe to run locally and take a few seconds.

```sh
tools/c-tests/run-containers.sh                  # routine run, also in CI (build job)
tools/c-tests/run-containers.sh --known-defects  # plus the reproducers in known_defects/
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

## Sanitizers

The test binary and the two production objects it links are built with
`-fsanitize=address,undefined -fno-sanitize-recover=all`; any report fails the run.
This applies only to this test program, not to the FreeWRL build. LeakSanitizer is not
available with Apple clang on arm64 macOS, so leaks are not checked.

## Known defects

`known_defects/` holds reproducers for behavior that looks wrong and has not been fixed.
They are not part of the routine run. Each exits 42 when its defect reproduces normally
and 0 once it no longer does (then review and retire it); `--known-defects` reports
either. Any other status, such as a sanitizer report, crash or signal, is an unexpected
failure and makes the command exit nonzero.

- `cdl_insert.c`: `cdl_insert` into a non-empty circular list corrupts the forward links
  (the new item is never reachable going forward, and walking the ring from the head
  can loop forever). `cd_list_t` has no callers in the engine.
