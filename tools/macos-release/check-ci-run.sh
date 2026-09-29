#!/bin/bash
# check-ci-run.sh --conclusion C --head-sha H --expected-sha E --event V --head-branch B
#                 --workflow-path P [--workflow-name W]
# Decide whether a CI run is acceptable evidence for a formal release build. It takes the run's
# already-fetched facts and makes a pure decision; it does no network I/O itself, so it is easy to
# test. The release workflow reads the run from the GitHub Actions run API
# (GET /repos/{owner}/{repo}/actions/runs/{id}) and passes the fields here.
#
# The formal-release CI contract is fail-closed. GitHub Actions is a release-validation system:
# pushes and pull requests do not start it. The evidence is the manual validation run. The run
# must be ALL of:
#   * conclusion success;
#   * for exactly the expected commit (full 40-char SHA, no prefix match);
#   * a workflow_dispatch event (push and pull_request runs are NOT release evidence);
#   * on the master branch;
#   * from the workflow file .github/workflows/macos.yml (the path is authoritative; the display
#     name is never the primary identity check).
#
#   --conclusion C     the run's conclusion (want: success)
#   --head-sha H       the commit the run was for (API head_sha)
#   --expected-sha E   the commit the release must be built from (full 40-char SHA)
#   --event V          the event that triggered the run (API event; want: workflow_dispatch)
#   --head-branch B    the branch the run was for (API head_branch; want: master)
#   --workflow-path P  the run's workflow file (API path; want: .github/workflows/macos.yml)
#   --workflow-name W  optional: the run's display name; when given it must also match
#                      "macOS Release Validation" (a name alone never proves the workflow)
#
# Prints PASS/FAIL lines and a RESULT line. Exit 0 when the run is acceptable, 1 otherwise,
# 2 on a usage error (every field except --workflow-name is required).
set -u
prog=${0##*/}
die() { echo "$prog: $*" >&2; exit 2; }

want_event=workflow_dispatch
want_branch=master
want_path=.github/workflows/macos.yml
want_name="macOS Release Validation"

conclusion= head= expected= event= branch= path= name= have_name=0
while [ $# -gt 0 ]; do
	case $1 in
	--conclusion) [ $# -ge 2 ] || die "--conclusion needs a value"; conclusion=$2; shift ;;
	--head-sha) [ $# -ge 2 ] || die "--head-sha needs a value"; head=$2; shift ;;
	--expected-sha) [ $# -ge 2 ] || die "--expected-sha needs a value"; expected=$2; shift ;;
	--event) [ $# -ge 2 ] || die "--event needs a value"; event=$2; shift ;;
	--head-branch) [ $# -ge 2 ] || die "--head-branch needs a value"; branch=$2; shift ;;
	--workflow-path) [ $# -ge 2 ] || die "--workflow-path needs a value"; path=$2; shift ;;
	--workflow-name) [ $# -ge 2 ] || die "--workflow-name needs a value"; name=$2; have_name=1; shift ;;
	-h|--help) sed -n '2,29p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
	*) die "unknown argument: $1" ;;
	esac
	shift
done
[ -n "$conclusion" ] || die "--conclusion is required"
[ -n "$head" ] || die "--head-sha is required"
[ -n "$expected" ] || die "--expected-sha is required"
[ -n "$event" ] || die "--event is required"
[ -n "$branch" ] || die "--head-branch is required"
[ -n "$path" ] || die "--workflow-path is required"

pass=0 fail=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
no() { echo "FAIL $1"; fail=$((fail + 1)); }

if [ "$conclusion" = success ]; then ok "ci-success: run conclusion is success"
else no "ci-success: run conclusion is '$conclusion', not success"; fi

# exact full-SHA match only (case-insensitive); a short or prefix SHA is not proof
lc() { printf '%s' "$1" | tr 'A-F' 'a-f'; }
if ! printf '%s' "$expected" | grep -Eq '^[0-9a-fA-F]{40}$'; then
	no "ci-sha: expected SHA '$expected' is not a full 40-char SHA"
elif ! printf '%s' "$head" | grep -Eq '^[0-9a-fA-F]{40}$'; then
	no "ci-sha: run head '$head' is not a full 40-char SHA"
elif [ "$(lc "$head")" = "$(lc "$expected")" ]; then
	ok "ci-sha: run head $head equals expected"
else
	no "ci-sha: run head $head does NOT equal expected $expected (the run is for another commit)"
fi

if [ "$event" = "$want_event" ]; then ok "ci-event: run was triggered by $want_event"
else no "ci-event: run event is '$event', not $want_event (only a manual workflow_dispatch run is release evidence; push and pull_request runs are not)"; fi

if [ "$branch" = "$want_branch" ]; then ok "ci-branch: run is on $want_branch"
else no "ci-branch: run branch is '$branch', not $want_branch"; fi

if [ "$path" = "$want_path" ]; then ok "ci-workflow-path: run is from $want_path"
else no "ci-workflow-path: run workflow is '$path', not $want_path"; fi

if [ "$have_name" = 1 ]; then
	if [ "$name" = "$want_name" ]; then ok "ci-workflow-name: display name is '$want_name'"
	else no "ci-workflow-name: display name is '$name', not '$want_name'"; fi
fi

echo
if [ "$fail" -gt 0 ]; then echo "RESULT: FAIL ($fail of $((pass + fail)) checks failed)"; exit 1; fi
echo "RESULT: PASS ($pass checks). CI run is acceptable formal-release evidence."
