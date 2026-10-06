#!/bin/sh
# Build the pinned SDL3 into a private prefix on Linux, for the later SDL platform layer.
# FreeWRL does not link SDL3 yet: the X11 frontend and the OpenGL renderer stay active.
# A system SDL3 package is never used; the pinned upstream release is the only source.
#
# usage: build.sh [-p prefix] [-c source-cache]
#   -p  install prefix                    (default: ./linux-deps-out/prefix)
#   -c  where the downloaded archive is kept (default: ./linux-deps-out/sources)
#
# The version, URL, SHA-256 and release commit are read from tools/macos-deps/build.sh
# (the SDL3 row and SDL3_COMMIT), so one file pins SDL3 for both platforms and for
# freex3d/CMakeLists.txt. The archive is checked against the SHA-256, and its REVISION.txt
# against the commit. Writes <prefix>/share/freewrl-deps/packages.tsv and the SDL3 license
# under <prefix>/share/freewrl-deps/licenses/SDL3/. Needs curl, sha256sum, CMake and a
# C compiler; uses Ninja when it is installed. SDL's configure stops when an X11 header it
# wants is missing (on Ubuntu 24.04 a FreeWRL build machine needs libxss-dev besides the
# X11 and GL headers FreeWRL uses). Then build FreeWRL's probe with
#   cmake -S freex3d -B build -G Ninja -DFREEWRL_SDL3_PROBE=ON -DCMAKE_PREFIX_PATH=<prefix>
set -eu
H=$(cd "$(dirname "$0")" && pwd)
PREFIX= CACHE=
while getopts "p:c:" opt; do
	case $opt in
	p) PREFIX=$OPTARG ;;
	c) CACHE=$OPTARG ;;
	*) sed -n '2,18p' "$0"; exit 2 ;;
	esac
done
PREFIX=${PREFIX:-linux-deps-out/prefix} CACHE=${CACHE:-linux-deps-out/sources}
for t in curl sha256sum cmake; do
	command -v $t > /dev/null || { echo "SDL3 needs $t" >&2; exit 1; }
done
case $(realpath -m "$PREFIX")/ in
/usr/*|/opt/*) echo "use a private prefix, not $PREFIX" >&2; exit 1 ;;
esac
mkdir -p "$PREFIX" "$CACHE"
PREFIX=$(cd "$PREFIX" && pwd) CACHE=$(cd "$CACHE" && pwd)
WORK=$(mktemp -d "${TMPDIR:-/tmp}/freewrl-linux-deps.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

PIN=$H/../macos-deps/build.sh
set -- $(sed -n 's/^SDL3 \([0-9.]* [^ ]* [0-9a-f]*\)$/\1/p' "$PIN")
[ $# -eq 3 ] || { echo "no SDL3 row in $PIN" >&2; exit 1; }
ver=$1 url=$2 sha=$3
SDL3_COMMIT=$(sed -n 's/^SDL3_COMMIT=\([0-9a-f]*\)$/\1/p' "$PIN")
[ ${#SDL3_COMMIT} -eq 40 ] || { echo "no SDL3_COMMIT in $PIN" >&2; exit 1; }
echo "== SDL3 $ver ($(uname -m))"

f=$CACHE/$(basename "$url")
[ -f "$f" ] || { curl -sSfL -o "$f.part" "$url" && mv "$f.part" "$f"; }
got=$(sha256sum "$f" | cut -d' ' -f1)
[ "$got" = "$sha" ] || { echo "$f: SHA-256 $got, expected $sha" >&2; exit 1; }
tar xf "$f" -C "$WORK"
cd "$WORK/SDL3-$ver"
rev=$(cat REVISION.txt)
case $rev in
"release-$ver-0-g"*) [ "${SDL3_COMMIT#"${rev##*-g}"}" != "$SDL3_COMMIT" ] ;;
*) false ;;
esac || { echo "SDL3: REVISION.txt says $rev, expected release-$ver at $SDL3_COMMIT" >&2; exit 1; }

# a shared library only (no static library, tests or examples), installed to <prefix>/lib;
# the prefix's CMake config and pkg-config files are what FreeWRL's build uses
gen=
command -v ninja > /dev/null && gen="-G Ninja"
log=$WORK/SDL3.log
cmake -S . -B build $gen -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PREFIX" \
	-DCMAKE_INSTALL_LIBDIR=lib -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TEST_LIBRARY=OFF \
	-DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF -DSDL_RPATH=OFF > "$log" 2>&1 || { tail -30 "$log"; exit 1; }
{ cmake --build build -j"$(nproc)" && cmake --install build; } >> "$log" 2>&1 || { tail -30 "$log"; echo "SDL3: build failed" >&2; exit 1; }

got=$(sed -n 's/^Version: //p' "$PREFIX/lib/pkgconfig/sdl3.pc")
[ "$got" = "$ver" ] || { echo "SDL3: installed version $got, expected $ver" >&2; exit 1; }
lib=$(readelf -d "$PREFIX/lib/libSDL3.so" | sed -n 's/.*(SONAME).*\[\(.*\)\]/\1/p')
[ -f "$PREFIX/lib/$lib" ] || { echo "SDL3: $PREFIX/lib/libSDL3.so has no SONAME" >&2; exit 1; }
echo "   SDL3 $got, $rev, $lib"

META=$PREFIX/share/freewrl-deps
rm -rf "$META"
mkdir -p "$META/licenses/SDL3"
cp LICENSE.txt "$META/licenses/SDL3/"
chmod 644 "$META/licenses/SDL3/LICENSE.txt"
printf 'package\tversion\tlibraries\tsource\tsha256\n' > "$META/packages.tsv"
printf '%s\t%s\t%s\t%s\t%s\n' SDL3 "$ver" "$lib" "$url" "$sha" >> "$META/packages.tsv"
echo "prefix: $PREFIX"
