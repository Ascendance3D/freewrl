#!/bin/bash
# test-verify.sh
# Focused tests for verify.py path handling. Builds a minimal FreeWRL-shaped bundle (arm64,
# macOS 14.0, three @rpath dylibs) in $TMPDIR and checks that verify.py
#   - passes it under the /var/folders spelling of $TMPDIR (really /private/var/folders), the
#     path package.sh used before it switched to pwd -P, and under the canonical spelling;
#   - still fails a run path that leaves Contents, one that only shares its name prefix
#     (Contents-x), and a dependency that is a symlink to a file outside the bundle.
# Needs clang (Xcode command line tools) and python3. Prints one PASS/FAIL line per case and a
# TOTAL line. Exit 0 when every case passed, 1 otherwise.
set -u
here=$(cd "$(dirname "$0")" && pwd)
verify=$here/verify.py

pass=0 fail=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
no() { echo "FAIL $1${2:+: $2}"; fail=$((fail + 1)); }
# check NAME APP expect(0|1) [must-contain]
check() {
	local name=$1 app=$2 want=$3 needle=${4:-} out rc
	out=$(python3 "$verify" --macos 14.0 "$app" 2>&1); rc=$?
	if [ "$want" = 0 ] && [ "$rc" -ne 0 ]; then no "$name" "expected success, got exit $rc"; printf '%s\n' "$out" | grep ERROR; return; fi
	if [ "$want" = 1 ] && [ "$rc" -eq 0 ]; then no "$name" "expected failure, got success"; return; fi
	if [ -n "$needle" ] && ! printf '%s' "$out" | grep -q -- "$needle"; then
		no "$name" "output missing '$needle'"; return
	fi
	ok "$name"
}

tmp=$(mktemp -d "${TMPDIR:-/tmp}/fw-verify-tests.XXXXXX") || exit 1
trap 'rm -rf "$tmp"' EXIT
cc() { clang -arch arm64 -mmacosx-version-min=14.0 "$@"; }

# mkapp DIR [extra exe linker flags...]: a bundle verify.py accepts unless the flags break it
mkapp() {
	local app=$1 c=$1/Contents lib f
	shift
	mkdir -p "$c/MacOS" "$c/Frameworks" "$c/Resources/fonts" "$c/Resources/ThirdPartyLicenses"
	cat > "$c/Info.plist" <<-EOF
	<?xml version="1.0" encoding="UTF-8"?>
	<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
	<plist version="1.0"><dict>
	<key>CFBundleExecutable</key><string>FreeWRL</string>
	<key>LSMinimumSystemVersion</key><string>14.0</string>
	</dict></plist>
	EOF
	echo 'int fw_lib(void) { return 0; }' > "$tmp/lib.c"
	echo 'int fw_lib(void); int main(void) { return fw_lib(); }' > "$tmp/main.c"
	for lib in libfreetype.6 libode.8 libalut.0; do
		(cd "$c/Frameworks" && cc -dynamiclib -install_name "@rpath/$lib.dylib" \
			-Wl,-rpath,@loader_path -o "$lib.dylib" "$tmp/lib.c") || return 1
	done
	(cd "$c/Frameworks" && cc -o ../MacOS/FreeWRL "$tmp/main.c" libfreetype.6.dylib libode.8.dylib \
		libalut.0.dylib -Wl,-rpath,@executable_path/../Frameworks "$@") || return 1
	for f in VeraMono Vera VeraBd VeraIt VeraBI VeraSe VeraSeBd VeraMoBd VeraMoIt VeraMoBI; do
		: > "$c/Resources/fonts/$f.ttf"
	done
	f=$c/Resources/ThirdPartyLicenses
	printf 'library\tversion\tpackage\n' > "$f/MANIFEST.tsv"
	printf 'package\tversion\tfile\tsource\n' > "$f/LICENSES.tsv"
	for lib in freetype FreeWRL duktape libtess stb_image; do
		mkdir -p "$f/$lib"; : > "$f/$lib/LICENSE"
		printf '%s\t1\tLICENSE\ttest\n' "$lib" >> "$f/LICENSES.tsv"
	done
	printf 'libfreetype.6.dylib\t1\tfreetype\n' >> "$f/MANIFEST.tsv"
	: > "$f/freetype/LICENSE.TXT"; : > "$f/freetype/FTL.TXT"
}

real=$(cd "$tmp" && pwd -P)
[ "$real" != "$tmp" ] || echo "note: $tmp has no other spelling; the alias case checks the canonical path"

mkapp "$tmp/good/FreeWRL.app" || { echo "FAIL could not build the test bundle (clang)"; exit 1; }
check "tmpdir-alias-path-passes" "$tmp/good/FreeWRL.app" 0 "PASS"
check "canonical-path-passes" "$real/good/FreeWRL.app" 0 "PASS"
check "dotdot-path-passes" "$tmp/good/../good/FreeWRL.app" 0 "PASS"

mkapp "$tmp/leaves/FreeWRL.app" -Wl,-rpath,@executable_path/../.. || exit 1
check "rpath-leaving-contents-fails" "$tmp/leaves/FreeWRL.app" 1 "LC_RPATH @executable_path/../.. leaves the bundle"

mkapp "$tmp/prefix/FreeWRL.app" -Wl,-rpath,@executable_path/../../Contents-x || exit 1
check "rpath-sharing-name-prefix-fails" "$tmp/prefix/FreeWRL.app" 1 "Contents-x leaves the bundle"

mkapp "$tmp/link/FreeWRL.app" || exit 1
mv "$tmp/link/FreeWRL.app/Contents/Frameworks/libode.8.dylib" "$tmp/link/libode.8.dylib"
ln -s ../../../libode.8.dylib "$tmp/link/FreeWRL.app/Contents/Frameworks/libode.8.dylib"
check "dependency-symlinked-outside-fails" "$tmp/link/FreeWRL.app" 1 "libode.8.dylib resolves outside the bundle"

echo
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then echo "TOTAL: $pass/$total PASS, $fail FAIL"; exit 1; fi
echo "TOTAL: $pass/$total PASS"
