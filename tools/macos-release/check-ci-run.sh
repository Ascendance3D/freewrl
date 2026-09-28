#!/bin/bash
# check-ci-run.sh --conclusion C --head-sha H --expected-sha E --workflow-name W [--expected-workflow X]
# Decide whether a normal CI run is acceptable evidence for a release build. It takes the run's
# already-fetched facts and makes a pure decision; it does no network I/O itself, so it is easy to
# test. The release workflow reads the run with `gh run view` and passes the fields here.
#
#   --conclusion C        the run's conclusion (want: success)
#   --head-sha H          the commit the run was for
#   --expected-sha E      the commit the release must be built from
#   --workflow-name W     the run's workflow name
#   --expected-workflow X the workflow name the run must belong to
#                         (default: "macOS Apple Silicon CI")
#
# Prints PASS/FAIL lines and a RESULT line. Exit 0 when the run is acceptable, 1 otherwise,
# 2 on a usage error.
set -u
prog=${0##*/}
die() { echo "$prog: $*" >&2; exit 2; }

conclusion= head= expected= wf= expected_wf="macOS Apple Silicon CI"
while [ $# -gt 0 ]; do
	case $1 in
	--conclusion) [ $# -ge 2 ] || die "--conclusion needs a value"; conclusion=$2; shift ;;
	--head-sha) [ $# -ge 2 ] || die "--head-sha needs a value"; head=$2; shift ;;
	--expected-sha) [ $# -ge 2 ] || die "--expected-sha needs a value"; expected=$2; shift ;;
	--workflow-name) [ $# -ge 2 ] || die "--workflow-name needs a value"; wf=$2; shift ;;
	--expected-workflow) [ $# -ge 2 ] || die "--expected-workflow needs a value"; expected_wf=$2; shift ;;
	-h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
	*) die "unknown argument: $1" ;;
	esac
	shift
done
[ -n "$conclusion" ] || die "--conclusion is required"
[ -n "$head" ] || die "--head-sha is required"
[ -n "$expected" ] || die "--expected-sha is required"
[ -n "$wf" ] || die "--workflow-name is required"

pass=0 fail=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
no() { echo "FAIL $1"; fail=$((fail + 1)); }

if [ "$conclusion" = success ]; then ok "ci-success: run conclusion is success"
else no "ci-success: run conclusion is '$conclusion', not success"; fi

# accept a full/short match in either direction
if [ "$head" = "$expected" ] || printf '%s' "$head" | grep -iq "^$expected" || printf '%s' "$expected" | grep -iq "^$head"; then
	ok "ci-sha: run head $head matches expected $expected"
else
	no "ci-sha: run head $head does NOT match expected $expected (the run is for another commit)"
fi

if [ "$wf" = "$expected_wf" ]; then ok "ci-workflow: run belongs to '$expected_wf'"
else no "ci-workflow: run belongs to '$wf', not '$expected_wf'"; fi

echo
if [ "$fail" -gt 0 ]; then echo "RESULT: FAIL ($fail of $((pass + fail)) checks failed)"; exit 1; fi
echo "RESULT: PASS ($pass checks). CI run is acceptable release evidence."
