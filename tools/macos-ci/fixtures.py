#!/usr/bin/env python3
"""Static checks of the regression fixtures and of the tools/macos-ci scripts that run them.

usage: fixtures.py check [--all] [--changed FILE]
       fixtures.py expect FIXTURE

Run by prepush-light.sh. Standard library only; never starts FreeWRL, never uses the network.

check prints one PASS, FAIL or SKIP line per check (problems follow, indented) and exits 1 if
a check failed:
  fixture-xml       fixtures in X3D XML encoding are well-formed
  fixture-metadata  X3D: the profile and <component> declarations cover every node used (a node
                    outside the component table below needs profile Full), every element is a
                    node FreeWRL knows, version matches the DOCTYPE; every fixture:
                    its description (<meta name='description'> or header comment) has a Pass
                    clause, and the markers that clause and the fixture's README entry name are
                    ones the fixture prints; the regression README lists it
  fixture-script    every Browser.<name> a Script uses exists on duktape's Browser object; each
                    success marker (a *_DONE, *_OK, *_PASS ... string) is checked by a CI script
                    and printed only where a result guard (an if/else/switch/catch, ?:, && or ||)
                    decides it prints -- being inside an event handler is not enough, since a
                    handler runs on its event whatever the value
  marker-contract   for every fixture a CI script runs with a marker check (smoke.sh
                    "run NAME WORLD MARKER", suite.sh "texrun NAME-i WORLD" with
                    grep -c "MARKER" over NAME-*.out): the fixture exists and prints that
                    marker, not unconditionally at load time, and its Pass clause quotes it
                    (a log line the engine prints instead, such as "Skinning Method: CPU", must
                    be in the engine source); its success marker is the one checked. Every
                    repository path the scripts build from $H, $R, $SRC, $T or $G exists.
The first three cover the regression fixtures named in FILE (one repo-relative path per line:
the changed and deleted files), or all of them with --all, when FILE names a file they all
depend on (the regression README, the duktape Browser tables, GeneratedCode.c, this script), or
when a regression fixture was deleted or renamed. marker-contract always covers every CI entry.

expect prints what the CI scripts check in FIXTURE's log, for prepush-light.sh --runtime:
"marker<TAB>PATTERN" lines (the fixture's own success markers when no script checks it) and
"expect-fail<TAB>N" when smoke.sh expects N images to fail to load.
"""
import argparse
import fnmatch
import gzip
import html
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zlib

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REG = "freewrl/tests/regression"
README = REG + "/README"
CI = "tools/macos-ci"
DUK = "freex3d/src/lib/world_script/jsVRMLBrowser_duk.c"   # the Browser object Script code sees
NODES_SRC = "freex3d/src/lib/scenegraph/GeneratedCode.c"     # NODES[]: every node FreeWRL parses
SHARED = {README, DUK, NODES_SRC, CI + "/fixtures.py"}
FIXTURE_EXT = (".x3d", ".x3dz", ".wrl", ".wrz", ".wrlz", ".x3dv", ".x3dvz")
XML_EXT = (".x3d", ".x3dz")

# a log marker: upper-case words joined by "_" (ROUTE_OK); a trailing "_" (DUK_DEFNAMES_UPDATE_)
# is a prefix the script completes at run time
MARKER = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+_?(?![A-Za-z0-9])")
SUCCESS = re.compile(r"_(?:DONE|OK|PASS|PASSED|SUCCESS|SUCCEEDED)$")
REGEX_META = re.compile(r"[\\^$.\[\]|()*+?{}]")

# X3D 4.0 nodes by component (ISO/IEC 19775-1); CoordinateDouble moved from NURBS to Rendering
COMPONENTS = {
    "Core": "MetadataBoolean MetadataDouble MetadataFloat MetadataInteger MetadataSet MetadataString WorldInfo",
    "Time": "TimeSensor",
    "Networking": "Anchor Inline LoadSensor",
    "Grouping": "Group StaticGroup Switch Transform",
    "Rendering": "ClipPlane Color ColorRGBA Coordinate CoordinateDouble IndexedLineSet IndexedTriangleFanSet "
                 "IndexedTriangleSet IndexedTriangleStripSet LineSet Normal PointSet Tangent TriangleFanSet "
                 "TriangleSet TriangleStripSet",
    "Shape": "AcousticProperties Appearance FillProperties LineProperties Material PhysicalMaterial "
             "PointProperties Shape TwoSidedMaterial UnlitMaterial",
    "Geometry3D": "Box Cone Cylinder ElevationGrid Extrusion IndexedFaceSet Sphere",
    "Geometry2D": "Arc2D ArcClose2D Circle2D Disk2D Polyline2D Polypoint2D Rectangle2D TriangleSet2D",
    "Text": "FontStyle Text",
    "Sound": "Analyser AudioClip AudioDestination BiquadFilter BufferAudioSource ChannelMerger ChannelSelector "
             "ChannelSplitter Convolver Delay DynamicsCompressor Gain ListenerPointSource MicrophoneSource "
             "OscillatorSource PeriodicWave Sound SpatialSound StreamAudioDestination StreamAudioSource WaveShaper",
    "Lighting": "DirectionalLight EnvironmentLight PointLight SpotLight",
    "Texturing": "ImageTexture MovieTexture MultiTexture MultiTextureCoordinate MultiTextureTransform PixelTexture "
                 "TextureCoordinate TextureCoordinateGenerator TextureProperties TextureTransform",
    "Interpolation": "ColorInterpolator CoordinateInterpolator CoordinateInterpolator2D EaseInEaseOut "
                     "NormalInterpolator OrientationInterpolator PositionInterpolator PositionInterpolator2D "
                     "ScalarInterpolator SplinePositionInterpolator SplinePositionInterpolator2D "
                     "SplineScalarInterpolator SquadOrientationInterpolator",
    "PointingDeviceSensor": "CylinderSensor PlaneSensor SphereSensor TouchSensor",
    "KeyDeviceSensor": "KeySensor StringSensor",
    "EnvironmentalSensor": "ProximitySensor TransformSensor VisibilitySensor",
    "Navigation": "Billboard Collision LOD NavigationInfo OrthoViewpoint Viewpoint ViewpointGroup",
    "EnvironmentalEffects": "Background Fog FogCoordinate LocalFog TextureBackground",
    "Geospatial": "GeoCoordinate GeoElevationGrid GeoLOD GeoLocation GeoMetadata GeoOrigin "
                  "GeoPositionInterpolator GeoProximitySensor GeoTouchSensor GeoTransform GeoViewpoint",
    "HAnim": "HAnimDisplacer HAnimHumanoid HAnimJoint HAnimMotion HAnimSegment HAnimSite",
    "NURBS": "Contour2D ContourPolyline2D CoordinateDouble NurbsCurve NurbsCurve2D NurbsOrientationInterpolator "
             "NurbsPatchSurface NurbsPositionInterpolator NurbsSet NurbsSurfaceInterpolator NurbsSweptSurface "
             "NurbsSwungSurface NurbsTextureCoordinate NurbsTrimmedSurface",
    "DIS": "DISEntityManager DISEntityTypeMapping EspduTransform ReceiverPdu SignalPdu TransmitterPdu",
    "Scripting": "Script",
    "EventUtilities": "BooleanFilter BooleanSequencer BooleanToggle BooleanTrigger IntegerSequencer "
                      "IntegerTrigger TimeTrigger",
    "Shaders": "ComposedShader FloatVertexAttribute Matrix3VertexAttribute Matrix4VertexAttribute PackagedShader "
               "ProgramShader ShaderPart ShaderProgram",
    "CADGeometry": "CADAssembly CADFace CADLayer CADPart IndexedQuadSet QuadSet",
    "Texturing3D": "ComposedTexture3D ImageTexture3D PixelTexture3D TextureCoordinate3D TextureCoordinate4D "
                   "TextureTransform3D TextureTransformMatrix3D",
    "CubeMapTexturing": "ComposedCubeMapTexture GeneratedCubeMapTexture ImageCubeMapTexture",
    "Layering": "Layer LayerSet Viewport",
    "Layout": "Layout LayoutGroup LayoutLayer ScreenFontStyle ScreenGroup",
    "RigidBodyPhysics": "BallJoint CollidableOffset CollidableShape CollisionCollection CollisionSensor "
                        "CollisionSpace Contact DoubleAxisHingeJoint MotorJoint RigidBody RigidBodyCollection "
                        "SingleAxisHingeJoint SliderJoint UniversalJoint",
    "Picking": "LinePickSensor PickableGroup PointPickSensor PrimitivePickSensor VolumePickSensor",
    "Followers": "ColorChaser ColorDamper CoordinateChaser CoordinateDamper OrientationChaser OrientationDamper "
                 "PositionChaser PositionChaser2D PositionDamper PositionDamper2D ScalarChaser ScalarDamper "
                 "TexCoordChaser2D TexCoordDamper2D",
    "ParticleSystems": "BoundedPhysicsModel ConeEmitter ExplosionEmitter ForcePhysicsModel ParticleSystem "
                       "PointEmitter PolylineEmitter SurfaceEmitter VolumeEmitter WindPhysicsModel",
    "VolumeRendering": "BlendedVolumeStyle BoundaryEnhancementVolumeStyle CartoonVolumeStyle ComposedVolumeStyle "
                       "EdgeEnhancementVolumeStyle IsoSurfaceVolumeData OpacityMapVolumeStyle "
                       "ProjectionVolumeStyle SegmentedVolumeData ShadedVolumeStyle "
                       "SilhouetteEnhancementVolumeStyle ToneMappedVolumeStyle VolumeData",
    "TextureProjection": "TextureProjector TextureProjectorParallel",
}
NODE_COMPONENTS = {}
for _component, _nodes in COMPONENTS.items():
    for _node in _nodes.split():
        NODE_COMPONENTS.setdefault(_node, set()).add(_component)
# components each profile includes (levels are not checked); None: all of them
_INTERCHANGE = {"Core", "Time", "Networking", "Grouping", "Rendering", "Shape", "Geometry3D", "Lighting",
                "Texturing", "Interpolation", "Navigation", "EnvironmentalEffects"}
_INTERACTIVE = _INTERCHANGE | {"PointingDeviceSensor", "KeyDeviceSensor", "EnvironmentalSensor", "EventUtilities"}
PROFILES = {"Core": {"Core"}, "Interchange": _INTERCHANGE, "Interactive": _INTERACTIVE,
            "Immersive": _INTERACTIVE | {"Geometry2D", "Text", "Sound", "Scripting"}, "Full": None}
UNCHECKED_PROFILES = {"CADInterchange", "MedicalInterchange", "MPEG-4 interactive", "MPEG4Interactive"}
X3D_VERSIONS = {"3.0", "3.1", "3.2", "3.3", "4.0", "4.1"}
STRUCTURAL = {"X3D", "head", "meta", "component", "unit", "Scene", "ROUTE", "IS", "connect", "field",
              "fieldValue", "ProtoDeclare", "ProtoInterface", "ProtoBody", "ProtoInstance",
              "ExternProtoDeclare", "IMPORT", "EXPORT"}

failed = False


def result(name, problems, summary, notes=()):
    global failed
    print("%s %s: %s" % ("FAIL" if problems else "PASS", name, summary))
    for p in problems:
        print("  - " + p)
    for n in notes:
        print("  note: " + n)
    failed = failed or bool(problems)


def skip(name, reason):
    print("SKIP %s: %s" % (name, reason))


def read_data(path):
    """The file's bytes; gzip-compressed fixtures are inflated (FreeWRL reads them whatever their name)."""
    with open(path, "rb") as f:
        data = f.read()
    return gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data


def read_source(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def attributes(text):
    return {m.group(1): m.group(2) if m.group(2) is not None else m.group(3)
            for m in re.finditer(r"([\w:-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", text)}


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def scan_js(src):
    """(code, strings): src with comments and string contents blanked (same length, so offsets agree)
    and [(value, start, end)] for each string literal."""
    code, strings, i, n = [], [], 0, len(src)
    while i < n:
        if src.startswith("//", i) or src.startswith("/*", i):
            j = src.find("\n", i) if src[i + 1] == "/" else src.find("*/", i + 2)
            j = n if j < 0 else (j if src[i + 1] == "/" else j + 2)
            code.append(re.sub(r"[^\n]", " ", src[i:j]))
            i = j
        elif src[i] in "\"'":
            q, j = src[i], i + 1
            while j < n and src[j] != q and src[j] != "\n":
                j += 2 if src[j] == "\\" else 1
            j = min(j, n)
            closed = j < n and src[j] == q
            body = src[i + 1:j]
            strings.append((re.sub(r"\\(.)", r"\1", body, flags=re.S), i, j + closed))
            code.append(q + " " * len(body) + (q if closed else ""))
            i = j + closed
        else:
            code.append(src[i])
            i += 1
    return "".join(code), strings


FUNCTION = re.compile(r"\bfunction\b\s*(\w*)\s*\(")
GUARD = re.compile(r"(?:if|else|switch|catch)\b")


def statement_context(code, pos):
    """(function, guarded) for the statement at offset pos: the innermost enclosing function's name
    ("" if anonymous, None at top level), and whether an if/else/switch/catch, ?:, && or || decides
    whether the statement runs."""
    blocks, start, depth = [], 0, 0
    for i in range(pos):
        c = code[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth = max(depth - 1, 0)
        elif c == "{":
            blocks.append(code[start:i].strip())
            start = i + 1
        elif c == "}":
            if blocks:
                blocks.pop()
            start = i + 1
        elif c == ";" and depth == 0:
            start = i + 1
    statement = code[start:pos].strip()
    guarded = bool(GUARD.match(statement) or re.search(r"\?|&&|\|\|", statement))
    for header in reversed(blocks):
        m = FUNCTION.search(header)
        if m:
            name = m.group(1)
            if not name:
                a = re.search(r"(\w+)\s*[:=]\s*function\b", header)
                name = a.group(1) if a else ""
            return name, guarded
        guarded = guarded or bool(GUARD.match(header))
    return None, guarded


class Script:
    """One Script body: its JavaScript, the file line it starts on, and the events that call it."""

    def __init__(self, js, line, handlers):
        self.js, self.line, self.handlers = js, line, handlers
        self.code, self.strings = scan_js(js)

    def line_of(self, offset):
        return self.line + self.js.count("\n", 0, offset)

    def unverified(self, offset):
        """Why a marker printed at offset proves only that the code ran, or None.

        A result guard is the only proof: the marker prints where an if/else/switch/catch, ?:,
        && or || decides whether it runs (statement_context sets `guarded`), so it is tied to a
        checked result. Being inside an event handler is not proof: the handler runs whenever its
        event is delivered, whatever the value, so a marker it prints unconditionally says only
        that the event arrived, not that the result was right."""
        func, guarded = statement_context(self.code, offset)
        if guarded:
            return None
        if func is None:
            return "unconditionally at load time"
        if func in self.handlers:
            return "unconditionally in event handler " + func + "() (the handler runs on the event " \
                   "whatever its value; guard the marker on the checked result)"
        return "unconditionally in " + (func + "()" if func else "an anonymous function")


def input_events(declarations):
    """Names of the functions events call: eventsProcessed, and one per inputOnly/inputOutput field."""
    names = {"eventsProcessed"}
    for access, name in declarations:
        names.add(name)
        if access in ("inputOutput", "exposedField"):
            names.add("set_" + name)
    return names


class Fixture:
    def __init__(self, rel):
        self.rel = rel
        self.path = os.path.join(ROOT, rel)
        self.exists = os.path.isfile(self.path)
        self.data, self.read_error = b"", None   # read_error: a normal FAIL of the checks, not a traceback
        if self.exists:
            try:
                self.data = read_data(self.path)
            except (OSError, EOFError, zlib.error) as e:   # unreadable, or truncated or corrupt gzip data
                self.read_error = "cannot be read: %s: %s" % (type(e).__name__, e)
        self.text = self.data.decode("utf-8", "replace")
        self.xml = rel.lower().endswith(XML_EXT)
        self.root = self.xml_error = None
        if self.xml and self.exists and not self.read_error:
            try:
                self.root = ET.fromstring(self.data)
            except (ET.ParseError, LookupError) as e:   # LookupError: an unknown encoding= declaration
                self.xml_error = str(e)
        self.scripts = self._scripts()
        self.literals = [(v, s, start, end) for s in self.scripts for v, start, end in s.strings]
        self.tokens = {}   # marker token -> (script, offset) of the first literal holding it
        for v, s, start, _ in self.literals:
            for t in MARKER.findall(v):
                self.tokens.setdefault(t, (s, start))

    def _line(self, offset):
        return self.text.count("\n", 0, offset) + 1

    def _scripts(self):
        text, out = self.text, []
        if self.xml:
            for m in re.finditer(r"<Script\b([^>]*?)(?:/>|>(.*?)</Script\s*>)", text, re.S):
                inner = m.group(2) or ""
                fields = [attributes(f.group(1)) for f in re.finditer(r"<field\b([^>]*)>", inner)]
                handlers = input_events((a.get("accessType"), a.get("name")) for a in fields
                                        if a.get("accessType") in ("inputOnly", "inputOutput") and a.get("name"))
                for c in re.finditer(r"<!\[CDATA\[(.*?)\]\]>", inner, re.S):
                    out.append(Script(c.group(1), self._line(m.start(2) + c.start(1)), handlers))
                url = html.unescape(attributes(m.group(1)).get("url", ""))
                for u in re.finditer(r"\"((?:java|ecma|vrml)script:(?:[^\"\\]|\\.)*)\"", url, re.S):
                    out.append(Script(re.sub(r"\\(.)", r"\1", u.group(1), flags=re.S), self._line(m.start()), handlers))
        else:
            handlers = input_events(re.findall(r"\b(eventIn|inputOnly|exposedField|inputOutput)\s+\w+\s+(\w+)", text))
            for u in re.finditer(r"\"((?:java|ecma|vrml)script:(?:[^\"\\]|\\.)*)\"", text, re.S):
                out.append(Script(re.sub(r"\\(.)", r"\1", u.group(1), flags=re.S), self._line(u.start(1)), handlers))
        return out

    def description(self):
        """<meta name='description'> content (XML), or the header comment after the #VRML/#X3D line."""
        if self.root is not None:
            return next((el.get("content") or "" for el in self.root.iter()
                         if local(el.tag) == "meta" and el.get("name") == "description"), None)
        if self.xml:   # not well-formed: best effort
            for m in re.finditer(r"<meta\b([^>]*)>", self.text):
                a = attributes(m.group(1))
                if a.get("name") == "description":
                    return html.unescape(a.get("content") or "")
            return None
        comments = []
        for line in self.text.splitlines()[1:]:
            if not line.startswith("#"):
                break
            comments.append(line[1:].strip())
        return " ".join(comments) or None

    def success(self):
        return sorted(t for t in self.tokens if SUCCESS.search(t))

    def prints(self, token):
        """Whether a string literal holds token, or a prefix of it the script completes (UPDATE_ + i)."""
        return any(t == token or (t.endswith("_") and token.startswith(t) and token[len(t):].isalnum())
                   for t in self.tokens)

    def find(self, expect):
        """How the fixture prints what a CI script greps for: ("exact", script, offset) when a string
        literal contains it, ("value", ...) when a literal is its fixed start and the script appends
        the rest (the grep then checks a computed value), or None."""
        hit = next(((s, start) for v, s, start, _ in self.literals if contains(v, expect)), None)
        if hit:
            return ("exact",) + hit
        if not REGEX_META.search(expect):
            for v, s, start, end in self.literals:
                if MARKER.search(v) and expect.startswith(v) and len(expect) > len(v) and re.match(r"\s*\+", s.code[end:]):
                    return ("value", s, start)
        return None


def contains(text, expect):
    """Whether text holds what `grep -E expect` matches; a plain word-edged expect must not run into
    more word characters (ROUTE_OK does not match ROUTE_OKAY)."""
    if REGEX_META.search(expect):
        try:
            return re.search(expect, text) is not None
        except re.error:
            return False
    edge_l = r"(?<!\w)" if re.match(r"\w", expect) else ""
    edge_r = r"(?!\w)" if re.search(r"\w$", expect) else ""
    return re.search(edge_l + re.escape(expect) + edge_r, text) is not None


def pass_clause(description):
    """The sentence of a description that says what a pass looks like ("Pass: ..." or "Expected ...: ...")."""
    m = re.search(r"\b(?:Pass|Expected[^:.]{0,40}):", description or "")
    if not m:
        return None
    rest = description[m.start():]
    end = re.search(r"\.(?=\s|$)", rest)
    return rest[:end.end()] if end else rest


def engine_file(text):
    """A tracked engine or app source that prints this log text (a printf may supply its value), or None."""
    fixed = re.split(REGEX_META, text)[0] if REGEX_META.search(text) else text
    candidates = [fixed] + [fixed[:fixed.rfind(sep) + len(sep)] for sep in (": ", "=") if fixed.rfind(sep) > 0]
    for c in candidates:
        if len(c) < 6:
            continue
        r = subprocess.run(["git", "-C", ROOT, "grep", "-l", "-F", "-e", c, "--", "freex3d/src", "OSX_gui"],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.splitlines()[0]
    return None


def table(text, name):
    """The quoted names in a C table such as FWFunctionSpec (BrowserFunctions)[] = { {"getName", ...}, ... };"""
    m = re.search(r"\(" + name + r"\)\[\]\s*=\s*\{(.*?)\n\};", text, re.S)
    return set(re.findall(r"^\s*\{\s*\"(\w+)\"", m.group(1), re.M)) if m else set()


def freewrl_nodes():
    m = re.search(r"const char \*NODES\[\]\s*=\s*\{(.*?)\};", read_source(NODES_SRC), re.S)
    return set(re.findall(r"\"(\w+)\"", m.group(1))) if m else set()


def regression_fixtures():
    out = []
    for d, dirs, files in os.walk(os.path.join(ROOT, REG)):
        dirs.sort()
        out += [os.path.relpath(os.path.join(d, f), ROOT) for f in sorted(files) if f.lower().endswith(FIXTURE_EXT)]
    return out


def readme_entries():
    """[pattern, text] per fixture line of the regression README (text includes indented continuation lines)."""
    entries, current = [], None
    for line in read_source(README).splitlines():
        m = re.match(r"(\S+\.(?:x3dv?z?|wrl|wrlz|wrz))\s", line + " ")
        if m:
            current = [m.group(1), line[m.end():].strip()]
            entries.append(current)
        elif current and line[:1].isspace() and line.strip():
            current[1] += " " + line.strip()
        else:
            current = None
    return entries


# ---------------------------------------------------------------------------------------------
# CI scripts

ASSIGN = re.compile(r"(?:^|(?<=[\s;]))([A-Za-z_]\w*)=(\$\(cd .+? && pwd\)|\"[^\"\n]*\"|[^\s;]+)", re.M)
RUN = re.compile(r"^[ \t]*run[ \t]+(\w+)[ \t]+(\"[^\"\n]*\"|\S+)[ \t]+(\"[^\"\n]*\"|'[^'\n]*'|\S+)"
                 r"(?:[ \t]+(\d+))?[ \t]*(?:#.*)?$", re.M)
TEXRUN = re.compile(r"\btexrun[ \t]+\"(\w+)-[^\"\n]*\"[ \t]+(\"[^\"\n]*\"|\S+)")
GATE = re.compile(r"\"\$OUT\"/(\w+)-\*\.(?:out|err)\b[^|\n]*\|[ \t]*grep[ \t]+-c[ \t]+(\"[^\"\n]+\"|'[^'\n]+')")


class Entry:
    """One fixture run by a CI script, with what the script greps for in its log (None: nothing)."""

    def __init__(self, script, line, name, world, expect, expect_fail):
        self.script, self.line, self.name = script, line, name
        self.world, self.expect, self.expect_fail = world, expect, expect_fail

    @property
    def where(self):
        return "%s:%d (%s)" % (self.script, self.line, self.name)


def shell_vars(text, script_dir):
    """Directories a CI script derives from its own location: H=$(cd "$(dirname "$0")" && pwd),
    R=$(cd "$H/../.." && pwd), T=$R/freewrl/tests, G=$T/regression ... as {name: absolute path}."""
    values = {}
    for m in ASSIGN.finditer(text):
        v = m.group(2)
        if v.startswith("$(cd "):
            v = v[len("$(cd "):-len(" && pwd)")]
        v = v.replace('"$(dirname "$0")"', script_dir).replace('$(dirname "$0")', script_dir).strip('"')
        v = re.sub(r"\$\{?(\w+)\}?", lambda r: values.get(r.group(1), "\0"), v)
        if "\0" not in v and v.startswith("/"):
            values[m.group(1)] = os.path.normpath(v)
    return values


def ci_scripts():
    """(entries, missing paths, number of paths checked) for tools/macos-ci/*.sh."""
    entries, missing, npaths = [], [], 0
    for name in sorted(os.listdir(os.path.join(ROOT, CI))):
        if not name.endswith(".sh"):
            continue
        rel = CI + "/" + name
        text = read_source(rel)
        values = shell_vars(text, os.path.join(ROOT, CI))

        def world(word):
            w = re.sub(r"\$\{?(\w+)\}?", lambda r: values.get(r.group(1), "\0"), word.strip("\"'"))
            return os.path.relpath(os.path.normpath(w), ROOT) if "\0" not in w and w.startswith("/") else None

        def line(pos):
            return text.count("\n", 0, pos) + 1

        for m in RUN.finditer(text):
            want = m.group(3).strip("\"'")
            entries.append(Entry(rel, line(m.start()), m.group(1), world(m.group(2)), None if want == "-" else want,
                                 int(m.group(4)) if m.group(4) else None))
        gates = {}
        for m in GATE.finditer(text):
            gates.setdefault(m.group(1), []).append(m.group(2).strip("\"'"))
        for m in TEXRUN.finditer(text):
            for want in gates.get(m.group(1), [None]):
                entries.append(Entry(rel, line(m.start()), m.group(1) + "-*", world(m.group(2)), want, None))
        for m in re.finditer(r"\$\{?(\w+)\}?/([\w.+-]+(?:/[\w.+-]+)*)", text):
            base = values.get(m.group(1))
            if not base or text[m.end():m.end() + 1] in ("*", "?", "[", "$"):
                continue
            path = os.path.normpath(os.path.join(base, m.group(2)))
            if not path.startswith(ROOT + os.sep):
                continue
            npaths += 1
            if not os.path.exists(path):
                missing.append("%s:%d: %s does not exist" % (rel, line(m.start()), os.path.relpath(path, ROOT)))
    return entries, missing, npaths


# ---------------------------------------------------------------------------------------------
# checks

def check_xml(scope, hint):
    xml = [f for f in scope if f.xml]
    if not xml:
        return skip("fixture-xml", "no X3D XML fixture in scope" + hint)
    problems = ["%s: %s" % (f.rel, f.read_error or "not well-formed XML: " + f.xml_error)
                for f in xml if f.read_error or f.xml_error]
    result("fixture-xml", problems, "%d X3D XML fixture(s) parsed" % len(xml))


def x3d_problems(f, root, known_nodes, notes):
    tag = local(root.tag)
    if tag != "X3D":
        return ["%s: the root element is <%s>, not <X3D>" % (f.rel, tag)]
    problems = []
    profile, version = root.get("profile"), root.get("version")
    if not version:
        problems.append("%s: <X3D> has no version attribute" % f.rel)
    elif version not in X3D_VERSIONS:
        problems.append("%s: version='%s' is not an X3D version" % (f.rel, version))
    else:
        prolog = re.split(r"<(?:head|Scene)\b", f.text, maxsplit=1)[0]   # XML declaration, DOCTYPE, <X3D ...>
        for m in re.finditer(r"DTD X3D (\d+\.\d+)|x3d-(\d+\.\d+)\.(?:dtd|xsd)", prolog):
            if (m.group(1) or m.group(2)) != version:
                problems.append("%s: version='%s' but its %s says %s (stale header)" % (
                    f.rel, version, "DOCTYPE" if m.group(1) else "DTD/schema URL", m.group(1) or m.group(2)))
                break
    declared = {c.get("name") for c in root.iter() if local(c.tag) == "component"}
    for c in sorted(str(d) for d in declared if d not in COMPONENTS):
        problems.append("%s: <component name='%s'> is not an X3D component" % (f.rel, c))
    allowed = None
    if not profile:
        problems.append("%s: <X3D> has no profile attribute" % f.rel)
    elif profile in PROFILES:
        allowed = PROFILES[profile] and PROFILES[profile] | declared
    elif profile in UNCHECKED_PROFILES:
        notes.append("%s: nodes not checked against profile '%s' (no table for it here)" % (f.rel, profile))
    else:
        problems.append("%s: profile='%s' is not an X3D profile" % (f.rel, profile))
    unknown, unmapped, outside = set(), set(), {}
    for el in root.iter():
        name = local(el.tag)
        if not name or name in STRUCTURAL:
            continue
        if known_nodes and name not in known_nodes:
            unknown.add(name)
        elif name not in NODE_COMPONENTS:
            unmapped.add(name)
        elif allowed and not NODE_COMPONENTS[name] & allowed:
            outside[name] = sorted(NODE_COMPONENTS[name])
    for name in sorted(unknown):
        problems.append("%s: <%s> is not a node FreeWRL knows (NODES[] in %s)" % (f.rel, name, NODES_SRC))
    for name in sorted(unmapped) if allowed else ():
        problems.append("%s: <%s> is in no X3D component of the table here (a FreeWRL extension or a newer X3D "
                        "node), so only profile='Full' covers it, not '%s'" % (f.rel, name, profile))
    if outside:
        need = {c for comps in outside.values() for c in comps} - (allowed or set())
        fit = next((p for p in ("Interchange", "Interactive", "Immersive") if need <= PROFILES[p]), "Full")
        for name, comps in sorted(outside.items()):
            problems.append("%s: <%s> belongs to the %s component, which profile '%s' does not include; declare "
                            "profile='%s' or add <component name='%s' level='...'/>" % (
                                f.rel, name, "/".join(comps), profile, fit, comps[0]))
    return problems


def check_metadata(scope, all_scope, hint):
    if not scope:
        return skip("fixture-metadata", "no regression fixture in scope" + hint)
    problems, notes = [], []
    known_nodes = freewrl_nodes()
    if not known_nodes:
        notes.append("element names not checked: no NODES[] table found in " + NODES_SRC)
    readme = readme_entries()
    for f in scope:
        if f.read_error:
            problems.append("%s: %s" % (f.rel, f.read_error))
            continue
        if f.root is not None:
            problems += x3d_problems(f, f.root, known_nodes, notes)
        elif f.xml:
            notes.append("%s: profile, version and nodes not checked (not well-formed XML)" % f.rel)
        what = "<meta name='description'>" if f.xml else "header comment"
        description = f.description()
        clause = pass_clause(description)
        if not description:
            problems.append("%s: no %s that says what a pass looks like" % (f.rel, what))
        elif clause is None:
            problems.append("%s: its %s has no 'Pass:' clause" % (f.rel, what))
        else:
            for t in MARKER.findall(clause):
                if not f.prints(t) and not engine_file(t):
                    problems.append("%s: the Pass clause names %s, which the fixture never prints (stale)" % (f.rel, t))
        texts = [text for pattern, text in readme if fnmatch.fnmatchcase(os.path.basename(f.rel), pattern)]
        if not texts:
            problems.append("%s: not listed in %s" % (f.rel, README))
        for text in texts:
            for t in MARKER.findall(text):
                if not f.prints(t) and not engine_file(t):
                    problems.append("%s: its %s entry names %s, which the fixture never prints (stale)" % (f.rel, README, t))
    if all_scope:
        names = [os.path.basename(r) for r in regression_fixtures()]
        for pattern, _ in readme:
            if not any(fnmatch.fnmatchcase(n, pattern) for n in names):
                problems.append("%s lists %s, which is not in %s" % (README, pattern, REG))
    result("fixture-metadata", problems, "%d regression fixture(s) checked" % len(scope), notes)


def check_script(scope, checked, hint):
    if not scope:
        return skip("fixture-script", "no regression fixture in scope" + hint)
    source = read_source(DUK)
    browser = table(source, "BrowserFunctions") | table(source, "BrowserProperties")
    context = table(source, "X3DExecutionContextFunctions") | table(source, "X3DExecutionContextProperties")
    problems, notes = [], []
    if not browser:
        notes.append("Browser.* names not checked: no BrowserFunctions/BrowserProperties table found in " + DUK)
    for f in scope:
        for s in f.scripts:
            for m in re.finditer(r"\bBrowser\s*\.\s*([A-Za-z_$][\w$]*)", s.code):
                if browser and m.group(1) not in browser:
                    problems.append("%s:%d: Browser.%s does not exist on the duktape Browser object (%s)%s" % (
                        f.rel, s.line_of(m.start()), m.group(1), DUK,
                        "; it is an X3DExecutionContext member: use Browser.currentScene.%s" % m.group(1)
                        if m.group(1) in context else ""))
        for t in f.success():
            if (f.rel, t) in checked:
                continue   # marker-contract checks it
            s, offset = f.tokens[t]
            problems.append("%s:%d: prints success marker %s, but no %s script checks it" % (
                f.rel, s.line_of(offset), t, CI))
            why = s.unverified(offset)
            if why:
                problems.append("%s:%d: success marker %s is printed %s; print it only after checking the result" % (
                    f.rel, s.line_of(offset), t, why))
    result("fixture-script", problems, "%d regression fixture(s), %d Script body(ies)" % (
        len(scope), sum(len(f.scripts) for f in scope)), notes)


def check_contract(entries, missing, npaths):
    problems, notes, fixtures = list(missing), [], {}
    greps = engine = 0
    for e in entries:
        if e.world is None:
            notes.append("%s: world path not resolved; not checked" % e.where)
            continue
        f = fixtures.setdefault(e.world, Fixture(e.world))
        if not f.exists:
            problems.append("%s: runs %s, which does not exist" % (e.where, e.world))
            continue
        if f.read_error:
            problems.append("%s: runs %s, which %s" % (e.where, e.world, f.read_error))
            continue
        success = f.success()
        if e.expect is None:
            if success:
                problems.append("%s: runs %s without a marker check, but the fixture prints %s on success" % (
                    e.where, e.world, ", ".join(success)))
            continue
        greps += 1
        how = f.find(e.expect)
        if how is None:
            if engine_file(e.expect):
                engine += 1
            else:
                problems.append("%s: greps for '%s', which %s never prints (nor does the engine source)" % (
                    e.where, e.expect, e.world))
            continue
        kind, s, offset = how
        wanted = MARKER.findall(e.expect)
        if success and not set(success) & set(wanted):
            problems.append("%s: greps for '%s', but %s reports success with %s; check that exact marker" % (
                e.where, e.expect, e.world, ", ".join(success)))
        why = s.unverified(offset) if kind == "exact" else None
        if why:
            problems.append("%s: greps for '%s', which %s:%d prints %s: that proves only that the script ran; "
                            "print it after checking the result" % (e.where, e.expect, e.world, s.line_of(offset), why))
        clause = pass_clause(f.description())
        if clause is None or not contains(clause, e.expect):
            problems.append("%s: the Pass clause of %s does not quote '%s', the text the script greps for (stale)" % (
                e.where, e.world, e.expect))
    result("marker-contract", problems, "%d CI script entries, %d marker greps (%d of engine log lines), %d paths" % (
        len(entries), greps, engine, npaths), notes)


def check(args):
    changed = []
    if args.changed:
        with open(args.changed, encoding="utf-8", errors="replace") as f:
            changed = [line.strip() for line in f if line.strip()]
    fixtures = regression_fixtures()
    gone = [c for c in changed if c.startswith(REG + "/") and c.lower().endswith(FIXTURE_EXT)
            and not os.path.exists(os.path.join(ROOT, c))]   # deleted, or the old name of a rename
    shared = sorted(SHARED & set(changed)) + gone
    if args.all or shared:
        names, hint = fixtures, ""
        print("fixture scope: all %d regression fixtures (%s)" % (len(fixtures), "--all" if args.all else
                                                                   "changed: " + ", ".join(shared)))
    else:
        names = [c for c in changed if c in set(fixtures)]
        hint = " (none changed since the base; --all checks every fixture)"
        print("fixture scope: %d changed of %d regression fixtures" % (len(names), len(fixtures)))
    scope = [Fixture(n) for n in names]
    entries, missing, npaths = ci_scripts()
    checked = {(e.world, t) for e in entries if e.expect for t in MARKER.findall(e.expect)}
    check_xml(scope, hint)
    check_metadata(scope, bool(args.all or shared), hint)
    check_script(scope, checked, hint)
    check_contract(entries, missing, npaths)
    return 1 if failed else 0


def expect(args):
    rel = os.path.relpath(os.path.realpath(args.fixture), ROOT)
    mine = [e for e in ci_scripts()[0] if e.world == rel]
    wants = []
    for e in mine:
        if e.expect and e.expect not in wants:
            wants.append(e.expect)
    if not wants:
        f = Fixture(rel)
        if f.read_error:
            print("%s: %s" % (rel, f.read_error), file=sys.stderr)
            return 1
        wants = f.success()
    for w in wants:
        print("marker\t" + w)
    for n in sorted({e.expect_fail for e in mine if e.expect_fail is not None}):
        print("expect-fail\t%d" % n)
    return 0


def main():
    ap = argparse.ArgumentParser(description="Static checks of the regression fixtures and the CI scripts.")
    sub = ap.add_subparsers(dest="command")
    c = sub.add_parser("check")
    c.add_argument("--all", action="store_true", help="check every regression fixture, not only changed ones")
    c.add_argument("--changed", metavar="FILE", help="file listing the changed paths, one per line")
    e = sub.add_parser("expect")
    e.add_argument("fixture")
    args = ap.parse_args()
    if args.command == "check":
        return check(args)
    if args.command == "expect":
        return expect(args)
    ap.print_usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
