#!/bin/bash
# live-input.sh APP OUTDIR [--require-access] [--sessions main,quit-q,quit-cmdq,stringsensor]
# Native macOS real-input baseline (CGEventPost through fwinput.swift; see live_input.py).
# Test tooling only: nothing here ships in FreeWRL.app. Starts one FreeWRL at a time.
exec python3 "$(cd "$(dirname "$0")" && pwd)/live_input.py" "$@"
