#!/bin/sh
# Xcode Cloud: runs after each xcodebuild action. When the action produced FreeWRL.app, check
# that it is arm64 only and that its minos and LSMinimumSystemVersion equal the project's
# MACOSX_DEPLOYMENT_TARGET. FreeWRL is not started (Xcode Cloud has no GPU session for it;
# runtime and ASan proof stay in .github/workflows/macos.yml). See ci_scripts/README.md.
set -eu
ROOT=${CI_PRIMARY_REPOSITORY_PATH:?not running in Xcode Cloud}
PBX=$ROOT/OSX_gui/FreeWRL-Desktop/FreeWRL.xcodeproj/project.pbxproj
echo "action: ${CI_XCODEBUILD_ACTION:-?} exit: ${CI_XCODEBUILD_EXIT_CODE:-?}"
[ "${CI_XCODEBUILD_EXIT_CODE:-0}" = 0 ] || exit 0  # xcodebuild already failed the action

APP=
for d in "${CI_ARCHIVE_PATH:-}/Products/Applications" "${CI_DERIVED_DATA_PATH:-}/Build/Products/Release" "${CI_DERIVED_DATA_PATH:-}/Build/Products/Debug"; do
	[ -d "$d/FreeWRL.app" ] && { APP=$d/FreeWRL.app; break; }
done
[ -n "$APP" ] || { echo "no FreeWRL.app from this action: nothing to check"; exit 0; }

TARGET=$(awk -F' = ' '/MACOSX_DEPLOYMENT_TARGET/{sub(/;.*/, "", $2); print $2; exit}' "$PBX")
E=$APP/Contents/MacOS/FreeWRL
echo "app: $APP"
archs=$(lipo -archs "$E"); echo "archs: $archs"
[ "$archs" = arm64 ]
minos=$(vtool -show-build "$E" | awk '/minos/{print $2; exit}'); echo "minos: $minos (target $TARGET)"
[ "$minos" = "$TARGET" ]
ls=$(/usr/libexec/PlistBuddy -c 'Print :LSMinimumSystemVersion' "$APP/Contents/Info.plist"); echo "LSMinimumSystemVersion: $ls"
[ "$ls" = "$TARGET" ]
"$ROOT/tools/macos-ci/doctypes.sh" "$APP"
echo "PASS"
