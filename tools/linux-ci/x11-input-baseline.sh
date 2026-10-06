#!/bin/bash
# x11-input-baseline.sh BUILD OUTDIR [--sessions main,quit-q]
# Native Linux X11/GLX smoke and real-input baseline under Xvfb with xdotool and gdb (see
# x11_input_baseline.py). Test tooling only: xdotool, Xvfb and gdb are not FreeWRL dependencies.
exec python3 "$(cd "$(dirname "$0")" && pwd)/x11_input_baseline.py" "$@"
