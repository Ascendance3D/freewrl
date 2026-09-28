#!/bin/bash
# check-app-version.sh --app FreeWRL.app (--tag TAG | --expected VERSION)
# Release-safety gate: read CFBundleShortVersionString from the BUILT application bundle and require
# it to equal the version the release tag derives to. It inspects the built artifact, never the
# source plist, so a release cannot ship an app whose displayed version does not match its tag.
# Read-only: it never tags, releases, pushes or builds. See RELEASING.md.
#
#   --app APP          the built FreeWRL.app to inspect (reads APP/Contents/Info.plist)
#   --tag TAG          release tag; the core MAJOR.MINOR.PATCH is compared (e.g. v6.8.0 -> 6.8.0,
#                      v6.8.0-beta.1 -> 6.8.0)
#   --expected VERSION compare against this exact version instead of deriving from a tag
#
# Prints one PASS or FAIL line and a RESULT line. Exit 0 on match, 1 on any mismatch or unreadable
# input, 2 on a usage error.
set -u
prog=${0##*/}
die() { echo "$prog: $*" >&2; sed -n '2,15p' "$0" | sed 's/^# \{0,1\}/  /' >&2; exit 2; }

app= tag= expected=
while [ $# -gt 0 ]; do
	case $1 in
	--app) [ $# -ge 2 ] || die "--app needs a path"; app=$2; shift ;;
	--tag) [ $# -ge 2 ] || die "--tag needs a value"; tag=$2; shift ;;
	--expected) [ $# -ge 2 ] || die "--expected needs a value"; expected=$2; shift ;;
	-h|--help) sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
	*) die "unknown argument: $1" ;;
	esac
	shift
done
[ -n "$app" ] || die "--app is required"
[ -n "$tag" ] || [ -n "$expected" ] || die "one of --tag or --expected is required"

# the version the tag derives to: strip leading v and any -alpha/-beta/-rc.N suffix
if [ -n "$expected" ]; then want=$expected
else want=$(printf '%s' "$tag" | sed -E 's/^v//; s/-(alpha|beta|rc)\.[0-9]+$//'); fi

echo "check-app-version: built-app version gate (reads CFBundleShortVersionString from the bundle)"
echo "  app:      $app"
echo "  expected: $want${tag:+  (from tag $tag)}"

plist=$app/Contents/Info.plist
if [ ! -f "$plist" ]; then
	echo "FAIL app-plist: $plist is missing or not a file (cannot read the built app version)"
	echo "RESULT: FAIL"
	exit 1
fi

# read CFBundleShortVersionString; a missing key must FAIL, not read as empty
got= rc=1
if command -v /usr/libexec/PlistBuddy >/dev/null 2>&1; then
	got=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$plist" 2>/dev/null); rc=$?
fi
if [ "$rc" -ne 0 ] || [ -z "$got" ]; then
	if command -v plutil >/dev/null 2>&1; then
		got=$(plutil -extract CFBundleShortVersionString raw -o - "$plist" 2>/dev/null); rc=$?
	fi
fi
if [ "$rc" -ne 0 ] || [ -z "$got" ]; then
	echo "FAIL app-version-key: CFBundleShortVersionString missing or empty in $plist"
	echo "RESULT: FAIL"
	exit 1
fi

if [ "$got" = "$want" ]; then
	echo "PASS app-version: built app CFBundleShortVersionString $got == $want"
	echo "RESULT: PASS"
	exit 0
fi
echo "FAIL app-version: built app CFBundleShortVersionString $got != $want (tag and app disagree)"
echo "RESULT: FAIL"
exit 1
