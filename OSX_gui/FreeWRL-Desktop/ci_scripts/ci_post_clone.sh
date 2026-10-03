#!/bin/sh
# Xcode Cloud: runs after the clone, before xcodebuild. Xcode Cloud cannot pass build settings
# on the command line the way GitHub Actions and Codemagic do (FW_DEPS=..., ARCHS=arm64), so
# this script prepares the clone instead:
#   1. host-only container tests (tools/c-tests, no app launch);
#   2. FreeType, ODE and freealut from their pinned sources (tools/macos-deps/build.sh), for the
#      project's own MACOSX_DEPLOYMENT_TARGET, into a private prefix;
#   3. FW_DEPS points at that prefix and ARCHS is arm64, in this clone's project.pbxproj only.
# Nothing is committed back. See ci_scripts/README.md.
set -eu
ROOT=${CI_PRIMARY_REPOSITORY_PATH:?not running in Xcode Cloud}
PBX=$ROOT/OSX_gui/FreeWRL-Desktop/FreeWRL.xcodeproj/project.pbxproj
PREFIX=$ROOT/macos-deps-out/prefix

sw_vers; uname -m; xcodebuild -version

"$ROOT/tools/c-tests/run-containers.sh"

TARGET=$(awk -F' = ' '/MACOSX_DEPLOYMENT_TARGET/{sub(/;.*/, "", $2); print $2; exit}' "$PBX")
case $TARGET in [0-9]*.[0-9]*) ;; *) echo "no MACOSX_DEPLOYMENT_TARGET in $PBX" >&2; exit 1 ;; esac
echo "deployment target: $TARGET"
"$ROOT/tools/macos-deps/build.sh" -t "$TARGET" -p "$PREFIX" -c "$ROOT/macos-deps-out/sources"
cat "$PREFIX/share/freewrl-deps/packages.tsv"

n=$(grep -c 'FW_DEPS = /opt/homebrew;' "$PBX")
[ "$n" -ge 1 ] || { echo "FW_DEPS = /opt/homebrew; not found in $PBX" >&2; exit 1; }
sed -i '' -e "s|FW_DEPS = /opt/homebrew;|FW_DEPS = \"$PREFIX\"; ARCHS = arm64;|" "$PBX"
echo "FW_DEPS -> $PREFIX, ARCHS = arm64 ($n build configuration(s))"
