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
		tools/macos-release/check-ci-run.sh \
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
check "ci-good-passes" "'$ci' --conclusion success --head-sha abc123 --expected-sha abc123 --workflow-name 'macOS Apple Silicon CI'" 0 "RESULT: PASS"
check "ci-failed-run-rejected" "'$ci' --conclusion failure --head-sha abc123 --expected-sha abc123 --workflow-name 'macOS Apple Silicon CI'" 1 "FAIL ci-success"
check "ci-wrong-sha-rejected" "'$ci' --conclusion success --head-sha abc123 --expected-sha def456 --workflow-name 'macOS Apple Silicon CI'" 1 "FAIL ci-sha"
check "ci-wrong-workflow-rejected" "'$ci' --conclusion success --head-sha abc123 --expected-sha abc123 --workflow-name 'Some Other CI'" 1 "FAIL ci-workflow"

echo
echo "== make-release-metadata.sh (checksums + manifest) =="
# a well-formed fake archive with an app Info.plist inside
app=$tmp/src/FreeWRL.app/Contents; mkdir -p "$app"
cat > "$app/Info.plist" <<'PL'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>LSMinimumSystemVersion</key><string>14.0</string></dict></plist>
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
check "metadata-manifest-matches-checksum" "python3 -c 'import json,sys; m=json.load(open(sys.argv[1])); sys.exit(0 if m[\"sha256\"]==sys.argv[2] and m[\"minimum_macos\"]==\"14.0\" and m[\"commit\"]==\"cafe\" else 1)' '$O/release-manifest.json' '$SUM'" 0
check "metadata-wrong-name-rejected" "'$meta' --archive '$A' --version 1.2.3 --tag v1.2.3 --commit x --out '$tmp/o-wrong'" 1 "asset contract"
check "metadata-missing-archive-rejected" "'$meta' --archive '$tmp/nope.zip' --version 6.8.0 --tag v6.8.0 --commit x --out '$tmp/o-missing'" 1
check "metadata-overwrite-refused" "'$meta' --archive '$A' --version 6.8.0 --tag v6.8.0 --commit x --out '$O'" 1 "refusing to overwrite"
check "metadata-overwrite-forced" "'$meta' --archive '$A' --version 6.8.0 --tag v6.8.0 --commit x --out '$O' --force" 0 "wrote"
check "metadata-selftest-passes" "'$meta' --selftest" 0 "SELFTEST: PASS"

echo
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then echo "TOTAL: $pass/$total PASS, $fail FAIL"; exit 1; fi
echo "TOTAL: $pass/$total PASS"
