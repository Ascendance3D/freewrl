#!/bin/bash
# test-release.sh
# Focused tests for the macOS release infrastructure. Everything runs in throwaway temp git
# repositories and temp directories: it creates NO public tags, NO GitHub releases, and touches
# NO remote. It needs only git, python3, zip and a SHA-256 tool. Prints one PASS/FAIL line per
# case and a TOTAL line. Exit 0 when every case passed, 1 otherwise.
set -u
here=$(cd "$(dirname "$0")" && pwd)
verify=$here/verify-release.sh
meta=$here/make-release-metadata.sh
ci=$here/check-ci-run.sh

pass=0 fail=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
no() { echo "FAIL $1${2:+: $2}"; fail=$((fail + 1)); }
# check NAME "command..." expect(0|1) [must-contain]
check() {
	local name=$1 cmd=$2 want=$3 needle=${4:-} out rc
	out=$(eval "$cmd" 2>&1); rc=$?
	if [ "$want" = 0 ] && [ "$rc" -ne 0 ]; then no "$name" "expected success, got exit $rc"; return; fi
	if [ "$want" = 1 ] && [ "$rc" -eq 0 ]; then no "$name" "expected failure, got success"; return; fi
	if [ -n "$needle" ] && ! printf '%s' "$out" | grep -q -- "$needle"; then
		no "$name" "output missing '$needle'"; return
	fi
	ok "$name"
}

tmp=$(mktemp -d "${TMPDIR:-/tmp}/fw-release-tests.XXXXXX") || exit 1
trap 'rm -rf "$tmp"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

# Build a fresh repo whose buildversion.h holds $2, on a `master` branch, with the release infra
# file paths present so verify-release's file-present check can pass. Echoes the repo path.
mkrepo() { # dir buildversion
	local d=$1 bv=$2 f
	mkdir -p "$d"; git -C "$d" init -q -b master
	mkdir -p "$d/freex3d/src" "$d/tools/macos-release" "$d/tools/macos-package" "$d/.github/workflows"
	printf '#define FW_BUILD_VERSION_STR "%s"\n#define FW_BUILD_VERSION_NUM %s,0\n' "$bv" "${bv//./,}" \
		> "$d/freex3d/src/buildversion.h"
	for f in tools/macos-release/verify-release.sh tools/macos-release/make-release-metadata.sh \
		tools/macos-release/check-ci-run.sh tools/macos-release/check-app-version.sh \
		tools/macos-package/package.sh .github/workflows/release-macos.yml RELEASING.md; do
		: > "$d/$f"
	done
	git -C "$d" add -A; git -C "$d" commit -qm "base $bv"
	printf '%s\n' "$d"
}

echo "== verify-release.sh (tag validation) =="

R=$(mkrepo "$tmp/r1" 6.8.0); C=$(git -C "$R" rev-parse HEAD)
git -C "$R" tag -a v6.8.0 -m "release 6.8.0"
check "valid-annotated-passes" "'$verify' --repo '$R' --tag v6.8.0 --expected-sha '$C'" 0 "RESULT: PASS"

R=$(mkrepo "$tmp/r2" 6.8.0); C=$(git -C "$R" rev-parse HEAD)
git -C "$R" tag v6.8.0   # lightweight
check "lightweight-rejected" "'$verify' --repo '$R' --tag v6.8.0 --expected-sha '$C'" 1 "FAIL tag-annotated"

R=$(mkrepo "$tmp/r3" 6.8.0); C=$(git -C "$R" rev-parse HEAD)
check "missing-tag-rejected" "'$verify' --repo '$R' --tag v6.8.0 --expected-sha '$C'" 1 "FAIL tag-exists"

R=$(mkrepo "$tmp/r4" 6.8.0); C=$(git -C "$R" rev-parse HEAD)
check "invalid-format-rejected" "'$verify' --repo '$R' --tag 6.8.0 --expected-sha '$C'" 1 "FAIL tag-syntax"

R=$(mkrepo "$tmp/r5" 6.8.0); C1=$(git -C "$R" rev-parse HEAD)
git -C "$R" tag -a v6.8.0 -m x
echo change > "$R/freex3d/src/note.txt"; git -C "$R" add -A; git -C "$R" commit -qm second
C2=$(git -C "$R" rev-parse HEAD)
check "expected-sha-mismatch-rejected" "'$verify' --repo '$R' --tag v6.8.0 --expected-sha '$C2'" 1 "FAIL expected-sha"

# unreachable: tag a commit that lives only on a side branch, not on master
R=$(mkrepo "$tmp/r6" 6.8.0)
git -C "$R" checkout -q -b side
echo s > "$R/side.txt"; git -C "$R" add -A; git -C "$R" commit -qm side
S=$(git -C "$R" rev-parse HEAD)
git -C "$R" tag -a v6.8.0 -m x "$S"
git -C "$R" checkout -q master
check "unreachable-from-master-rejected" "'$verify' --repo '$R' --tag v6.8.0 --expected-sha '$S'" 1 "FAIL reachable"

R=$(mkrepo "$tmp/r7" 6.8.0); C=$(git -C "$R" rev-parse HEAD)
git -C "$R" tag -a v9.9.9 -m x   # annotated, reachable, but disagrees with buildversion.h
check "version-mismatch-rejected" "'$verify' --repo '$R' --tag v9.9.9 --expected-sha '$C'" 1 "FAIL version-agrees"

echo
echo "== check-ci-run.sh (CI-run gate) =="
# the formal-release contract: success, exact SHA, workflow_dispatch, master,
# .github/workflows/macos.yml. GitHub Actions is release validation only, so a push or pull_request
# run is never release evidence. ciargs overrides fields of a good run: ciargs [FIELD VALUE]...
SHA1=1111111111111111111111111111111111111111 SHA2=2222222222222222222222222222222222222222
ciargs() {
	local conclusion=success head=$SHA1 event=workflow_dispatch branch=master path=.github/workflows/macos.yml
	local name='macOS Release Validation'
	while [ $# -ge 2 ]; do
		case $1 in
		conclusion) conclusion=$2 ;; head) head=$2 ;; event) event=$2 ;; branch) branch=$2 ;;
		path) path=$2 ;; name) name=$2 ;;
		esac
		shift 2
	done
	printf "%s --conclusion '%s' --head-sha '%s' --expected-sha '%s' --event '%s' --head-branch '%s' --workflow-path '%s' --workflow-name '%s'" \
		"'$ci'" "$conclusion" "$head" "$SHA1" "$event" "$branch" "$path" "$name"
}
check "ci-master-dispatch-passes" "$(ciargs)" 0 "RESULT: PASS"
check "ci-push-rejected" "$(ciargs event push)" 1 "FAIL ci-event"
check "ci-pull-request-rejected" "$(ciargs event pull_request)" 1 "FAIL ci-event"
check "ci-other-branch-dispatch-rejected" "$(ciargs branch macos/some-branch)" 1 "FAIL ci-branch"
check "ci-wrong-workflow-path-rejected" "$(ciargs path .github/workflows/release-macos.yml)" 1 "FAIL ci-workflow-path"
check "ci-wrong-sha-rejected" "$(ciargs head $SHA2)" 1 "FAIL ci-sha"
check "ci-short-sha-rejected" "$(ciargs head ${SHA1:0:12})" 1 "FAIL ci-sha"
check "ci-failed-run-rejected" "$(ciargs conclusion failure)" 1 "FAIL ci-success"
check "ci-in-progress-run-rejected" "$(ciargs conclusion null)" 1 "FAIL ci-success"
# the display name is right but the file is not: the name alone is not proof
check "ci-right-name-wrong-path-rejected" "$(ciargs path .github/workflows/other.yml)" 1 "PASS ci-workflow-name"
check "ci-right-name-wrong-path-fails" "$(ciargs path .github/workflows/other.yml)" 1 "FAIL ci-workflow-path"
check "ci-wrong-name-rejected" "$(ciargs name 'Some Other CI')" 1 "FAIL ci-workflow-name"
# the path is authoritative: no display name given, the right path still passes
check "ci-path-only-passes" "'$ci' --conclusion success --head-sha $SHA1 --expected-sha $SHA1 --event workflow_dispatch --head-branch master --workflow-path .github/workflows/macos.yml" 0 "RESULT: PASS"
# a missing required field is a usage error (exit 2), not a decision
check "ci-missing-event-usage-error" "'$ci' --conclusion success --head-sha $SHA1 --expected-sha $SHA1 --head-branch master --workflow-path .github/workflows/macos.yml; [ \$? -eq 2 ]" 0 "--event is required"

echo
echo "== check-app-version.sh (built-app version gate) =="
appver=$here/check-app-version.sh
# helper: build a throwaway FreeWRL.app whose Info.plist carries $2 as CFBundleShortVersionString
# (or, when $2 is the literal "NONE", omit the key)
mkapp() { # dir version
	local d=$1 v=$2
	mkdir -p "$d/FreeWRL.app/Contents"
	if [ "$v" = NONE ]; then
		cat > "$d/FreeWRL.app/Contents/Info.plist" <<'PL'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>CFBundleName</key><string>FreeWRL</string></dict></plist>
PL
	else
		cat > "$d/FreeWRL.app/Contents/Info.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>CFBundleShortVersionString</key><string>$v</string></dict></plist>
PL
	fi
	printf '%s\n' "$d/FreeWRL.app"
}
AV=$(mkapp "$tmp/av-match" 6.8.0)
check "appver-matches-tag-passes" "'$appver' --app '$AV' --tag v6.8.0" 0 "PASS app-version"
AV=$(mkapp "$tmp/av-diff" 4.2)
check "appver-differs-from-tag-rejected" "'$appver' --app '$AV' --tag v6.8.0" 1 "FAIL app-version"
AV=$(mkapp "$tmp/av-nokey" NONE)
check "appver-missing-key-rejected" "'$appver' --app '$AV' --tag v6.8.0" 1 "FAIL app-version-key"
mkdir -p "$tmp/av-noplist/FreeWRL.app/Contents"   # a bundle with no Info.plist at all
check "appver-missing-plist-rejected" "'$appver' --app '$tmp/av-noplist/FreeWRL.app' --tag v6.8.0" 1 "FAIL app-plist"
# a prerelease tag derives to its core version
AV=$(mkapp "$tmp/av-beta" 6.8.0)
check "appver-prerelease-core-passes" "'$appver' --app '$AV' --tag v6.8.0-beta.1" 0 "PASS app-version"
# --zip: the gate extracts the exact release archive and checks the app inside it
mkzip() { # dir version zip -> archive holding FreeWRL.app with that version
	mkapp "$1" "$2" >/dev/null && ( cd "$1" && zip -qry "$3" FreeWRL.app )
}
mkzip "$tmp/az-match" 6.8.0 "$tmp/az-match.zip"
check "appver-zip-matches-tag-passes" "'$appver' --zip '$tmp/az-match.zip' --tag v6.8.0" 0 "PASS app-version"
mkzip "$tmp/az-diff" 4.2 "$tmp/az-diff.zip"
check "appver-zip-stale-version-rejected" "'$appver' --zip '$tmp/az-diff.zip' --tag v6.7.0" 1 "FAIL app-version: built app CFBundleShortVersionString 4.2 != 6.7.0"
mkzip "$tmp/az-two" 6.8.0 "$tmp/az-two.zip"; mkdir -p "$tmp/az-two/Other.app"
( cd "$tmp/az-two" && zip -qry "$tmp/az-two.zip" Other.app )
check "appver-zip-two-apps-rejected" "'$appver' --zip '$tmp/az-two.zip' --tag v6.8.0" 1 "FAIL app-zip"
mkdir -p "$tmp/az-none" && echo x > "$tmp/az-none/readme.txt" && ( cd "$tmp/az-none" && zip -q "$tmp/az-none.zip" readme.txt )
check "appver-zip-no-app-rejected" "'$appver' --zip '$tmp/az-none.zip' --tag v6.8.0" 1 "FAIL app-zip"
echo "not a zip" > "$tmp/az-bad.zip"
check "appver-zip-corrupt-rejected" "'$appver' --zip '$tmp/az-bad.zip' --tag v6.8.0" 1 "FAIL app-zip"
check "appver-zip-missing-rejected" "'$appver' --zip '$tmp/az-nope.zip' --tag v6.8.0" 1 "FAIL app-zip"
check "appver-app-and-zip-usage-error" "'$appver' --app '$AV' --zip '$tmp/az-match.zip' --tag v6.8.0; [ \$? -eq 2 ]" 0 "not both"

echo
echo "== source version identity (this checkout) =="
# the Desktop app's CFBundleShortVersionString must equal the engine's FW_BUILD_VERSION_STR, so the
# built app reports the same version as the tag check-app-version.sh gates on. Reads both files.
root=$(cd "$here/../.." && pwd)
bvh=$root/freex3d/src/buildversion.h
dplist=$root/OSX_gui/FreeWRL-Desktop/FreeWRL/FreeWRL-Info.plist
BV=$(sed -nE 's/^#define FW_BUILD_VERSION_STR "([^"]*)".*/\1/p' "$bvh")
PV=$(python3 -c 'import plistlib,sys; print(plistlib.load(open(sys.argv[1],"rb")).get("CFBundleShortVersionString",""))' "$dplist" 2>/dev/null)
check "source-version-identity" "echo 'buildversion.h=$BV Desktop plist=$PV'; [ -n '$BV' ] && [ '$BV' = '$PV' ]" 0

echo
echo "== make-release-metadata.sh (checksums + manifest) =="
# a well-formed fake archive with an app Info.plist inside
app=$tmp/src/FreeWRL.app/Contents; mkdir -p "$app"
cat > "$app/Info.plist" <<'PL'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>LSMinimumSystemVersion</key><string>15.0</string></dict></plist>
PL
A=$tmp/FreeWRL-6.8.0-macOS-arm64.zip
( cd "$tmp/src" && zip -qr "$A" FreeWRL.app )
sha() { if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'; else sha256sum "$1" | awk '{print $1}'; fi; }
SUM=$(sha "$A")

O=$tmp/out
check "metadata-valid-generates" "'$meta' --archive '$A' --version 6.8.0 --tag v6.8.0 --commit cafe --out '$O'" 0 "wrote"
check "metadata-sha256sums-present" "test -f '$O/SHA256SUMS.txt' && test -f '$O/release-manifest.json'" 0
check "metadata-checksum-matches-bytes" "grep -q '$SUM  FreeWRL-6.8.0-macOS-arm64.zip' '$O/SHA256SUMS.txt'" 0
if command -v shasum >/dev/null 2>&1; then
	check "metadata-shasum-c-verifies" "cd '$O' && cp '$A' . && shasum -a 256 -c SHA256SUMS.txt" 0 "OK"
fi
check "metadata-manifest-matches-checksum" "python3 -c 'import json,sys; m=json.load(open(sys.argv[1])); sys.exit(0 if m[\"sha256\"]==sys.argv[2] and m[\"minimum_macos\"]==\"15.0\" and m[\"commit\"]==\"cafe\" else 1)' '$O/release-manifest.json' '$SUM'" 0
check "metadata-wrong-name-rejected" "'$meta' --archive '$A' --version 1.2.3 --tag v1.2.3 --commit x --out '$tmp/o-wrong'" 1 "asset contract"
check "metadata-missing-archive-rejected" "'$meta' --archive '$tmp/nope.zip' --version 6.8.0 --tag v6.8.0 --commit x --out '$tmp/o-missing'" 1
check "metadata-overwrite-refused" "'$meta' --archive '$A' --version 6.8.0 --tag v6.8.0 --commit x --out '$O'" 1 "refusing to overwrite"
check "metadata-overwrite-forced" "'$meta' --archive '$A' --version 6.8.0 --tag v6.8.0 --commit x --out '$O' --force" 0 "wrote"
check "metadata-selftest-passes" "'$meta' --selftest" 0 "SELFTEST: PASS"

echo
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then echo "TOTAL: $pass/$total PASS, $fail FAIL"; exit 1; fi
echo "TOTAL: $pass/$total PASS"
