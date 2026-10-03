#!/bin/bash
# xib-check.sh : static gate for the Desktop app's Interface Builder files. No GUI, no app launch.
# For every .xib that FreeWRL.xcodeproj builds:
#   - ibtool compiles it with no error, warning or notice (a deprecated appearance such as
#     texturedBackground is a warning);
#   - every customClass names a class that exists: an AppKit class (NS...), FirstResponder, or an
#     @interface in OSX_gui/FreeWRL-Desktop/FreeWRL. A missing class is only logged at run time
#     ("[Nib Loading] Unknown class 'BtnLoad'"), and AppKit silently uses the superclass.
# And every .xib under OSX_gui/FreeWRL-Desktop is one the project builds: an unbuilt copy is easy
# to edit by mistake (en.lproj/MainMenu.xib was one).
# Prints PASS/FAIL lines and XIBCHECK PASS|FAIL; exit 1 on any failure, 2 without ibtool.
set -u
SRC=$(cd "$(dirname "$0")/../.." && pwd)
D=$SRC/OSX_gui/FreeWRL-Desktop
PROJ=$D/FreeWRL.xcodeproj/project.pbxproj
command -v ibtool >/dev/null 2>&1 || { echo "xib-check: ibtool not found (Xcode)"; exit 2; }
tmp=$(mktemp -d "${TMPDIR:-/tmp}/xib-check.XXXXXX"); trap 'rm -rf "$tmp"' EXIT
fail=0
bad() { echo "FAIL $*"; fail=1; }

# the .xib files the project builds: PBXFileReference paths, found under the FreeWRL group
built=()
for p in $(sed -n 's/.*lastKnownFileType = file\.xib; path = \([^;]*\);.*/\1/p' "$PROJ"); do
	f=$D/FreeWRL/$p
	if [ -f "$f" ]; then built+=("$f"); else bad "project references $p, not found at ${f#"$SRC"/}"; fi
done
[ ${#built[@]} -ge 1 ] || bad "no .xib file reference in ${PROJ#"$SRC"/}"
while IFS= read -r f; do
	case " ${built[*]} " in *" $f "*) ;; *) bad "${f#"$SRC"/} is not built by FreeWRL.xcodeproj (delete it or add it)";; esac
done < <(find "$D" -name '*.xib' -not -path '*/build/*' -not -path '*/DerivedData/*' | sort)

classes=$(cat "$D"/FreeWRL/*.h "$D"/FreeWRL/*.m 2>/dev/null | sed -n 's/^[[:space:]]*@interface[[:space:]]\{1,\}\([A-Za-z_][A-Za-z0-9_]*\).*/\1/p' | sort -u)
for f in "${built[@]}"; do
	rel=${f#"$SRC"/}
	ibtool --errors --warnings --notices --output-format human-readable-text \
		--compile "$tmp/$(basename "$f" .xib).nib" "$f" > "$tmp/ibtool.txt" 2>&1
	rc=$?
	msgs=$(grep -E ': (error|warning|notice): ' "$tmp/ibtool.txt")
	if [ $rc != 0 ] || [ -n "$msgs" ]; then
		bad "$rel: ibtool exit $rc"; sed 's/^/    /' "$tmp/ibtool.txt"
	else
		echo "PASS $rel: ibtool compiles with no error, warning or notice"
	fi
	missing=""
	for c in $(sed -n 's/.*customClass="\([^"]*\)".*/\1/p' "$f" | sort -u); do
		case $c in NS*|FirstResponder) continue;; esac
		echo "$classes" | grep -qx "$c" || missing="$missing $c"
	done
	if [ -n "$missing" ]; then bad "$rel: customClass with no @interface in OSX_gui/FreeWRL-Desktop/FreeWRL:$missing"
	else echo "PASS $rel: every customClass exists"; fi
done
[ $fail = 0 ] && echo "XIBCHECK PASS" || echo "XIBCHECK FAIL"
exit $fail
