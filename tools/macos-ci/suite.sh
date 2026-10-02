#!/bin/bash
# suite.sh APP OUTDIR KIND   (KIND: release | asan)
# One FreeWRL at a time: world-replacement cycles (PROTO worlds among others), then the texture
# fixtures repeatedly. Prints one line per run and a gate summary; exits 1 if the gate fails.
#   CYC  replacement cycles, CSEC seconds each (the world is replaced every 90 frames, while
#        the pointer, driven by reloader.py, hovers and presses whatever is under it)
#   TEX  runs of texture_formats.wrl, TSTB runs of texture_formats_stb.wrl, TSEC seconds each;
#        then one run of particles_maxparticles.x3d (TSEC seconds)
# Gate: no crash, no allocator abort, no texture "failed to load" or GL/shader error; every
# cycle made at least one world replacement and sent pointer events (a reloader.py fault --
# not armed, a failed load or pointer call -- fails the gate: a run that replaced nothing
# proves nothing); sensor_replace.wrl's sensors fired under the pointer; with asan, no
# AddressSanitizer report at all. Reports are counted per defect class (PROTO lifetime,
# Frustum extent stack, Vector, GLCore client attributes, other) so a regression names its class.
# Nothing is retried: a run that exits cleanly before its window fails the gate like a crash, an
# allocator abort, an AddressSanitizer report or a texture/shader error (the early exit was a
# world load turned into a quit, fixed in MainLoop.c fwl_draw, PR #53).
H=$(cd "$(dirname "$0")" && pwd); R=$(cd "$H/../.." && pwd)
APP=$1 OUT=$2 KIND=$3; mkdir -p "$OUT"
T=$R/freewrl/tests; G=$T/regression
# replaced in turn; 8.wrl, 10.wrl, proto_replace.wrl, gzip_proto.wrl and sensor_replace.wrl
# declare PROTOs (no audio); sensor_replace.wrl puts pointing-device sensors under the pointer
export RELOAD_PATHS="$T/8.wrl:$G/texture_formats.wrl:$T/10.wrl:$G/proto_replace.wrl:$T/1.wrl:$T/16.wrl:$G/text_fonts.wrl:$G/route_dotted.wrl:$G/hanim_skin.x3d:$G/gzip_proto.wrl:$G/sensor_replace.wrl:$G/texture_formats_stb.wrl:$G/glcore_stale_attribs.wrl"
export RELOAD_POINTER=300,300
if [ "$KIND" = asan ]; then
	export ASAN_OPTIONS=halt_on_error=0:abort_on_error=0:log_path=$OUT/asan
	CYC=${CYC:-2} CSEC=${CSEC:-120} TEX=${TEX:-3} TSTB=${TSTB:-2} TSEC=${TSEC:-30}
else
	CYC=${CYC:-2} CSEC=${CSEC:-120} TEX=${TEX:-10} TSTB=${TSTB:-5} TSEC=${TSEC:-25}
fi
BAD='failed to load|problem with (VERTEX|FRAGMENT) shader|GL error'
for ((i=1; i<=CYC; i++)); do RELOAD_PERIOD=90 "$H/run.sh" "$APP" "$G/texture_formats.wrl" $CSEC "$OUT/cycle-$i"; done | tee "$OUT/cycles.txt"
unset RELOAD_PATHS RELOAD_POINTER
texrun() { # name world : one texture run
	"$H/run.sh" "$APP" "$2" $TSEC "$OUT/$1"
}
{
for ((i=1; i<=TEX; i++)); do texrun "texture-$i" "$G/texture_formats.wrl"; done
for ((i=1; i<=TSTB; i++)); do texrun "texstb-$i" "$G/texture_formats_stb.wrl"; done
# ParticleSystem maxParticles raised 4 -> 2000 at run time (particle Vector growth), once per suite
texrun "particles-1" "$G/particles_maxparticles.x3d"
# X3DExecutionContext createNode + updateNamedNode append path (duktape), functional smoke, once per suite
texrun "defnames-1" "$G/duktape_defnames.x3d"
} | tee "$OUT/textures.txt"

fail=0
crashes=$(cat "$OUT/cycles.txt" "$OUT/textures.txt" | grep -c 'CRASH:')
mallocs=$(cat "$OUT/cycles.txt" "$OUT/textures.txt" | grep -vc 'malloc=none')
# any run (cycle or texture) that exited by itself before its window
early=$(cat "$OUT/cycles.txt" "$OUT/textures.txt" | grep -cE 'EXIT:exited with status = [0-8] ')
reloads=$(grep -o 'reloads=[0-9]*' "$OUT/cycles.txt" | cut -d= -f2 | paste -sd+ - | bc)
# every cycle must have replaced the world (reloads=0 means the harness never drove the app)
# and must be free of harness faults
cycidle=$(grep -vcE 'reloads=[1-9]' "$OUT/cycles.txt")
harness=$(grep -c 'HARNESS:' "$OUT/cycles.txt")
pointer=$(grep -o 'pointer-events=[0-9]*' "$OUT/cycles.txt" | cut -d= -f2 | paste -sd+ - | bc)
texbad=$(cat "$OUT"/texture-*.out "$OUT"/texture-*.err "$OUT"/texstb-*.out "$OUT"/texstb-*.err 2>/dev/null | grep -cE "$BAD")
cycbad=$(cat "$OUT"/cycle-*.out "$OUT"/cycle-*.err 2>/dev/null | grep -cE "$BAD")
# the particles run must have raised maxParticles (its Script reads the new value back)
particles=$(cat "$OUT"/particles-*.out "$OUT"/particles-*.err 2>/dev/null | grep -c "PARTICLES_MAXPARTICLES_READBACK max=2000")
# the defnames run must have added all six DEF names through updateNamedNode
defnames=$(cat "$OUT"/defnames-*.out "$OUT"/defnames-*.err 2>/dev/null | grep -c "DUK_DEFNAMES_DONE")
# the pointer must have driven sensor_replace.wrl's SphereSensor in the cycles (picking ran)
sensors=$(cat "$OUT"/cycle-*.out "$OUT"/cycle-*.err 2>/dev/null | grep -o "SENSOR_SPHERE" | wc -l | tr -d ' ')
echo "GATE runs: $CYC cycles (${reloads:-0} world replacements, ${pointer:-0} pointer events, cycles without a replacement: $cycidle, harness faults: $harness), $TEX texture_formats + $TSTB texture_formats_stb runs, 1 particles run (maxParticles raised: $particles), 1 defnames run (updateNamedNode: $defnames), sensors driven by the pointer: $sensors"
echo "GATE crashes=$crashes allocator-aborts=$mallocs texture-errors=$texbad cycle-errors=$cycbad early-clean-exits=$early"
[ "$crashes" = 0 ] && [ "$mallocs" = 0 ] && [ "$texbad" = 0 ] && [ "$cycbad" = 0 ] && [ "$early" = 0 ] && [ "$particles" -ge 1 ] && [ "$defnames" -ge 1 ] \
	&& [ "${reloads:-0}" -ge 1 ] && [ "$cycidle" = 0 ] && [ "$harness" = 0 ] && [ "${pointer:-0}" -ge 1 ] && [ "$sensors" -ge 1 ] || fail=1
if [ "$KIND" = asan ]; then
	# Each report is classified by its first FreeWRL frame (the SUMMARY line names only the
	# faulting frame, which for a memcpy is the sanitizer itself). One line per report.
	PROTO='gc_broto_instance|startOfLoopNodeUpdates|getTypeNode|hasSiblingAffectorField|walk_fields|freeMallocedNodeFields|deleteVector_'
	FRUSTUM='extent6f_union_extent6f Frustum.c'
	VECTOR='vector_removeElement Vector.c'
	GLCORE='upload_client_attribs GLCoreCompat.c|fw_core_glDraw(Arrays|Elements) GLCoreCompat.c'
	DUKDEF='X3DExecutionContext_updateNamedNode jsVRMLBrowser_duk.c'
	cat "$OUT"/asan.* 2>/dev/null | grep '^SUMMARY' | sort | uniq -c > "$OUT/asan-summary.txt"
	cat "$OUT"/asan.* 2>/dev/null | awk '
		/^==[0-9]+==ERROR: AddressSanitizer:/ { if (kind != "") print kind, frame; kind=$3; frame="(no FreeWRL frame)"; found=0; next }
		/^    #[0-9]+ / && !found && $0 !~ /libclang_rt|wrap_|__asan|GLEngine|libsystem|libobjc/ { found=1; frame=$4 " " $5 }
		END { if (kind != "") print kind, frame }' | sort | uniq -c > "$OUT/asan-frames.txt"
	proto=$(grep -E "$PROTO" "$OUT/asan-frames.txt" | awk '{s+=$1} END {print s+0}')
	frustum=$(grep -E "$FRUSTUM" "$OUT/asan-frames.txt" | awk '{s+=$1} END {print s+0}')
	vector=$(grep -E "$VECTOR" "$OUT/asan-frames.txt" | awk '{s+=$1} END {print s+0}')
	glcore=$(grep -E "$GLCORE" "$OUT/asan-frames.txt" | awk '{s+=$1} END {print s+0}')
	dukdef=$(grep -E "$DUKDEF" "$OUT/asan-frames.txt" | awk '{s+=$1} END {print s+0}')
	total_asan=$(awk '{s+=$1} END {print s+0}' "$OUT/asan-frames.txt")
	other=$((total_asan - proto - frustum - vector - glcore - dukdef))
	echo "ASan reports (count, kind, place):"; sed 's/^/  /' "$OUT/asan-summary.txt"
	echo "ASan reports by first FreeWRL frame:"; sed 's/^/  /' "$OUT/asan-frames.txt"
	echo "GATE asan PROTO=$proto Frustum=$frustum Vector=$vector GLCore=$glcore DUKdef=$dukdef Other=$other Total=$total_asan"
	[ "$total_asan" = 0 ] || fail=1
fi
[ $fail = 0 ] && echo "GATE PASS" || echo "GATE FAIL"
exit $fail
