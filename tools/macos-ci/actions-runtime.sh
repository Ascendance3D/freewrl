#!/bin/bash
# actions-runtime.sh : every GitHub Action that .github/workflows uses must run on Node 24.
# For each `uses: owner/repo[/path]@ref`, read that action's action.yml (or action.yaml) at ref
# through the GitHub API (gh) and check `runs.using`: node24, composite or docker pass; node20 and
# older fail. GitHub runs a Node 20 action on Node 24 with a deprecation warning ("Node.js 20 is
# deprecated ... forced to run on Node.js 24"); this check catches it before a run does.
# Local actions (./path) and docker:// images are skipped.
# Prints one PASS/FAIL line per action and ACTIONS PASS|FAIL; exit 1 on a failure, 2 when gh is
# missing or the API cannot be read (offline, not logged in).
set -u
SRC=$(cd "$(dirname "$0")/../.." && pwd)
command -v gh >/dev/null 2>&1 || { echo "actions-runtime: gh not found"; exit 2; }
fail=0
for a in $(sed -n 's/^[[:space:]-]*uses:[[:space:]]*\([^[:space:]#]*\).*/\1/p' "$SRC"/.github/workflows/*.yml "$SRC"/.github/workflows/*.yaml 2>/dev/null | sort -u); do
	case $a in ./*|docker://*) continue;; esac
	ref=${a##*@} spec=${a%@*}
	repo=$(echo "$spec" | cut -d/ -f1-2) sub=$(echo "$spec" | cut -d/ -f3- -s)
	using=""
	for file in action.yml action.yaml; do
		path=${sub:+$sub/}$file
		body=$(gh api "repos/$repo/contents/$path?ref=$ref" --jq .content 2>/dev/null) || continue
		using=$(printf '%s' "$body" | base64 -d 2>/dev/null | sed -n "s/^[[:space:]]*using:[[:space:]]*['\"]\{0,1\}\([A-Za-z0-9]*\).*/\1/p" | head -1)
		[ -n "$using" ] && break
	done
	if [ -z "$using" ]; then
		echo "actions-runtime: cannot read the action.yml of $a (offline, not logged in, or no such ref)"; exit 2
	fi
	case $using in
		node24|composite|docker) echo "PASS $a: $using" ;;
		*) echo "FAIL $a: $using (needs node24; use a newer major of $repo)"; fail=1 ;;
	esac
done
[ $fail = 0 ] && echo "ACTIONS PASS" || echo "ACTIONS FAIL"
exit $fail
