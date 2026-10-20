#!/bin/bash
cd freex3d
make clean
./configure --with-target=x11 --with-javascript=duk CFLAGS='-O1 -g -fsanitize=address' LDFLAGS='-fsanitize=address'
make -j$(nproc)
ASAN_OPTIONS=detect_leaks=1 timeout 5 xvfb-run -a src/bin/freewrl ../freewrl/tests/1.wrl
ASAN_OPTIONS=detect_leaks=1 timeout 5 xvfb-run -a src/bin/freewrl ../freewrl/tests/2.wrl
ASAN_OPTIONS=detect_leaks=1 timeout 5 xvfb-run -a src/bin/freewrl ../freewrl/tests/3.wrl
ASAN_OPTIONS=detect_leaks=1 timeout 5 xvfb-run -a src/bin/freewrl ../freewrl/tests/4.wrl
