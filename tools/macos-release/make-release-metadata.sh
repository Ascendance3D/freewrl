#!/bin/bash
# make-release-metadata.sh --archive ZIP --version V --tag TAG --commit SHA [--out DIR]
#                          [--min-macos X] [--force]
# make-release-metadata.sh --selftest
# Produce the release metadata for one macOS Apple Silicon archive:
#   SHA256SUMS.txt        the archive's SHA-256, in `shasum -a 256 -c` format
#   release-manifest.json a small machine-readable record for the future Downloads page
# The SHA-256 is computed from the ACTUAL archive bytes, never from source files, and the manifest
# SHA-256 is the same value written to SHA256SUMS.txt. This tool uses no network. It does not
# create tags or releases and does not push. See tools/macos-release/README.md and RELEASING.md.
#
#   --archive ZIP    the exact built archive to describe
#   --version V      release version WITHOUT the leading v, e.g. 6.8.0 or 6.8.0-beta.1
#   --tag TAG        the annotated release tag, e.g. v6.8.0
#   --commit SHA     the tagged (peeled) commit the archive was built from
#   --out DIR        where to write the two files (default: the archive's directory)
#   --min-macos X    minimum macOS; default: read LSMinimumSystemVersion from the app in the archive
#   --force          overwrite existing output files (default: refuse, to protect a real release)
#   --selftest       run the built-in checks and exit (no arguments needed)
#
# The archive basename must be the release asset contract name:
#   FreeWRL-<version>-macOS-arm64.zip
# Exit status: 0 on success, 1 on a failure, 2 on a usage error.
set -u

prog=${0##*/}
die() { echo "$prog: $*" >&2; sed -n '2,25p' "$0" | sed 's/^# \{0,1\}/  /' >&2; exit 2; }
err() { echo "$prog: $*" >&2; exit 1; }

sha256() { # path -> lowercase hex
	if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
	else sha256sum "$1" | awk '{print $1}'; fi
}

# read LSMinimumSystemVersion from the FreeWRL.app inside the archive; empty if it cannot be read
min_macos_from_archive() { # zip -> version or empty
	local zip=$1 tmp plist v
	command -v unzip >/dev/null 2>&1 || return 0
	tmp=$(mktemp -d "${TMPDIR:-/tmp}/fw-relmeta.XXXXXX") || return 0
	unzip -oq "$zip" -d "$tmp" >/dev/null 2>&1 || { rm -rf "$tmp"; return 0; }
	plist=$(find "$tmp" -maxdepth 3 -path '*/Contents/Info.plist' -print 2>/dev/null | head -1)
	if [ -n "$plist" ]; then
		if command -v /usr/libexec/PlistBuddy >/dev/null 2>&1; then
			v=$(/usr/libexec/PlistBuddy -c 'Print :LSMinimumSystemVersion' "$plist" 2>/dev/null)
		fi
		[ -z "${v:-}" ] && command -v plutil >/dev/null 2>&1 && \
			v=$(plutil -extract LSMinimumSystemVersion raw -o - "$plist" 2>/dev/null)
	fi
	rm -rf "$tmp"
	printf '%s' "${v:-}"
}

# write SHA256SUMS.txt and release-manifest.json into OUT for the given archive/metadata
generate() { # archive version tag commit out min_macos force
	local archive=$1 version=$2 tag=$3 commit=$4 out=$5 min_macos=$6 force=$7
	local base sums manifest sum expect_name

	[ -f "$archive" ] || err "no such archive: $archive"
	[ -s "$archive" ] || err "archive is empty: $archive"
	base=${archive##*/}
	expect_name="FreeWRL-${version}-macOS-arm64.zip"
	[ "$base" = "$expect_name" ] || err "archive name '$base' breaks the asset contract (want '$expect_name')"

	mkdir -p "$out" || err "cannot create output directory: $out"
	sums=$out/SHA256SUMS.txt
	manifest=$out/release-manifest.json
	if [ "$force" != 1 ]; then
		for o in "$sums" "$manifest"; do
			[ -e "$o" ] && err "refusing to overwrite $o (pass --force)"
		done
	fi

	sum=$(sha256 "$archive")
	[ -n "$sum" ] || err "could not compute SHA-256 of $archive"

	# SHA256SUMS.txt in `shasum -a 256 -c` format: "<hex>  <name>" (two spaces).
	printf '%s  %s\n' "$sum" "$base" > "$sums" || err "cannot write $sums"

	# release-manifest.json: written by python3 so the JSON is well formed. The sha256 field is the
	# exact value in SHA256SUMS.txt; the commit is the validated tagged commit passed in.
	command -v python3 >/dev/null 2>&1 || err "python3 is required to write the manifest"
	FW_PROJECT="FreeWRL" FW_VERSION="$version" FW_TAG="$tag" FW_COMMIT="$commit" \
	FW_MINMACOS="$min_macos" FW_ASSET="$base" FW_SHA="$sum" \
	python3 - "$manifest" <<'PY' || err "cannot write $manifest"
import json, os, sys
m = {
    "project": os.environ["FW_PROJECT"],
    "version": os.environ["FW_VERSION"],
    "tag": os.environ["FW_TAG"],
    "commit": os.environ["FW_COMMIT"],
    "platform": "macOS",
    "architecture": "arm64",
    "minimum_macos": os.environ["FW_MINMACOS"],
    "asset": os.environ["FW_ASSET"],
    "sha256": os.environ["FW_SHA"],
}
with open(sys.argv[1], "w") as f:
    json.dump(m, f, indent=2)
    f.write("\n")
PY

	echo "wrote $sums"
	echo "wrote $manifest"
	echo "  asset:        $base"
	echo "  sha256:       $sum"
	echo "  version:      $version"
	echo "  tag:          $tag"
	echo "  commit:       $commit"
	echo "  minimum_macos: ${min_macos:-(unknown)}"
}

# ---- self-test: no network, uses a throwaway archive and temp dirs -----------------------------
selftest() {
	local pass=0 fail=0 arch out sum line mjson
	# t is intentionally NOT local: the EXIT trap below reads it after this function returns
	t=$(mktemp -d "${TMPDIR:-/tmp}/fw-relmeta-selftest.XXXXXX") || err "mktemp failed"
	trap 'rm -rf "$t"' EXIT
	tick() { if eval "$2"; then echo "PASS $1"; pass=$((pass + 1)); else echo "FAIL $1"; fail=$((fail + 1)); fi; }

	# a well-formed fake archive with a plausible app Info.plist inside
	mkdir -p "$t/src/FreeWRL.app/Contents"
	cat > "$t/src/FreeWRL.app/Contents/Info.plist" <<'PL'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>LSMinimumSystemVersion</key><string>14.0</string>
</dict></plist>
PL
	arch=$t/FreeWRL-9.9.9-macOS-arm64.zip
	( cd "$t/src" && zip -qr "$arch" FreeWRL.app ) || err "zip failed (needed for self-test)"
	out=$t/out

	# 1. valid archive: generation succeeds and writes both files
	tick "valid-archive" "'$0' --archive '$arch' --version 9.9.9 --tag v9.9.9 --commit deadbeef --out '$out' >/dev/null 2>&1 && [ -f '$out/SHA256SUMS.txt' ] && [ -f '$out/release-manifest.json' ]"

	# 2. checksum matches the real bytes (shasum -c verifies against the archive)
	sum=$(sha256 "$arch")
	line=$(cat "$out/SHA256SUMS.txt")
	tick "checksum-matches-bytes" "[ '$line' = '$sum  FreeWRL-9.9.9-macOS-arm64.zip' ]"

	# 3. manifest sha256 equals the SHA256SUMS value, and min_macos was read from the app
	mjson=$(python3 -c 'import json,sys;m=json.load(open(sys.argv[1]));print(m["sha256"],m["minimum_macos"],m["asset"])' "$out/release-manifest.json" 2>/dev/null)
	tick "manifest-matches-checksum" "[ '$mjson' = '$sum 14.0 FreeWRL-9.9.9-macOS-arm64.zip' ]"

	# 4. malformed input: a missing archive fails
	tick "missing-archive-fails" "! '$0' --archive '$t/nope.zip' --version 9.9.9 --tag v9.9.9 --commit x --out '$t/o4' >/dev/null 2>&1"

	# 5. wrong asset name (version mismatch in the contract name) fails
	tick "wrong-asset-name-fails" "! '$0' --archive '$arch' --version 1.2.3 --tag v1.2.3 --commit x --out '$t/o5' >/dev/null 2>&1"

	# 6. overwrite safety: a second run without --force refuses; with --force it succeeds
	tick "overwrite-refused" "! '$0' --archive '$arch' --version 9.9.9 --tag v9.9.9 --commit x --out '$out' >/dev/null 2>&1"
	tick "overwrite-forced" "'$0' --archive '$arch' --version 9.9.9 --tag v9.9.9 --commit x --out '$out' --force >/dev/null 2>&1"

	echo
	if [ "$fail" -gt 0 ]; then echo "SELFTEST: FAIL ($fail of $((pass + fail)) failed)"; return 1; fi
	echo "SELFTEST: PASS ($pass checks)"
}

# ---- argument parsing --------------------------------------------------------------------------
archive= version= tag= commit= out= min_macos= force=0 selftest=0
while [ $# -gt 0 ]; do
	case $1 in
	--archive) [ $# -ge 2 ] || die "--archive needs a path"; archive=$2; shift ;;
	--version) [ $# -ge 2 ] || die "--version needs a value"; version=$2; shift ;;
	--tag) [ $# -ge 2 ] || die "--tag needs a value"; tag=$2; shift ;;
	--commit) [ $# -ge 2 ] || die "--commit needs a value"; commit=$2; shift ;;
	--out) [ $# -ge 2 ] || die "--out needs a path"; out=$2; shift ;;
	--min-macos) [ $# -ge 2 ] || die "--min-macos needs a value"; min_macos=$2; shift ;;
	--force) force=1 ;;
	--selftest) selftest=1 ;;
	-h|--help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
	*) die "unknown argument: $1" ;;
	esac
	shift
done

if [ "$selftest" = 1 ]; then selftest; exit $?; fi

[ -n "$archive" ] || die "--archive is required"
[ -n "$version" ] || die "--version is required"
[ -n "$tag" ] || die "--tag is required"
[ -n "$commit" ] || die "--commit is required"
[ -n "$out" ] || out=$(cd "$(dirname "$archive")" && pwd)
[ -n "$min_macos" ] || min_macos=$(min_macos_from_archive "$archive")

generate "$archive" "$version" "$tag" "$commit" "$out" "$min_macos" "$force"
