#!/bin/sh
# Build the libraries FreeWRL.app embeds (FreeType, ODE, freealut) from source for an older
# macOS than the build machine's, into a private prefix. Homebrew's bottles target the macOS
# they were built on, so an app bundling them cannot run on anything older.
# Also builds SDL3 into the same prefix for the later SDL platform layer; FreeWRL does not
# link it yet, so package.sh does not embed it.
#
# usage: build.sh [-p prefix] [-t macos-version] [-c source-cache]
#   -p  install prefix                         (default: ./macos-deps-out/prefix)
#   -t  minimum macOS (MACOSX_DEPLOYMENT_TARGET) (default: 15.0)
#   -c  where downloaded sources are kept      (default: ./macos-deps-out/sources)
#
# Sources are the ones Homebrew's formulae use, checked against the same SHA-256; SDL3 is
# the upstream release archive, checked against its SHA-256 and the release commit.
# Writes <prefix>/share/freewrl-deps/packages.tsv (package, version, libraries, source URL,
# SHA-256) and each package's license files under <prefix>/share/freewrl-deps/licenses/,
# which tools/macos-package/bundle.py reads. Needs Xcode's command line tools, make and CMake.
set -eu
H=$(cd "$(dirname "$0")" && pwd)
PREFIX= TARGET=15.0 CACHE=
while getopts "p:t:c:" opt; do
	case $opt in
	p) PREFIX=$OPTARG ;;
	t) TARGET=$OPTARG ;;
	c) CACHE=$OPTARG ;;
	*) sed -n '2,17p' "$0"; exit 2 ;;
	esac
done
PREFIX=${PREFIX:-macos-deps-out/prefix} CACHE=${CACHE:-macos-deps-out/sources}
mkdir -p "$PREFIX" "$CACHE"
PREFIX=$(cd "$PREFIX" && pwd) CACHE=$(cd "$CACHE" && pwd)
WORK=$(mktemp -d "${TMPDIR:-/tmp}/freewrl-deps.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

# package version url sha256
PACKAGES="
freetype 2.14.3 https://downloads.sourceforge.net/project/freetype/freetype2/2.14.3/freetype-2.14.3.tar.xz 36bc4f1cc413335368ee656c42afca65c5a3987e8768cc28cf11ba775e785a5f
ode 0.16.6 https://bitbucket.org/odedevs/ode/downloads/ode-0.16.6.tar.gz c91a28c6ff2650284784a79c726a380d6afec87ecf7a35c32a6be0c5b74513e8
freealut 1.1.0 https://deb.debian.org/debian/pool/main/f/freealut/freealut_1.1.0.orig.tar.gz 60d1ea8779471bb851b89b49ce44eecb78e46265be1a6e9320a28b100c8df44f
SDL3 3.4.18 https://github.com/libsdl-org/SDL/releases/download/release-3.4.18/SDL3-3.4.18.tar.gz 9c75cf16330322c217dedd2e0609f1124f1b54b8633e763467b4684d0f4334a3
"
# commit of SDL's release-<version> tag (github.com/libsdl-org/SDL); the archive's
# REVISION.txt must name it. freex3d/CMakeLists.txt reads this line and the SDL3 row above.
SDL3_COMMIT=829a65d769d935c4852f8159e964312c0957260a
command -v cmake > /dev/null || { echo "SDL3 needs cmake" >&2; exit 1; }

export MACOSX_DEPLOYMENT_TARGET=$TARGET
FLAGS="-arch arm64 -mmacosx-version-min=$TARGET"
# header room for bundle.py to rewrite install names to @rpath (Homebrew adds this too)
export CC=clang CXX=clang++ CFLAGS="$FLAGS -O2" CXXFLAGS="$FLAGS -O2" LDFLAGS="$FLAGS -Wl,-headerpad_max_install_names"
# keep Homebrew (or any other pkg-config tree) out of the builds
export PKG_CONFIG_LIBDIR="$PREFIX/lib/pkgconfig" PKG_CONFIG_PATH=
NCPU=$(sysctl -n hw.ncpu)

META=$PREFIX/share/freewrl-deps
rm -rf "$META"
mkdir -p "$META/licenses"
printf 'package\tversion\tlibraries\tsource\tsha256\n' > "$META/packages.tsv"

fetch() { # url sha256 -> path of the verified archive
	f=$CACHE/$(basename "$1")
	[ -f "$f" ] || curl -sSfL -o "$f.part" "$1" && { [ -f "$f" ] || mv "$f.part" "$f"; }
	got=$(shasum -a 256 "$f" | cut -d' ' -f1)
	[ "$got" = "$2" ] || { echo "$f: SHA-256 $got, expected $2" >&2; exit 1; }
	echo "$f"
}
licenses() { # package file...  (license files, from the source tree)
	mkdir -p "$META/licenses/$1"
	p=$1; shift
	for f; do cp "$f" "$META/licenses/$p/"; done
	chmod 644 "$META/licenses/$p"/*
}

echo "$PACKAGES" | while read -r pkg ver url sha; do
	[ -n "$pkg" ] || continue
	echo "== $pkg $ver (macOS $TARGET)"
	src=$(fetch "$url" "$sha")
	tar xf "$src" -C "$WORK"
	cd "$WORK/$pkg-$ver"
	log=$WORK/$pkg.log
	dirs=.
	case $pkg in
	freetype)
		# system zlib and bzip2 only; no PNG (colour emoji bitmaps), HarfBuzz or Brotli
		./configure --prefix="$PREFIX" --enable-shared --disable-static \
			--with-zlib=yes --with-bzip2=yes --with-png=no --with-harfbuzz=no --with-brotli=no > "$log" 2>&1
		libs=libfreetype.6.dylib
		licenses freetype LICENSE.TXT docs/FTL.TXT docs/GPLv2.TXT ;;
	ode)
		# as Homebrew builds it (double precision, libccd colliders), but with ODE's own copy
		# of libccd instead of a separate library
		./configure --prefix="$PREFIX" --enable-shared --disable-static --disable-demos \
			--enable-double-precision --enable-libccd --with-libccd=internal > "$log" 2>&1
		libs=libode.8.dylib
		licenses ode COPYING LICENSE.TXT LICENSE-BSD.TXT
		cp libccd/BSD-LICENSE "$META/licenses/ode/libccd-BSD-LICENSE" ;;
	freealut)
		# Apple's OpenAL, as FreeWRL uses (configure's library search only knows libopenal)
		LIBS="-framework OpenAL" ./configure --prefix="$PREFIX" --enable-shared --disable-static \
			--disable-debug --disable-dependency-tracking > "$log" 2>&1
		libs=libalut.0.dylib
		dirs="src include"  # the library and its header, not the examples and tests
		licenses freealut COPYING ;;
	SDL3)
		rev=$(cat REVISION.txt)
		case $rev in
		"release-$ver-0-g"*) [ "${SDL3_COMMIT#"${rev##*-g}"}" != "$SDL3_COMMIT" ] ;;
		*) false ;;
		esac || { echo "SDL3: REVISION.txt says $rev, expected release-$ver at $SDL3_COMMIT" >&2; exit 1; }
		# a shared library only: no static library, framework, tests or examples; the prefix's
		# CMake config and pkg-config files are what FreeWRL's builds use
		cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PREFIX" \
			-DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_DEPLOYMENT_TARGET="$TARGET" \
			-DCMAKE_IGNORE_PREFIX_PATH="/opt/homebrew;/usr/local;/opt/local" \
			-DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_FRAMEWORK=OFF -DSDL_TEST_LIBRARY=OFF \
			-DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF > "$log" 2>&1 || { tail -30 "$log"; exit 1; }
		{ cmake --build build -j"$NCPU" && cmake --install build; } >> "$log" 2>&1 || { tail -30 "$log"; echo "$pkg: build failed" >&2; exit 1; }
		got=$(sed -n 's/^Version: //p' "$PREFIX/lib/pkgconfig/sdl3.pc")
		[ "$got" = "$ver" ] || { echo "SDL3: installed version $got, expected $ver" >&2; exit 1; }
		echo "   SDL3 $got, $rev"
		libs=libSDL3.0.dylib
		dirs=
		licenses SDL3 LICENSE.txt ;;
	esac
	for d in $dirs; do
		{ make -C "$d" -j"$NCPU" && make -C "$d" install; } >> "$log" 2>&1 || { tail -30 "$log"; echo "$pkg: build failed" >&2; exit 1; }
	done
	chmod 644 "$META/licenses/$pkg"/*
	printf '%s\t%s\t%s\t%s\t%s\n' "$pkg" "$ver" "$libs" "$url" "$sha" >> "$META/packages.tsv"
	for l in $libs; do
		[ -f "$PREFIX/lib/$l" ] || { echo "$pkg: $PREFIX/lib/$l not built" >&2; exit 1; }
		m=$(otool -l "$PREFIX/lib/$l" | awk '/LC_BUILD_VERSION/{f=1} f&&/minos/{print $2; exit}')
		echo "   $l: minimum macOS $m"
	done
	cd - > /dev/null
done
echo "prefix: $PREFIX"
