#!/bin/bash
# prepush-light.sh [--all] [--base REF] [--app APP] [--runtime [--seconds N] FIXTURE...]
# Light local checks to run before `git push`: seconds instead of a GitHub Actions round trip.
# They catch shell syntax errors, broken or stale regression fixtures, and drift between a
# fixture and the marker a CI script greps for, and run the host-only C tests and the static
# document-type gate. GitHub Actions stays the final gate. This script never pushes, merges,
# fetches or changes a remote, never installs a git hook, and by default never starts FreeWRL.
# It works from any directory. See tools/macos-ci/README.md.
#   --all        check every regression fixture, not only those changed since the base
#   --base REF   compare with REF (default origin/master, else master; the local ref, not fetched)
#   --app APP    run the document-type gate on this built FreeWRL.app (default: the source Info.plist)
#   --runtime    also start APP (needs --app) on 1 to 3 named FIXTUREs, one at a time, under lldb
#   --seconds N  seconds per fixture with --runtime (default 25, as smoke.sh)
# Prints one PASS, FAIL or SKIP line per check and a RESULT line. Exit status: 0 when no check
# failed (skipped checks are listed, not hidden), 1 when a check failed, 2 on a usage error.
here=$(cd "$(dirname "$0")" && pwd)
die() { echo "prepush-light: $*" >&2; sed -n 2p "$0" | sed 's/^# /usage: /' >&2; exit 2; }
abs() { case $1 in /*) printf '%s\n' "$1" ;; *) printf '%s\n' "$PWD/$1" ;; esac; }

all=0 base= app= runtime=0 seconds=25 fixtures=()
while [ $# -gt 0 ]; do
	case $1 in
	--all) all=1 ;;
	--base) [ $# -ge 2 ] || die "--base needs a git ref"; base=$2; shift ;;
	--app) [ $# -ge 2 ] || die "--app needs a path"; app=$(abs "${2%/}"); shift ;;
	--runtime) runtime=1 ;;
	--seconds) [ $# -ge 2 ] || die "--seconds needs a number"; seconds=$2; shift ;;
	-h|--help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
	-*) die "unknown option $1" ;;
	*) fixtures+=("$(abs "$1")") ;;
	esac
	shift
done
[ -z "$app" ] || [ -d "$app" ] || die "no such app: $app"
if [ $runtime = 1 ]; then
	[ -n "$app" ] || die "--runtime needs --app (a built FreeWRL.app)"
	[ -x "$app/Contents/MacOS/FreeWRL" ] || die "no Contents/MacOS/FreeWRL in $app"
	[ ${#fixtures[@]} -ge 1 ] && [ ${#fixtures[@]} -le 3 ] || die "--runtime takes 1 to 3 fixtures (broad runs belong in CI)"
	for f in "${fixtures[@]}"; do [ -f "$f" ] || die "no such fixture: $f"; done
	case $seconds in '' | *[!0-9]*) die "--seconds needs a whole number" ;; esac
	[ "$seconds" -ge 5 ] && [ "$seconds" -le 120 ] || die "--seconds must be 5 to 120"
elif [ ${#fixtures[@]} -gt 0 ]; then
	die "fixture arguments need --runtime"
fi

root=$(git -C "$here" rev-parse --show-toplevel 2>/dev/null) || die "$here is not in a git checkout"
g() { git -C "$root" "$@"; }
tmpdir=${TMPDIR:-/tmp}; tmpdir=${tmpdir%/}
tmp=$(mktemp -d "$tmpdir/freewrl-prepush.XXXXXX") || exit 2
trap 'rm -rf "$tmp"' EXIT
trap 'exit 130' INT TERM

# what changed: commits since the merge-base with the base, plus uncommitted and untracked files;
# deletions are listed too, and a rename as a deletion and an addition
if [ -n "$base" ]; then
	g rev-parse -q --verify "$base^{commit}" >/dev/null || die "unknown base: $base"
else
	for b in origin/master master; do
		g rev-parse -q --verify "$b^{commit}" >/dev/null && { base=$b; break; }
	done
fi
mb=$([ -n "$base" ] && g merge-base HEAD "$base" 2>/dev/null)
if [ -n "$mb" ]; then
	{ g -c core.quotePath=false diff --name-only --no-renames --diff-filter=ACDMT "$mb" --
	  g -c core.quotePath=false ls-files --others --exclude-standard; } | sort -u > "$tmp/changed"
else
	: > "$tmp/changed"; all=1
fi
read -r n_staged n_unstaged n_untracked <<EOF
$(g --no-optional-locks status --porcelain | awk '/^\?\?/ {u++; next}
	{ if (substr($0, 1, 1) != " ") s++; if (substr($0, 2, 1) != " ") w++ } END { print s + 0, w + 0, u + 0 }')
EOF

echo "prepush-light: light local checks before git push (GitHub Actions stays the final gate)"
echo "  repo:    $root"
echo "  branch:  $(g symbolic-ref --short -q HEAD || echo '(detached HEAD)')"
echo "  HEAD:    $(g rev-parse HEAD)"
if [ -n "$mb" ]; then
	echo "  base:    $base $(g rev-parse --short "$base"), merge-base $(g rev-parse --short "$mb") (local ref, not fetched)"
	echo "  changed: $(wc -l < "$tmp/changed" | tr -d ' ') file(s) since the merge-base (uncommitted and untracked included)"
else
	echo "  base:    none (no origin/master or master, or no common history): every fixture is checked"
fi
if [ $((n_staged + n_unstaged + n_untracked)) = 0 ]; then
	echo "  tree:    clean"
else
	echo "  tree:    dirty: $n_staged staged, $n_unstaged unstaged, $n_untracked untracked" \
		"(checks read the working tree; git push sends only commits)"
fi
if [ $runtime = 1 ]; then echo "  mode:    default checks, then --runtime on ${#fixtures[@]} fixture(s)"
else echo "  mode:    default (static checks; FreeWRL is not started)"; fi
echo

ran=() skipped=() failed=()
record() { # STATUS NAME
	case $1 in
	PASS) ran+=("$2") ;;
	FAIL) ran+=("$2"); failed+=("$2") ;;
	SKIP) skipped+=("$2") ;;
	esac
}
report() { echo "$1 $2: $3"; record "$1" "$2"; }
join() { printf '%s, ' "$@" | sed 's/, $//'; }

# 1. shell syntax: every tools/**/*.sh and every changed shell script, parsed by the shell its #!
#    line names (bash -n without one); scripts under tools/ must also be executable in git
shell_of() { # the Bourne-type shell a #! line names, or nothing
	local first words
	IFS= read -r first < "$1"
	case $first in '#!'*) ;; *) return ;; esac
	read -r -a words <<< "${first#??}"
	[ "${words[0]##*/}" = env ] && words=("${words[@]:1}")
	case ${words[0]##*/} in bash | sh | zsh | dash | ksh)
		command -v "${words[0]}" >/dev/null 2>&1 && echo "${words[0]}" || echo "${words[0]##*/}" ;;
	esac
}
{ g ls-files -- 'tools/*.sh'; g ls-files --others --exclude-standard -- 'tools/*.sh'
  while IFS= read -r f; do
	case $f in *.sh) echo "$f" ;; *) [ -f "$root/$f" ] && [ -n "$(shell_of "$root/$f")" ] && echo "$f" ;; esac
  done < "$tmp/changed"; } | sort -u > "$tmp/scripts"
problems=() nsh=0 nx=0 prefix=$root/
while IFS= read -r f; do
	[ -f "$root/$f" ] || continue
	nsh=$((nsh + 1))
	sh=$(shell_of "$root/$f"); sh=${sh:-bash}
	if ! err=$("$sh" -n "$root/$f" 2>&1); then
		err=${err//"$prefix"/}   # repo-relative paths
		problems+=("$sh -n: $(printf '%s' "$err" | head -3 | tr '\n' ' ')")
	fi
	case $f in tools/*)
		nx=$((nx + 1))
		mode=$(g ls-files -s -- "$f" | cut -c1-6)
		if [ -n "$mode" ]; then
			[ "$mode" = 100755 ] || problems+=("$f: mode $mode in git, not executable (git update-index --chmod=+x $f)")
		else
			[ -x "$root/$f" ] || problems+=("$f: not executable (chmod +x $f)")
		fi ;;
	esac
done < "$tmp/scripts"
if [ ${#problems[@]} = 0 ]; then
	report PASS shell-syntax "$nsh script(s) parse (bash -n, or sh -n/zsh -n as their #! says); $nx under tools/ are executable"
else
	report FAIL shell-syntax "$nsh script(s) checked"
	printf '  - %s\n' "${problems[@]}"
fi

# 2-5. regression fixtures and the fixture/marker contract of the CI scripts (fixtures.py)
names="fixture-xml fixture-metadata fixture-script marker-contract"
if python3 -c 'import sys; sys.exit(sys.version_info < (3, 6))' >/dev/null 2>&1; then
	args=(check --changed "$tmp/changed"); [ $all = 1 ] && args+=(--all)
	python3 "$here/fixtures.py" "${args[@]}" > "$tmp/fixtures" 2>&1
	rc=$? n=0
	while IFS= read -r line; do
		echo "$line"
		case $line in 'PASS '* | 'FAIL '* | 'SKIP '*)
			n=$((n + 1)); name=${line#* }; record "${line%% *}" "${name%%:*}" ;;
		esac
	done < "$tmp/fixtures"
	[ $n = 4 ] || report FAIL fixture-checks "tools/macos-ci/fixtures.py stopped after $n of 4 checks (exit $rc)"
else
	for c in $names; do report SKIP $c "python3 3.6 or newer not found"; done
fi

# 6. host-only C tests (the CI build job's first step)
cc=${CC:-clang}
if ! "$cc" --version >/dev/null 2>&1; then
	report SKIP host-c-tests "C compiler '$cc' not usable (tools/c-tests/run-containers.sh needs clang or CC)"
else
	t0=$(date +%s)
	if "$root/tools/c-tests/run-containers.sh" > "$tmp/c-tests" 2>&1; then
		report PASS host-c-tests "tools/c-tests/run-containers.sh: $(sed -n 's/^== TOTAL: //p' "$tmp/c-tests" | tail -1) ($(($(date +%s) - t0)) s)"
	else
		report FAIL host-c-tests "tools/c-tests/run-containers.sh failed; its last lines:"
		tail -15 "$tmp/c-tests" | sed 's/^/    /'
	fi
fi

# 6a. every GitHub Action the workflows use runs on Node 24 (reads each action.yml through gh)
"$here/actions-runtime.sh" > "$tmp/actions" 2>&1
case $? in
0) report PASS actions-runtime "tools/macos-ci/actions-runtime.sh: $(grep -c '^PASS' "$tmp/actions") action(s) on node24" ;;
1) report FAIL actions-runtime "tools/macos-ci/actions-runtime.sh:"; grep '^FAIL' "$tmp/actions" | sed 's/^/    /' ;;
*) report SKIP actions-runtime "$(tail -1 "$tmp/actions")" ;;
esac

# 7. document-type gate (CI runs it on the built app; without --app, on the source Info.plist,
#    which the build copies with only $(VARIABLES) expanded)
plist=$root/OSX_gui/FreeWRL-Desktop/FreeWRL/FreeWRL-Info.plist
if ! command -v plutil >/dev/null 2>&1; then
	report SKIP doctypes "plutil not found (macOS only)"
elif ! python3 -c '' >/dev/null 2>&1; then
	report SKIP doctypes "python3 not found (doctypes.sh needs it)"
elif [ -z "$app" ] && [ ! -f "$plist" ]; then
	report SKIP doctypes "no ${plist#"$root"/} in this checkout and no --app"
else
	if [ -n "$app" ]; then
		target=$app what="on $app"
	else
		target=$tmp/source/FreeWRL.app what="on the source Info.plist (CI checks the built app; --app does too)"
		mkdir -p "$target/Contents" && cp "$plist" "$target/Contents/Info.plist"
	fi
	if "$here/doctypes.sh" "$target" > "$tmp/doctypes" 2>&1; then
		report PASS doctypes "tools/macos-ci/doctypes.sh $what"
	else
		report FAIL doctypes "tools/macos-ci/doctypes.sh $what"
		sed 's/^/    /' "$tmp/doctypes"
	fi
fi

# 7a. Interface Builder files: ibtool compiles them cleanly, every customClass exists, no unbuilt .xib
if ! command -v ibtool >/dev/null 2>&1; then
	report SKIP xib "ibtool not found (Xcode, macOS only)"
elif "$here/xib-check.sh" > "$tmp/xib" 2>&1; then
	report PASS xib "tools/macos-ci/xib-check.sh: $(grep -c '^PASS' "$tmp/xib") check(s)"
else
	report FAIL xib "tools/macos-ci/xib-check.sh:"
	grep -vE '^(PASS|XIBCHECK)' "$tmp/xib" | sed 's/^/    /'
fi

# 8. optional: start FreeWRL on the named fixtures, one at a time, with smoke.sh's checks
runtime_check() {
	local out bad bad_line f i name o asan res why markers kind value nfail want_fail nasan problems=() summary=()
	echo "WARNING: --runtime starts FreeWRL on this Mac under lldb: ${#fixtures[@]} fixture(s)," \
		"one at a time, about $seconds s each. Keep other FreeWRL windows closed."
	if ! command -v lldb >/dev/null 2>&1; then report SKIP runtime "lldb not found (tools/macos-ci/run.sh needs it)"; return; fi
	if ! python3 -c '' >/dev/null 2>&1; then report SKIP runtime "python3 not found (it reads the CI markers)"; return; fi
	if pgrep -x FreeWRL >/dev/null 2>&1; then
		report SKIP runtime "not started: FreeWRL is already running (pid $(pgrep -x FreeWRL | tr '\n' ' ')); run one at a time"
		return
	fi
	out=$(mktemp -d "$tmpdir/freewrl-prepush-runtime.XXXXXX")
	bad=$(sed -n "s/^BAD='\(.*\)'\$/\1/p" "$here/smoke.sh" | head -1)
	bad=${bad:-'failed to load|problem with (VERTEX|FRAGMENT) shader|GL error|Script error'}
	noise=$(sed -n "s/^NOISE='\(.*\)'\$/\1/p" "$here/smoke.sh" | head -1)
	i=0
	for f in "${fixtures[@]}"; do
		i=$((i + 1)); name=$(basename "$f"); name=${name%.*}; o=$out/$i-$name
		why="" markers=""
		python3 "$here/fixtures.py" expect "$f" > "$o.expect" 2>&1 || why=" CI-markers-unreadable:'$(tail -1 "$o.expect")'"
		asan=halt_on_error=0:abort_on_error=0:log_path=$o.asan   # as suite.sh; unused by a non-ASan build
		res=$(ASAN_OPTIONS=$asan "$here/run.sh" "$app" "$f" "$seconds" "$o")
		echo "  $res"
		echo "$res" | grep -qE 'CRASH:|malloc=[^n]' && why="$why crash-or-allocator-abort"
		echo "$res" | grep -qE 'EXIT:exited with status = [0-8] ' && why="$why early-exit"   # not retried, as smoke.sh
		while IFS=$'\t' read -r kind value; do
			[ "$kind" = marker ] || continue
			markers="$markers '$value'"
			grep -qE -- "$value" "$o.out" "$o.err" 2>/dev/null || why="$why MISSING:'$value'"
		done < "$o.expect"
		want_fail=$(awk -F'\t' '$1 == "expect-fail" { print $2; exit }' "$o.expect")
		if [ -n "$want_fail" ]; then
			nfail=$(cat "$o.out" "$o.err" 2>/dev/null | grep -c "failed to load image")
			[ "$nfail" = "$want_fail" ] || why="$why EXPECTED:$want_fail-load-failures GOT:$nfail"
			bad_line=$(cat "$o.out" "$o.err" 2>/dev/null | grep -E "$bad" | grep -v "failed to load image" | head -1)
		else
			bad_line=$(cat "$o.out" "$o.err" 2>/dev/null | grep -E "$bad" | head -1)
		fi
		[ -z "$bad_line" ] && [ -n "$noise" ] && bad_line=$(cat "$o.out" "$o.err" 2>/dev/null | grep -E "$noise" | head -1)
		[ -n "$bad_line" ] && why="$why BAD:'$bad_line'"
		nasan=$(ls "$o".asan.* 2>/dev/null | wc -l | tr -d ' ')
		[ "$nasan" = 0 ] || why="$why AddressSanitizer-reports:$nasan"
		if [ -n "$why" ]; then problems+=("$name:$why"); fi
		if [ -n "$markers" ]; then summary+=("$name (marker$markers)"); else summary+=("$name (no marker to check)"); fi
	done
	if [ ${#problems[@]} = 0 ]; then
		rm -rf "$out"
		report PASS runtime "$(join "${summary[@]}"): no crash or error, markers present, no ASan report"
	else
		report FAIL runtime "${#fixtures[@]} fixture(s) run; logs kept in $out"
		printf '  - %s\n' "${problems[@]}"
	fi
}
if [ $runtime = 0 ]; then
	report SKIP runtime "not requested (the default mode never starts FreeWRL; see --runtime)"
elif [ ${#failed[@]} -gt 0 ]; then
	report SKIP runtime "not started: fix the failed checks above first"
else
	runtime_check
fi

echo
echo "checks run:     ${#ran[@]} ($(join "${ran[@]}"))"
echo "checks skipped: ${#skipped[@]}${skipped:+ ($(join "${skipped[@]}"))}"
if [ ${#failed[@]} -gt 0 ]; then
	echo "RESULT: FAIL: $(join "${failed[@]}"). Fix before git push."
	exit 1
fi
echo "RESULT: PASS${skipped:+ (${#skipped[@]} skipped, listed above)}. GitHub Actions remains the final gate."
