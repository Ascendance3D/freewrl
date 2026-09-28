#!/bin/bash
# verify-release.sh --tag TAG --expected-sha SHA [--remote-ref REF] [--repo DIR]
# Host-side release-tag validator. It PROVES that a release tag is safe to build and publish.
# It is read-only: it never creates or moves a tag, never creates or edits a release, and never
# pushes or fetches. GitHub Actions and Ryan stay the authorities that build and publish. It works
# from any directory inside the checkout. See tools/macos-release/README.md and RELEASING.md.
#
#   --tag TAG            the release tag to validate, e.g. v6.8.0 or v6.8.0-beta.1
#   --expected-sha SHA   the commit the tag must point at (full 40-char SHA preferred)
#   --remote-ref REF     branch the tagged commit must be reachable from
#                        (default: origin/master, else master)
#   --repo DIR           run against this checkout instead of the current directory
#
# Prints one PASS or FAIL line per check and a RESULT line. Exit status: 0 when every check
# passed, 1 when a check failed, 2 on a usage error.
set -u

prog=${0##*/}
die() { echo "$prog: $*" >&2; sed -n '2,13p' "$0" | sed 's/^# \{0,1\}/  /' >&2; exit 2; }

# accepted NEW formal release tag: vMAJOR.MINOR.PATCH, optionally -alpha.N / -beta.N / -rc.N
tag_re='^v[0-9]+\.[0-9]+\.[0-9]+(-(alpha|beta|rc)\.[0-9]+)?$'

tag= expected= remote_ref= repo=
while [ $# -gt 0 ]; do
	case $1 in
	--tag) [ $# -ge 2 ] || die "--tag needs a value"; tag=$2; shift ;;
	--expected-sha) [ $# -ge 2 ] || die "--expected-sha needs a value"; expected=$2; shift ;;
	--remote-ref) [ $# -ge 2 ] || die "--remote-ref needs a value"; remote_ref=$2; shift ;;
	--repo) [ $# -ge 2 ] || die "--repo needs a path"; repo=$2; shift ;;
	-h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
	*) die "unknown argument: $1" ;;
	esac
	shift
done
[ -n "$tag" ] || die "--tag is required"
[ -n "$expected" ] || die "--expected-sha is required"

# locate the checkout (from --repo, else the working directory)
cd "${repo:-.}" 2>/dev/null || die "no such directory: $repo"
root=$(git rev-parse --show-toplevel 2>/dev/null) || die "not inside a git checkout"
g() { git -C "$root" "$@"; }

pass=0 fail=0
ok()   { echo "PASS $1"; pass=$((pass + 1)); }
no()   { echo "FAIL $1"; fail=$((fail + 1)); }

echo "verify-release: read-only release-tag validation (it never tags, releases, pushes or fetches)"
echo "  repo:     $root"
echo "  tag:      $tag"
echo "  expected: $expected"

# 1. repository state: a real checkout with the object database reachable
if g rev-parse --git-dir >/dev/null 2>&1; then ok "repo-state: $root is a git checkout"
else no "repo-state: $root is not a usable git checkout"; fi

# 2. tag syntax: the accepted NEW formal release form
if printf '%s' "$tag" | grep -Eq "$tag_re"; then
	ok "tag-syntax: '$tag' matches vMAJOR.MINOR.PATCH[-alpha|beta|rc.N]"
else
	no "tag-syntax: '$tag' is not a valid new release tag (want vMAJOR.MINOR.PATCH[-beta.N])"
fi

# 3. tag exists
tag_type=$(g cat-file -t "refs/tags/$tag" 2>/dev/null)
if [ -n "$tag_type" ]; then ok "tag-exists: refs/tags/$tag is present"
else no "tag-exists: refs/tags/$tag not found (create the annotated tag first)"; fi

# 4. tag is annotated (a real tag object, not a lightweight ref to a commit)
if [ "$tag_type" = tag ]; then ok "tag-annotated: '$tag' is an annotated tag object"
elif [ -n "$tag_type" ]; then no "tag-annotated: '$tag' is lightweight ($tag_type); formal releases need an annotated tag"
else no "tag-annotated: cannot check, tag is missing"; fi

# 5. peeled tag commit equals the expected SHA
peeled=$(g rev-parse -q --verify "refs/tags/$tag^{commit}" 2>/dev/null)
exp_full=$(g rev-parse -q --verify "${expected}^{commit}" 2>/dev/null)
if [ -z "$peeled" ]; then
	no "expected-sha: tag has no commit to peel"
elif [ -n "$exp_full" ] && [ "$peeled" = "$exp_full" ]; then
	ok "expected-sha: tag peels to $peeled"
elif [ -z "$exp_full" ] && printf '%s' "$peeled" | grep -iq "^$expected"; then
	ok "expected-sha: tag peels to $peeled (matched by prefix)"
else
	no "expected-sha: tag peels to ${peeled:-none}, not $expected"
fi

# 6. tagged commit is reachable from the release branch
ref=$remote_ref
if [ -z "$ref" ]; then
	for r in origin/master master; do g rev-parse -q --verify "$r^{commit}" >/dev/null 2>&1 && { ref=$r; break; }; done
fi
if [ -z "$ref" ]; then
	no "reachable: no origin/master or master to check reachability against (pass --remote-ref)"
elif [ -z "$peeled" ]; then
	no "reachable: no tagged commit to check"
elif g merge-base --is-ancestor "$peeled" "$ref" 2>/dev/null; then
	ok "reachable: tagged commit is an ancestor of $ref"
else
	no "reachable: tagged commit is NOT reachable from $ref (a release must build from the trunk)"
fi

# 7. tag version agrees with the built engine version. buildversion.h at the TAGGED commit is the
#    source that drives the macOS app (fwVersion.c -> ui/common.c libFreeWRL_get_version on AQUA).
core=$(printf '%s' "$tag" | sed -E 's/^v//; s/-(alpha|beta|rc)\.[0-9]+$//')
bv=$(g show "refs/tags/$tag:freex3d/src/buildversion.h" 2>/dev/null \
	| sed -n 's/^#define FW_BUILD_VERSION_STR "\([^"]*\)".*/\1/p' | head -1)
if [ -z "$tag_type" ]; then
	no "version-agrees: cannot check, tag is missing"
elif [ -z "$bv" ]; then
	no "version-agrees: FW_BUILD_VERSION_STR not found in buildversion.h at $tag"
elif [ "$core" = "$bv" ]; then
	ok "version-agrees: tag core $core == FW_BUILD_VERSION_STR $bv"
else
	no "version-agrees: tag core $core != FW_BUILD_VERSION_STR $bv (bump buildversion.h or choose the right tag)"
fi

# 8. the release infrastructure files exist at the tagged commit (so a build from the tag has them)
for f in \
	tools/macos-release/verify-release.sh \
	tools/macos-release/make-release-metadata.sh \
	tools/macos-release/check-ci-run.sh \
	tools/macos-package/package.sh \
	.github/workflows/release-macos.yml \
	RELEASING.md
do
	if g cat-file -e "refs/tags/$tag:$f" 2>/dev/null; then ok "file-present: $f at $tag"
	else no "file-present: $f missing at $tag"; fi
done

echo
if [ "$fail" -gt 0 ]; then
	echo "RESULT: FAIL ($fail of $((pass + fail)) checks failed). This tag is NOT safe to release."
	exit 1
fi
echo "RESULT: PASS ($pass checks). This tag is safe to build and, after review, publish."
