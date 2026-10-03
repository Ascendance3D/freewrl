#!/bin/sh
# Xcode Cloud: runs after each xcodebuild action. An action that builds FreeWRL.app must leave it
# in the one place Xcode Cloud puts it (the archive, or derived data for one configuration); the
# script fails if the app is missing. It checks that the app is arm64 only and that its minos and
# LSMinimumSystemVersion equal the project's MACOSX_DEPLOYMENT_TARGET. FreeWRL is not started
# (Xcode Cloud has no GPU session for it; runtime and ASan proof stay in
# .github/workflows/macos.yml). See ci_scripts/README.md.
set -eu
ROOT=${CI_PRIMARY_REPOSITORY_PATH:?not running in Xcode Cloud}
PBX=$ROOT/OSX_gui/FreeWRL-Desktop/FreeWRL.xcodeproj/project.pbxproj
ACTION=${CI_XCODEBUILD_ACTION:-}
echo "action: ${ACTION:-?} exit: ${CI_XCODEBUILD_EXIT_CODE:-?}"
[ "${CI_XCODEBUILD_EXIT_CODE:-0}" = 0 ] || exit 0  # xcodebuild already failed the action

case $ACTION in
test-without-building) echo "action $ACTION builds no app: nothing to check"; exit 0 ;;
archive) dirs="${CI_ARCHIVE_PATH:?CI_ARCHIVE_PATH not set}/Products/Applications" ;;
*)
	DD=${CI_DERIVED_DATA_PATH:?CI_DERIVED_DATA_PATH not set}
	dirs="$DD/Build/Products/Release $DD/Build/Products/Debug" ;;
esac
APP= n=0
for d in $dirs; do
	[ -d "$d/FreeWRL.app" ] && { APP=$d/FreeWRL.app; n=$((n + 1)); }
done
if [ "$n" != 1 ]; then
	echo "error: expected exactly one FreeWRL.app after action '${ACTION:-?}', found $n in:" >&2
	for d in $dirs; do
		echo "  $d: $(ls "$d" 2>/dev/null | tr '\n' ' ' || true)" >&2
	done
	exit 1
fi

TARGET=$(awk -F' = ' '/MACOSX_DEPLOYMENT_TARGET/{sub(/;.*/, "", $2); print $2; exit}' "$PBX")
case $TARGET in [0-9]*.[0-9]*) ;; *) echo "error: no MACOSX_DEPLOYMENT_TARGET in $PBX" >&2; exit 1 ;; esac
E=$APP/Contents/MacOS/FreeWRL
[ -f "$E" ] || { echo "error: no executable $E" >&2; exit 1; }
echo "app: $APP"
echo "executable: $E"
echo "target: $TARGET"
archs=$(lipo -archs "$E"); echo "archs: $archs"
[ "$archs" = arm64 ] || { echo "error: archs '$archs', expected arm64 only" >&2; exit 1; }
minos=$(vtool -show-build "$E" | awk '/minos/{print $2; exit}'); echo "minos: $minos"
[ "$minos" = "$TARGET" ] || { echo "error: minos '$minos', expected $TARGET" >&2; exit 1; }
ls=$(/usr/libexec/PlistBuddy -c 'Print :LSMinimumSystemVersion' "$APP/Contents/Info.plist"); echo "LSMinimumSystemVersion: $ls"
[ "$ls" = "$TARGET" ] || { echo "error: LSMinimumSystemVersion '$ls', expected $TARGET" >&2; exit 1; }
"$ROOT/tools/macos-ci/doctypes.sh" "$APP"
echo "PASS post-build: $APP"
