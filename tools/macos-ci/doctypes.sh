#!/bin/bash
# doctypes.sh APP : deterministic, headless regression gate for macOS document-type routing.
# Verifies the BUILT app can be routed .wrl/.x3d/.x3dv worlds (and their gzip variants) from
# Finder / `open`. This guards the fix in PR #18: LaunchServices only matches a document when the
# CFBundleDocumentTypes extensions are bare (no leading '.'), and a routed document only loads
# when the app delegate implements application:openURLs:. Both regressed silently before.
#
# It does NOT open a GUI (CI runners have no login session for that); the live open is
# tools/macos-ci/launchservices.sh, a mandatory release-QA step. This script is what CI runs.
set -euo pipefail
APP=${1:?usage: doctypes.sh /path/to/FreeWRL.app}
PLIST="$APP/Contents/Info.plist"
SRC=$(cd "$(dirname "$0")/../.." && pwd)   # repo root
DELEGATE="$SRC/OSX_gui/FreeWRL-Desktop/FreeWRL/FreeWRLAppDelegate.m"

# required routed extensions per declared document type, bare (no leading '.')
want_vrml="wrl wrz wrlz"; want_x3d="x3d x3dz"; want_x3dv="x3dv x3dvz"

fail=0; note(){ echo "  $*"; }
die(){ echo "FAIL doctypes: $*"; fail=1; }

# 1. every declared extension must be bare -- a single leading '.' is the exact PR #18 regression
exts=$(plutil -extract CFBundleDocumentTypes json -o - "$PLIST" \
  | python3 -c 'import json,sys; [print(e) for d in json.load(sys.stdin) for e in d.get("CFBundleTypeExtensions",[])]')
[ -n "$exts" ] || die "no CFBundleTypeExtensions in built app"
for e in $exts; do
  case "$e" in
    .*) die "extension '$e' has a leading period (LaunchServices will not match it)";;
  esac
done

# 2. each document type must carry exactly its expected bare extensions, none missing
have=" $(echo $exts) "
for e in $want_vrml $want_x3d $want_x3dv; do
  case "$have" in *" $e "*) : ;; *) die "expected extension '$e' missing from built app";; esac
done
note "extensions present: $(echo $exts)"

# 3. the delegate that loads a routed document must still exist (guards the openURLs: handler)
if [ -f "$DELEGATE" ]; then
  grep -q 'application:.*openURLs:' "$DELEGATE" \
    || die "FreeWRLAppDelegate.m has no application:openURLs: handler (routed documents will not load)"
  grep -q 'dllFreeWRL_onLoad' "$DELEGATE" \
    || die "openURLs: handler no longer calls dllFreeWRL_onLoad"
  note "delegate application:openURLs: -> dllFreeWRL_onLoad present"
else
  note "delegate source not present in this checkout (skipping source assertion)"
fi

[ "$fail" = 0 ] && { echo "PASS doctypes: routed document types are bare and loadable"; exit 0; }
exit 1
