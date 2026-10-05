"""Node data for vrmlc.py.

This is the Python form of VRMLNodes.pm.

NODE_SOURCE lists the node definitions in source order. Each entry is:

    (key, name, fields, x3d_node_type)

Each field is:

    (field_name, field_type, default, kind, spec, unca)

The field order is the order of the members of struct X3D_<key>, so it is
part of the C ABI. Do not reorder fields.

A default is the exact text that Perl made from the VRMLNodes.pm value:
a str, None (Perl undef), or a tuple of such values. For example, Perl
writes .5 as "0.5", 1.0 as "1" and 0.0 as "0". Keep defaults as text.
Python must not format these numbers again.

GeoTMParameters occurs two times. Perl keeps the last definition, so
load_nodes() does the same. The first definition has no effect.

"name" is the second argument of the Perl constructor. vrmlc.py does not
use it.

Note from VRMLNodes.pm: the VRML parser REQUIRES for routing that each
field name exists in only one table. For example, "value" can be made an
inputOutput field when the spec says initializeOnly. This has little if
any effect on parsing.

SPEC_VRML tag verified against
http://web3d.org/x3d/specifications/vrml/ISO-IEC-14772-VRML97/part1/nodesRef.html
"""

import re
from typing import NamedTuple

from vrml_fields import FIELD_TYPES

NODE_SOURCE = (
    ###################################################################################

    # chapter 7:        Core Component

    ###################################################################################

    ("WorldInfo", "WorldInfo", (
        ("info", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("title", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DChildNode"),

    # "ProtoInclude" => new VRML::NodeType("ProtoInclude", [
    #       metadata => ["SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
    #       names => ["MFString",["*"],"initializeOnly", 0,0],#ff
    #       url => ["MFString",[]","initializeOnly", 0,0"],#ff
    # ], "X3DChildNode"),

    ("Proto", "Proto", (
        # sept 2014: keep Inline the same as Proto, so one can be cast to the other, unless/until executionContext is extracted from both
        ("__children", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__protoDeclares", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__externProtoDeclares", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__nodes", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__subcontexts", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__GC", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__protoDef", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),  # user fields
        ("__protoFlags", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__prototype", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # first node in protobody
        ("__parentProto", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # first node in protobody
        ("__ROUTES", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__EXPORTS", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__IMPORTS", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__DEFnames", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__IS", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__scripts", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__META", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__oldurl", "MFString", (), "initializeOnly", "0", "0"),
        ("__afterPound", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__typename", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("__unitlengthfactor", "SFDouble", "1", "initializeOnly", "0", "0"),
        ("__specversion", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DProtoInstance"),

    ("MetadataBoolean", "MetadataBoolean", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("reference", "SFString", "", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value", "MFBool", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
    ), "X3DChildNode"),

    ("MetadataInteger", "MetadataInteger", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("reference", "SFString", "", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
    ), "X3DChildNode"),

    ("MetadataDouble", "MetadataDouble", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file:
        ("reference", "SFString", "", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
    ), "X3DChildNode"),

    ("MetadataFloat", "MetadataFloat", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("reference", "SFString", "", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
    ), "X3DChildNode"),

    ("MetadataString", "MetadataString", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("reference", "SFString", "", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
    ), "X3DChildNode"),

    ("MetadataSet", "MetadataSet", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("reference", "SFString", "", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
    ), "X3DChildNode"),

    ###################################################################################

    # Chapter 8:        Time Component

    ###################################################################################

    ("TimeSensor", "TimeSensor", (
        ("cycleInterval", "SFTime", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("loop", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("cycleTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fraction_changed", "SFFloat", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("time", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30)", "UNCA_NONE"),

        # time that we were initialized at
        ("__inittime", "SFTime", "0", "initializeOnly", "0", "0"),
        # cycleTimer flag.
        ("__ctflag", "SFTime", "10", "inputOutput", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
    ), "X3DSensorNode"),

    ###################################################################################

    # Chapter 9:        Networking Component

    ###################################################################################

    ("Anchor", "Anchor", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("parameter", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # load and refresh fields have no effect with Anchor node, they come with URL
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("refresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DGroupingNode"),

    ("Inline", "Inline", (
        # sept 2014: keep Inline the same as Proto, so one can be cast to the other, unless/until executionContext is extracted from both
        ("__children", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__protoDeclares", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__externProtoDeclares", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__nodes", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__subcontexts", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__GC", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__protoDef", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),  # user fields
        ("__protoFlags", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__prototype", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # first node in protobody
        ("__parentProto", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # first node in protobody
        ("__ROUTES", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__EXPORTS", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__IMPORTS", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__DEFnames", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__IS", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__scripts", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__META", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__oldurl", "MFString", (), "initializeOnly", "0", "0"),
        ("__afterPound", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__typename", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("__unitlengthfactor", "SFDouble", "1", "initializeOnly", "0", "0"),
        ("__specversion", "SFInt32", "0", "initializeOnly", "0", "0"),
        # inline-specific
        ("refresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        # load => ["SFBool", "TRUE","initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        # metadata => ["SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        # url => ["MFString", [], "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        # bboxCenter => ["SFVec3f", [0, 0, 0], "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        # bboxSize => ["SFVec3f", [-1, -1, -1], "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff

        # __children => ["MFNode", [], "inputOutput", 0,0],#ff
        # __loadstatus =>["SFInt32",0,"initializeOnly", 0],
        # _parentResource =>["FreeWRLPTR",0,"initializeOnly", 0,0],#ff
        # __loadResource => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
    ), "X3DNetworkSensorNode"),

    ("LoadSensor", "LoadSensor", (
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("timeOut", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("watchList", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("isActive", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isLoaded", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("loadTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("progress", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("__loading", "SFBool", "TRUE", "initializeOnly", "0", "0"),  # current internal status
        ("__finishedloading", "SFBool", "TRUE", "initializeOnly", "0", "0"),  # current internal status
        ("__StartLoadTime", "SFTime", "0", "outputOnly", "0", "0"),  # time we started loading...
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DNetworkSensorNode"),

    ###################################################################################

    # Chapter 10:       Grouping Component

    ###################################################################################

    ("Group", "Group", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
    ), "X3DGroupingNode"),

    ("StaticGroup", "StaticGroup", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("__transparency", "SFInt32", "-1", "initializeOnly", "0", "0"),  # display list for transparencies
        ("__solid", "SFInt32", "-1", "initializeOnly", "0", "0"),  # display list for solid geoms.
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
    ), "X3DGroupingNode"),

    ("Switch", "Switch", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("choice", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30)", "UNCA_NONE"),  # VRML nodes....
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # X3D nodes....
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("whichChoice", "SFInt32", "-1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("__isX3D", "SFBool", "(inputFileVersion[0]==3)", "initializeOnly", "0", "0"),  # "TRUE" for X3D V3.x files
    ), "X3DGroupingNode"),

    ("Transform", "Transform", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("scale", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("scaleOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # fields for reducing redundant calls
        ("__do_center", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_trans", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_rotation", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_scaleO", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_scale", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_anything", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
    ), "X3DGroupingNode"),

    ###################################################################################

    # Chapter 11:       Rendering Component

    ###################################################################################

    ("ClipPlane", "ClipPlane", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("plane", "SFVec4f", ("0", "1", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_PLANE"),

    ), "X3DChildNode"),

    ("Color", "Color", (
        ("color", "MFColor", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

    ), "X3DColorNode"),

    ("ColorRGBA", "ColorRGBA", (
        ("color", "MFColorRGBA", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

    ), "X3DColorNode"),

    ("Coordinate", "Coordinate", (
        ("point", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

    ), "X3DCoordinateNode"),

    ("CoordinateDouble", "CoordinateDouble", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("point", "MFVec3d", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
    ), "X3DCoordinateNode"),

    ("IndexedLineSet", "IndexedLineSet", (
        ("set_colorIndex", "MFInt32", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_coordIndex", "MFInt32", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorIndex", "MFInt32", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coordIndex", "MFInt32", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__vertArr", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__vertIndx", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__starts", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__counts", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__segCount", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__xcolours", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__xfog", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__vertices", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__vertexCount", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__skindex", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("LineSet", "LineSet", (
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vertexCount", "MFInt32", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__vertArr", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__vertIndx", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__starts", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # __counts  =>["FreeWRLPTR",0,"initializeOnly", 0,0],#ff
        ("__segCount", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__skindex", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("IndexedTriangleFanSet", "IndexedTriangleFanSet", (
        ("set_index", "MFInt32", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("index", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("IndexedTriangleSet", "IndexedTriangleSet", (
        ("set_index", "MFInt32", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("index", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("IndexedTriangleStripSet", "IndexedTriangleStripSet", (
        ("set_index", "MFInt32", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("index", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Normal", "Normal", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vector", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DNormalNode"),

    ("PointSet", "PointSet", (
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DGeometryNode"),

    ("TriangleFanSet", "TriangleFanSet", (
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fanCount", "MFInt32", ("3",), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("TriangleStripSet", "TriangleStripSet", (
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stripCount", "MFInt32", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),

    ), "X3DGeometryNode"),

    ("TriangleSet", "TriangleSet", (
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("BufferGeometry", "BufferGeometry", (
        # all done via _intern field
    ), "X3DGeometryNode"),

    ###################################################################################

    #   Chapter 12:     Shape Component

    ###################################################################################

    ("Appearance", "Appearance", (
        ("fillProperties", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("lineProperties", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pointProperties", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("acousticProperties", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("material", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("backMaterial", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shaders", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("effects", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureTransform", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DAppearanceNode"),

    ("AcousticProperties", "AcousticProperties", (
        ("absorption", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("specular", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("diffuse", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("refraction", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DAppearanceChildNode"),

    ("FillProperties", "FillProperties", (
        ("filled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hatchColor", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hatched", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hatchStyle", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_enabled", "SFBool", "TRUE", "inputOutput", "0", "0"),  # literally, is this thing used or not?
        ("_hatchScale", "SFVec2f", ("0.1", "0.1"), "inputOutput", "0", "0"),  # the rate of the lines, 0.1 = 10 lines/meter
    ), "X3DAppearanceChildNode"),

    ("LineProperties", "LineProperties", (
        ("applied", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("linetype", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("linewidthScaleFactor", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("type16dashes", "MFFloat", "0", "inputOutput", "0", "0"),
        ("type16wiggles", "MFVec2f", "NULL", "inputOutput", "0", "0"),
        ("styleStart", "SFString", "NONE", "inputOutput", "0", "0"),
        ("styleEnd", "SFString", "NONE", "inputOutput", "0", "0"),
        ("__styleStart", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__styleEnd", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__style16", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DAppearanceChildNode"),

    # v4 draft has PointProperties https://www.web3d.org/specifications/X3Dv4Draft/ISO-IEC19775-1v4-WD1/
    ("PointProperties", "PointProperties", (
        ("pointSizeScaleFactor", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("pointSizeMinValue", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("pointSizeMaxValue", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("attenuation", "MFFloat", ("1", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("markerType", "SFInt32", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # colorMode => ["SFString", "POINT_COLOR", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("_colormode", "SFInt32", "1", "inputOutput", "0", "0"),
        ("_attenuation", "SFVec3f", ("1", "0", "0"), "inputOutput", "0", "0"),
        ("_pointMethod", "SFInt32", "1", "inputOutput", "0", "0"),
    ), "X3DAppearanceChildNode"),

    # v4 https://github.com/michaliskambi/x3d-tests/wiki/X3D-version-4:-New-features-of-materials,-lights-and-textures#new-x3dmaterialnode-node-with-emissive-and-normalmap-textures

    ("Material", "Material", (
        # base class Material
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("emissiveColor", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("emissiveTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # emissiveTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("emissiveTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("normalScale", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("normalTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # normalTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("normalTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("transparency", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_material", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),

        ("occlusionStrength", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("occlusionTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("occlusionTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # this class Material
        ("ambientIntensity", "SFFloat", "0.2", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ambientTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # ambientTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("ambientTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("diffuseColor", "SFColor", ("0.8", "0.8", "0.8"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("diffuseTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # diffuseTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("diffuseTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("shininess", "SFFloat", "0.2", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shininessTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # specularShininessTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("shininessTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("specularColor", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("specularTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # specularShininessTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("specularTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DMaterialNode"),

    ("PhysicalMaterial", "PhysicalMaterial", (
        # base class Material
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("emissiveColor", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("emissiveTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # emissiveTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("emissiveTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("normalScale", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("normalTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # normalTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("normalTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("transparency", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_material", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),

        ("occlusionStrength", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("occlusionTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("occlusionTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # this class Material
        # X3DOM convention https://github.com/x3dom/x3dom/blob/master/src/nodes/Shape/PhysicalMaterial.js
        ("baseColor", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("baseTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # baseTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("baseTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("metallic", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("roughness", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("metallicRoughnessTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # metallicRoughnessTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("metallicRoughnessTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DMaterialNode"),

    ("UnlitMaterial", "UnlitMaterial", (
        # base class Material
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("emissiveColor", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("emissiveTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # emissiveTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("emissiveTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("normalScale", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("normalTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # normalTextureChannel => ["SFInt32", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)","UNCA_NONE"],#ff
        ("normalTextureMapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("transparency", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_material", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DMaterialNode"),

    ("Shape", "Shape", (
        # shared with particlesystem, keep in same order as particlesystem:
        ("appearance", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geometry", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("castShadow", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_shaderflags_base", "SFDouble", "0", "initializeOnly", "0", "0"),  # shaders
        ("_shaderflags_effects", "SFInt32", "0", "initializeOnly", "0", "0"),  # shaders
        ("_shaderflags_usershaders", "SFInt32", "0", "initializeOnly", "0", "0"),  # shaders
        # shape-specific:
        ("__visible", "SFInt32", "0", "initializeOnly", "0", "0"),  # for Occlusion tests.
        ("__occludeCheckCount", "SFInt32", "-1", "initializeOnly", "0", "0"),  # for Occlusion tests.
        ("__Samples", "SFInt32", "-1", "initializeOnly", "0", "0"),  # Occlude samples from last pass

    ), "X3DBoundedObject"),

    # deprecated in v4? see new Appearance.backMaterial field
    ("TwoSidedMaterial", "TwoSidedMaterial", (
        ("ambientIntensity", "SFFloat", "0.2", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("backAmbientIntensity", "SFFloat", "0.2", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("backDiffuseColor", "SFColor", ("0.8", "0.8", "0.8"), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("backEmissiveColor", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("backShininess", "SFFloat", "0.2", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("backSpecularColor", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("backTransparency", "SFFloat", "0", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("diffuseColor", "SFColor", ("0.8", "0.8", "0.8"), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("emissiveColor", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("shininess", "SFFloat", "0.2", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("separateBackColor", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("specularColor", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("transparency", "SFFloat", "0", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("_material", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_backMaterial", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),

    ), "X3DMaterialNode"),

    ###################################################################################

    # Chapter 13:       Geometry3D Component

    ###################################################################################

    ("Box", "Box", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("size", "SFVec3f", ("2", "2", "2"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__points", "MFVec3f", (), "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Cone", "Cone", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bottom", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("bottomRadius", "SFFloat", "1", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("height", "SFFloat", "2", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("side", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sidepoints", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__botpoints", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__normals", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__coneVBO", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__coneTriangles", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__wireindices", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Cylinder", "Cylinder", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bottom", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("height", "SFFloat", "2", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("radius", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("side", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("top", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("__points", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__normals", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__cylinderVBO", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__cylinderTriangles", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__wireindices", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("ElevationGrid", "ElevationGrid", (
        ("set_height", "MFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("creaseAngle", "SFFloat", "0", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("height", "MFFloat", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("xDimension", "SFInt32", "0", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("xSpacing", "SFFloat", "1", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("zDimension", "SFInt32", "0", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("zSpacing", "SFFloat", "1", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Extrusion", "Extrusion", (
        ("set_crossSection", "MFVec2f", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_orientation", "MFRotation", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_scale", "MFVec2f", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_spine", "MFVec3f", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("beginCap", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("convex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("creaseAngle", "SFFloat", "0", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("crossSection", "MFVec2f", (("1", "1"), ("1", "-1"), ("-1", "-1"), ("-1", "1"), ("1", "1")), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("endCap", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation", "MFRotation", (("0", "0", "1", "0"),), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),  # see note top of file
        ("scale", "MFVec2f", (("1", "1"),), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("spine", "MFVec3f", (("0", "0", "0"), ("0", "1", "0")), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DGeometryNode"),

    ("IndexedFaceSet", "IndexedFaceSet", (
        ("set_colorIndex", "MFInt32", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_coordIndex", "MFInt32", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_normalIndex", "MFInt32", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_texCoordIndex", "MFInt32", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorIndex", "MFInt32", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("convex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coordIndex", "MFInt32", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("creaseAngle", "SFFloat", "0", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("normalIndex", "MFInt32", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoordIndex", "MFInt32", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DGeometryNode"),

    ("Sphere", "Sphere", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("radius", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__points", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("_sideVBO", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__SphereIndxVBO", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__pindices", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__wireindicesVBO", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Teapot", "Teapot", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__ifsnode", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Pyramid", "Pyramid", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__ifsnode", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ###################################################################################

    #   Chapter 14: Geometry 2D Component

    ###################################################################################

    ("Arc2D", "Arc2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("endAngle", "SFFloat", "1.5707", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("radius", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("startAngle", "SFFloat", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("__points", "MFVec2f", (), "initializeOnly", "0", "0"),
        ("__numPoints", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("ArcClose2D", "ArcClose2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("closureType", "SFString", "PIE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("endAngle", "SFFloat", "1.5707", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("radius", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("solid", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startAngle", "SFFloat", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("__points", "MFVec2f", (), "initializeOnly", "0", "0"),
        ("__texCoords", "MFVec2f", (), "initializeOnly", "0", "0"),
        ("__numPoints", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__simpleDisk", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("__wireindices", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Circle2D", "Circle2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("radius", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("__points", "MFVec2f", (), "initializeOnly", "0", "0"),
        ("__numPoints", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Disk2D", "Disk2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("innerRadius", "SFFloat", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("outerRadius", "SFFloat", "1", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("solid", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__points", "MFVec2f", (), "initializeOnly", "0", "0"),
        ("__texCoords", "MFVec2f", (), "initializeOnly", "0", "0"),
        ("__numPoints", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__simpleDisk", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("__wireindices", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("Polyline2D", "Polyline2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("lineSegments", "MFVec2f", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
    ), "X3DGeometryNode"),

    ("Polypoint2D", "Polypoint2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("point", "MFVec2f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
    ), "X3DGeometryNode"),

    ("Rectangle2D", "Rectangle2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("size", "SFVec2f", ("2", "2"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("solid", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__points", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__numPoints", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("TriangleSet2D", "TriangleSet2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vertices", "MFVec2f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("solid", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__texCoords", "MFVec2f", (), "initializeOnly", "0", "0"),
        ("__wireindices", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ###################################################################################

    #   Chapter 15:     Text Component

    ###################################################################################

    ("Text", "Text", (
        ("fontStyle", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("length", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("maxExtent", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("string", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("lineBounds", "MFVec2f", (), "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("origin", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textBounds", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_isScreen", "SFInt32", "0", "inputOutput", "0", "0"),  # > 0 for screenfont
        ("_screendata", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),  # screentext rowvec
    ), "X3DTextNode"),

    ("FontStyle", "FontStyle", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("family", "MFString", ("SERIF",), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("horizontal", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("justify", "MFString", ("BEGIN",), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("language", "SFString", "", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("leftToRight", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("size", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("spacing", "SFFloat", "1", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("style", "SFString", "PLAIN", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("topToBottom", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DFontStyleNode"),

    ###################################################################################

    #   Chapter 16:     Sound Component

    ###################################################################################

    ("Analyser", "Analyser", (
        # X3DSoundProcessingNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # Analyzer
        ("fftSize", "SFInt32", "2048", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("frequencyBinCount", "SFInt32", "1024", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("minDecibels", "SFFloat", "-100", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("maxDecibels", "SFFloat", "-30", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("smoothingTimeConstant", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("byteFrequencyData", "MFInt32", (), "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("floatFrequencyData", "MFFloat", (), "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("byteTimeDomainData", "MFInt32", (), "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("floatTimeDomainData", "MFFloat", (), "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundProcessingNode"),

    ("AudioClip", "AudioClip", (

        # X3DUrlObject
        ("autoRefresh", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("autoRefreshTimeLimit", "SFTime", "3600", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # description => ["SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # internal sequence number, openal buffer number
        ("__sourceNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),

        # X3DSoundSourceNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__context_paused", "SFBool", "FALSE", "initializeOnly", "0", "0"),

        # AudioClip
        ("loop", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pitch", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration_changed", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
        # time that we were initialized at
        ("__inittime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),

        #       #movietexture compatible SoundSource section
        #       connect => ["MFNode", [], "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        #       _self => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
        #       _context => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
        #       description => ["SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       enabled => ["SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        #       loop => ["SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       metadata => ["SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       pauseTime => ["SFTime",0,"inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       pitch => ["SFFloat", 1.0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       resumeTime => ["SFTime",0,"inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       startTime => ["SFTime", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       stopTime => ["SFTime", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       url => ["MFString", [], "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       elapsedTime => ["SFTime",0,"outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       isActive => ["SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       isPaused => ["SFBool", "FALSE","outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       _parentResource =>["FreeWRLPTR",0,"initializeOnly", 0,0],#ff
        #       __oldEnabled => ["SFBool", "TRUE", "inputOutput", 0,0],#ff
        #       __loadstatus =>["SFInt32",0,"initializeOnly", 0,0],#ff
        #       __loadResource => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
        #       # internal sequence number, openal buffer number
        #       __sourceNumber => ["SFInt32", -1, "initializeOnly", 0,0],#ff
        #       # time that we were initialized at
        #       __inittime => ["SFTime", 0, "initializeOnly", 0,0],#ff
        #       __lasttime => ["SFTime", 0, "initializeOnly", 0,0],#ff
        #       # local name, as received on system
        #       # old audio __localFileName => ["FreeWRLPTR", 0,"initializeOnly", 0,0],#ff

    ), "X3DSoundSourceNode"),

    ("AudioBuffer", "AudioBuffer", (

        # X3DUrlObject - same order as AudioClip to share resource fetching code
        ("autoRefresh", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("autoRefreshTimeLimit", "SFTime", "3600", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # description => ["SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # internal sequence number, openal buffer number
        ("__sourceNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),

        # X3DSoundNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),

        # PCM float buffer
        ("buffer", "MFFloat", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bufferChannels", "SFInt32", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bufferLength", "SFInt32", "0", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bufferDuration", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

    ), "X3DSoundNode"),

    ("AudioDestination", "AudioDestination", (
        # X3DSoundDestinationNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # AudioDestination
        ("maxChannelCount", "SFInt32", "2", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("mediaDeviceID", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundDestinationNode"),

    ("BiquadFilter", "BiquadFilter", (
        # X3DSoundProcessingNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # BiquadFilter
        ("detune", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("frequency", "SFFloat", "350", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("qualityFactor", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("type", "SFString", "lowpass", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundProcessingNode"),

    ("BufferAudioSource", "BufferAudioSource", (
        # X3DSoundSourceNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__context_paused", "SFBool", "FALSE", "initializeOnly", "0", "0"),

        # AudioBufferSource
        ("detune", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("loop", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("loopStart", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("loopEnd", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("playbackRate", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # AudioBuffer
        ("buffer", "SFNode", "0", "initializeOnly", "0", "0"),

        ("bufferDuration", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
        # time that we were initialized at
        ("__inittime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        # internal sequence number, openal buffer number
        ("__sourceNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),

    ), "X3DSoundSourceNode"),

    ("ChannelMerger", "ChannelMerger", (
        # X3DSoundChannelNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("indexStream", "MFInt32", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("indexSource", "MFInt32", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("indexDestination", "MFInt32", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("selectors", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # ChannelMerger
    ), "X3DSoundChannelNode"),

    ("ChannelSelector", "ChannelSelector", (
        # X3DSoundChannelNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # ChannelSelector
        ("channelSelection", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("lastChannelSelection", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # proposal 3: Selector as 3-tuple
        ("channelSource", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_lastChannelSource", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelDestination", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_lastChannelDestination", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("stream", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_lastStream", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_initialized", "SFInt32", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundChannelNode"),

    ("ChannelSplitter", "ChannelSplitter", (
        # X3DSoundChannelNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # ChannelSplitter
        # outputs => ["MFNode", [], "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
    ), "X3DSoundChannelNode"),

    ("Convolver", "Convolver", (
        # X3DSoundProcessingNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # Convolver
        # buffer => ["MFFloat", "[]", "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        ("buffer", "SFNode", "0", "initializeOnly", "0", "0"),
        ("normalize", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundProcessingNode"),

    ("Delay", "Delay", (
        # X3DSoundProcessingNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # Delay
        ("delayTime", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("maxDelayTime", "SFTime", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundProcessingNode"),

    ("DynamicsCompressor", "DynamicsCompressor", (
        # X3DSoundProcessingNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # DynamicsCompressor
        ("attack", "SFTime", "0.003", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("release", "SFTime", "0.25", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("knee", "SFFloat", "30", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("ratio", "SFFloat", "12", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("threshold", "SFFloat", "-24", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("reduction", "SFFloat", "0", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundProcessingNode"),

    ("Gain", "Gain", (
        # X3DSoundProcessingNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # Gain
    ), "X3DSoundProcessingNode"),

    ("ListenerPointSource", "ListenerPointSource", (
        # X3DSoundSourceNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__context_paused", "SFBool", "FALSE", "initializeOnly", "0", "0"),

        # ListenerPointSource
        ("dopplerEnabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("interauralDistance", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("trackCurrentView", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("position", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSoundSourceNode"),

    ("ListenerPoint", "ListenerPoint", (
        # X3DSoundNode
        # simpler variant replaces context.listener == viewpoint 0,0,0 so panner nodes are wrt listenerpoint instead of viewpoint
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),

        # ListenerPoint
        # dopplerEnabled => ["SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        # interauralDistance => ["SFFloat", 0, "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        ("trackCurrentView", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("position", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("visualization", "SFNode", "0", "inputOutput", "0", "0"),
    ), "X3DSoundNode"),

    ("MicrophoneSource", "MicrophoneSource", (
        # X3DSoundSourceNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__context_paused", "SFBool", "FALSE", "initializeOnly", "0", "0"),

        # MicrophoneSource
        ("mediaDeviceID", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundSourceNode"),

    ("OscillatorSource", "OscillatorSource", (
        # X3DSoundSourceNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__context_paused", "SFBool", "FALSE", "initializeOnly", "0", "0"),

        # OscillatorSource
        ("detune", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("frequency", "SFFloat", "440", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("type", "SFString", "sine", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("periodicWave", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
        # time that we were initialized at
        ("__inittime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),

    ), "X3DSoundSourceNode"),

    ("PeriodicWave", "PeriodicWave", (
        # X3DSoundNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # PeriodicWave
        ("optionsReal", "MFFloat", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("optionsImag", "MFFloat", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("type", "SFString", "sine", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundNode"),

    ("Sound", "Sound", (
        # X3DSoundNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("direction", "SFVec3f", ("0", "0", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("location", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        # openal sound source number
        ("__sourceNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),
        ("__lastlocation", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("__lastdirection", "SFVec3f", ("0", "0", "1"), "initializeOnly", "0", "0"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("__velocity", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__dopplerFactor", "SFFloat", "1", "inputOutput", "0", "0"),
        # Sound
        ("spatialize", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("priority", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxBack", "SFFloat", "10", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("maxFront", "SFFloat", "10", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("minBack", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("minFront", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("source", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSoundNode"),

    ("SpatialSound", "SpatialSound", (
        # X3DSoundNode - keep same as above Sound node for a few shared functions
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("direction", "SFVec3f", ("0", "0", "1"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("location", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # openal sound source number
        ("__sourceNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),
        ("__lastlocation", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("__lastdirection", "SFVec3f", ("0", "0", "1"), "initializeOnly", "0", "0"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("__velocity", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__dopplerFactor", "SFFloat", "1", "inputOutput", "0", "0"),
        # SpatialSound
        ("spatialize", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("priority", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("coneInnerAngle", "SFFloat", "6.2832", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("coneOuterAngle", "SFFloat", "6.2832", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("coneOuterGain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("distanceModel", "SFString", "INVERSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("dopplerEnabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("enableHRTF", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("maxDistance", "SFFloat", "10000", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("referenceDistance", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("rolloffFactor", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundNode"),

    ("StreamAudioDestination", "StreamAudioDestination", (
        # X3DSoundDestinationNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # StreamAudioDestination
        ("streamIdentifier", "MFString", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundDestinationNode"),

    ("StreamAudioSource", "StreamAudioSource", (
        # X3DSoundSourceNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__context_paused", "SFBool", "FALSE", "initializeOnly", "0", "0"),

        # StreamAudioSource
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelCountMode", "SFString", "smax", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakders", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("streamIdentifier", "MFString", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundSourceNode"),

    ("WaveShaper", "WaveShaper", (
        # X3DSoundProcessingNode
        ("channelCountMode", "SFString", "max", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("channelInterpretation", "SFString", "speakers", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("channelCount", "SFInt32", "2", "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # WaveShaper
        ("curve", "MFFloat", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("oversample", "SFString", "none", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DSoundProcessingNode"),

    ###################################################################################

    # Chapter 17:       Lighting Component

    ###################################################################################

    # https://www.web3d.org/documents/specifications/19775-1/V3.3/Part01/components/lighting.html#DirectionalLight
    ("DirectionalLight", "DirectionalLight", (
        # base class light
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("global", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadows", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadowIntensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ambientIntensity", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # this class
        ("direction", "SFVec3f", ("0", "0", "-1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DLightNode"),

    ("PointLight", "PointLight", (
        # base class light
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("global", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadows", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadowIntensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ambientIntensity", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # this class
        ("attenuation", "SFVec3f", ("1", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("location", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("radius", "SFFloat", "100", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
    ), "X3DLightNode"),

    ("SpotLight", "SpotLight", (
        # base class light
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("global", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadows", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadowIntensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ambientIntensity", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # this class
        ("attenuation", "SFVec3f", ("1", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("location", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("radius", "SFFloat", "100", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # pre v4 specs say beamwidth=PI/4 = 0.78539816339 (we had 1.570796), v4 specs beamwidth= PI*3/16= 0.5890486225480862
        ("beamWidth", "SFFloat", "0.589048622548086", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        # specs say PI/2 = 1.57079632679 (we had 0.785398)
        ("cutOffAngle", "SFFloat", "1.57079632679", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("direction", "SFVec3f", ("0", "0", "-1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DLightNode"),

    ("EnvironmentLight", "EnvironmentLight", (
        # base class light
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("global", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadows", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadowIntensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ambientIntensity", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # this class
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_ANGLE"),
        ("diffuse", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("diffuseCoefficients", "MFFloat", "[]", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("diffuseTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("specularTexture", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DLightNode"),

    ###################################################################################

    #   Chapter18:  Texturing Component

    ###################################################################################

    ("ImageTexture", "ImageTexture", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatS", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatT", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("__unitlengthfactor", "SFDouble", "1", "initializeOnly", "0", "0"),
        ("__specversion", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("autoRefresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("autoRefreshTimeLimit", "SFTime", "3600", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DTextureNode"),

    ("MovieTexture", "MovieTexture", (
        # X3DUrlObject
        ("autoRefresh", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("autoRefreshTimeLimit", "SFTime", "3600", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # description => ["SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # internal sequence number, openal buffer number
        ("__sourceNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),

        # X3DSoundSourceNode
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("gain", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pauseTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("resumeTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("startTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tailTime", "SFTime", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPaused", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_self", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_context", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__context_paused", "SFBool", "FALSE", "initializeOnly", "0", "0"),

        # AudioClip
        ("loop", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pitch", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration_changed", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
        # time that we were initialized at
        ("__inittime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),

        # MovieTexture
        # Texture2D and Movie section
        ("repeatS", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatT", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("speed", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__frac", "SFFloat", "0", "initializeOnly", "0", "0"),
        # which texture number is used
        ("__ctex", "SFInt32", "0", "initializeOnly", "0", "0"),
        # lowest frame
        ("__lowest", "SFInt32", "0", "initializeOnly", "0", "0"),
        # highest frame
        ("__highest", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__fw_movie", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__unitlengthfactor", "SFDouble", "1", "initializeOnly", "0", "0"),
        ("__specversion", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__init_time", "SFTime", "0", "initializeOnly", "0", "0"),
        ("__last_time", "SFTime", "0", "initializeOnly", "0", "0"),

        #       connect => ["MFNode", [], "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        #       _self => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
        #       _context => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
        #       #SoundSource / AudioClip compatible section, keep in same order as AudioClip
        #       description => ["SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       enabled => ["SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        #       loop => ["SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       metadata => ["SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       pauseTime => ["SFTime",0,"inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       pitch => ["SFFloat", 1.0, "inputOutput", "(SPEC_X3D33)","UNCA_NONE"],#ff
        #       resumeTime => ["SFTime",0,"inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       startTime => ["SFTime", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       stopTime => ["SFTime", 0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       url => ["MFString", [""], "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       duration_changed => ["SFTime", -1, "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       elapsedTime => ["SFTime",0,"outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       isActive => ["SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       isPaused => ["SFBool","FALSE","outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       _parentResource =>["FreeWRLPTR",0,"initializeOnly", 0,0],#ff
        #       __oldEnabled => ["SFBool", "TRUE", "inputOutput", 0,0],#ff
        #       __loadstatus =>["SFInt32",0,"initializeOnly", 0,0],#ff
        #       __loadResource => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
        #       # internal sequence number
        #       __sourceNumber => ["SFInt32", -1, "initializeOnly", 0,0],#ff
        #       # time that we were initialized at
        #       __init_time => ["SFTime", 0, "initializeOnly", 0,0],#ff
        #       __last_time => ["SFTime", 0, "initializeOnly", 0,0],#ff
        #       #Texture2D and Movie section
        #       repeatS => ["SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       repeatT => ["SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       textureProperties => ["SFNode", 0, "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #       __textureTableIndex => ["SFInt32", 0, "initializeOnly", 0,0],#ff
        #       speed => ["SFFloat", 1.0, "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        #        __frac => ["SFFloat", 0.0, "initializeOnly", 0,0],#ff
        #        # which texture number is used
        #        __ctex => ["SFInt32", 0, "initializeOnly", 0,0],#ff
        #        # lowest frame
        #        __lowest => ["SFInt32", 0, "initializeOnly", 0,0],#ff
        #        # highest frame
        #        __highest => ["SFInt32", 0, "initializeOnly", 0,0],#ff
        #        __fw_movie  => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
        #       load => ["SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        #       __oldload => ["SFBool", "FALSE", "initializeOnly", 0,0],#ff
        #       __unitlengthfactor => ["SFDouble", 1.0, "initializeOnly", 0,0],#ff
        #       __specversion => ["SFInt32",0,"initializeOnly",0,0],#ff
        #       autoRefreshTimeLimit => ["SFTime", 3600.0, "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        #       autoRefresh => ["SFTime", 0.0, "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
        #       __lasttime => ["SFTime", 0, "initializeOnly", 0,0],#ff
    ), "X3DTextureNode"),

    ("MultiTexture", "MultiTexture", (
        ("alpha", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("function", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mode", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("source", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texture", "MFNode", None, "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__xparams", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DTextureNode"),

    ("MultiTextureCoordinate", "MultiTextureCoordinate", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "MFNode", None, "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTextureCoordinateNode"),

    ("MultiTextureTransform", "MultiTextureTransform", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureTransform", "MFNode", None, "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTextureTransformNode"),

    ("PixelTexture", "PixelTexture", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("image", "SFImage", "0, 0, 0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatS", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatT", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("update", "SFString", "NONE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTextureNode"),

    ("GeneratedTexture", "GeneratedTexture", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # image => ["SFImage", "0, 0, 0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        ("repeatS", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatT", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("update", "SFString", "NONE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("size", "MFInt32", "128", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("viewpoint", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("background", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("children", "MFNode", (), "initializeOnly", "0", "0"),
    ), "X3DTextureNode"),

    ("BufferTexture", "BufferTexture", (
        ("image", "SFImage", "0, 0, 0", "inputOutput", "0", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("repeatS", "SFBool", "TRUE", "initializeOnly", "0", "UNCA_NONE"),
        ("repeatT", "SFBool", "TRUE", "initializeOnly", "0", "UNCA_NONE"),
        ("textureProperties", "SFNode", "0", "initializeOnly", "0", "UNCA_NONE"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__delegate", "SFNode", "NULL", "initializeOnly", "0", "0"),
    ), "X3DTextureNode"),

    ("TextureCoordinate", "TextureCoordinate", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("point", "MFVec2f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTextureCoordinateNode"),

    ("TextureCoordinateGenerator", "TextureCoordinateGenerator", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("mode", "SFString", "SPHERE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("parameter", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTextureCoordinateNode"),

    ("TextureProperties", "TextureProperties", (
        ("anisotropicDegree", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("borderColor", "SFColorRGBA", ("0", "0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("borderWidth", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("boundaryModeS", "SFString", "REPEAT", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("boundaryModeT", "SFString", "REPEAT", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("boundaryModeR", "SFString", "REPEAT", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("magnificationFilter", "SFString", "DEFAULT", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("minificationFilter", "SFString", "DEFAULT", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("textureCompression", "SFString", "DEFAULT", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("texturePriority", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("generateMipMaps", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

    ), "X3DSFNode"),

    ("TextureTransform", "TextureTransform", (
        ("center", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("rotation", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("scale", "SFVec2f", ("1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("translation", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTextureTransformNode"),

    # NOT in specifications, 2022 experiment to duplicate TextureCoordinateGenerator functionality as TextureTransform
    ("TextureTransformGenerator", "TextureTransform", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("mapping", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("mode", "SFString", "REGULAR", "inputOutput", "0", "UNCA_NONE"),
        ("parameter", "MFFloat", (), "inputOutput", "0", "UNCA_NONE"),
    ), "X3DTextureTransformNode"),

    ###################################################################################

    #   Chapter 19:     Interpolation Component

    ###################################################################################

    ("ColorInterpolator", "ColorInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFColor", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFColor", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("CoordinateInterpolator", "CoordinateInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "MFVec3f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_GPU_Routes_out", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_CPU_Routes_out", "SFInt32", "0", "initializeOnly", "0", "0"),

        # GPU running only - run the interpolator on the GPU, use these...
        ("_keyVBO", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_keyValueVBO", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DInterpolatorNode"),

    ("CoordinateInterpolator2D", "CoordinateInterpolator2D", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec2f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "MFVec2f", (("0", "0"),), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("EaseInEaseOut", "EaseInEaseOut", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("easeInEaseOut", "MFVec2f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("modifiedFraction_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("NormalInterpolator", "NormalInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "MFVec3f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("OrientationInterpolator", "OrientationInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFRotation", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("PositionInterpolator", "PositionInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("PositionInterpolator2D", "PositionInterpolator2D", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec2f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("ScalarInterpolator", "ScalarInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFFloat", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("SplinePositionInterpolator", "SplinePositionInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("closed", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("keyVelocity", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalizeVelocity", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_T0", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("_T1", "MFVec3f", (), "initializeOnly", "0", "0"),
    ), "X3DInterpolatorNode"),

    ("SplinePositionInterpolator2D", "SplinePositionInterpolator2D", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("closed", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec2f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("keyVelocity", "MFVec2f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalizeVelocity", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_T0", "MFVec2f", (), "initializeOnly", "0", "0"),
        ("_T1", "MFVec2f", (), "initializeOnly", "0", "0"),
    ), "X3DInterpolatorNode"),

    ("SplineScalarInterpolator", "SplineScalarInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("closed", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyVelocity", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalizeVelocity", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFFloat", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_T0", "MFFloat", (), "initializeOnly", "0", "0"),
        ("_T1", "MFFloat", (), "initializeOnly", "0", "0"),
    ), "X3DInterpolatorNode"),

    ("SquadOrientationInterpolator", "SquadOrientationInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFRotation", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalizeVelocity", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("closed", "SFBool", "FALSE", "inputOutput", "0", "0"),  # H: the specs made a mistake it should be 'closed' not 'normalizeVelocity' -dug9
        ("value_changed", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_normkey", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_normkeyValue", "MFRotation", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    # VectorInterpolator, CoordinateMorpher, NormalMorpher - proposed by Instant Player, see Morpher paper in 26_Hanim
    ("VectorInterpolator", "VectorInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "MFFloat", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("CoordinateMorpher", "CoordinateMorpher", (
        ("set_weights", "MFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "MFVec3f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ("NormalMorpher", "NormalMorpher", (
        ("set_weights", "MFFloat", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "MFVec3f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DInterpolatorNode"),

    ###################################################################################

    #       Cubemap Texturing Component

    ###################################################################################

    ("ComposedCubeMapTexture", "ComposedCubeMapTexture", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("back", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bottom", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("front", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("left", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("top", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("right", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DEnvironmentTextureNode"),

    ("GeneratedCubeMapTexture", "GeneratedCubeMapTexture", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        # _parentResource =>["FreeWRLPTR",0,"initializeOnly", 0,0],#ff
        # __subTextures => ["MFNode",[],"initializeOnly",0,0],#ff
        # __regenSubTextures => ["SFBool","FALSE","initializeOnly",0,0],#ff
        ("update", "SFString", "NONE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("size", "SFInt32", "128", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
    ), "X3DEnvironmentTextureNode"),

    # same order of fields up to __regenSubtextures as GeneratedCubeMapTexture
    ("ImageCubeMapTexture", "ImageCubeMapTexture", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__subTextures", "MFNode", (), "initializeOnly", "0", "0"),
        ("__regenSubTextures", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("autoRefresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("autoRefreshTimeLimit", "SFTime", "3600", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DEnvironmentTextureNode"),

    ###################################################################################

    #   20  Pointing Device Component

    ###################################################################################

    ("TouchSensor", "TouchSensor", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hitNormal_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hitPoint_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hitTexCoord_changed", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_oldhitNormal", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),  # send event only if changed
        ("_oldhitPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),  # send event only if changed
        ("_oldhitTexCoord", "SFVec2f", ("0", "0"), "outputOnly", "0", "0"),  # send event only if changed
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isOver", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("touchTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DPointingDeviceSensorNode"),

    ("PlaneSensor", "PlaneSensor", (
        ("autoOffset", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("axisRotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxPosition", "SFVec2f", ("-1", "-1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("minPosition", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("offset", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isOver", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("trackPoint_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("translation_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sensorLocalOutput", "SFBool", "FALSE", "initializeOnly", "0", "UNCA_NONE"),
        ("_oldtrackPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("_oldtranslation", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        # where we are at a press...
        ("_orig_point", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DDragSensorNode"),

    # proposed for v4 - 2 finters on a drag sensor - you should get a rotation out
    ("MultiTouchSensor", "MultiTouchSensor", (
        ("autoOffset", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("axisRotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxPosition", "SFVec2f", ("-1", "-1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("minPosition", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("offset", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isOver", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        # trackPoint_changed => ["SFVec3f", [0, 0, 0], "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        ("translation_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sensorLocalOutput", "SFBool", "FALSE", "initializeOnly", "0", "UNCA_NONE"),
        ("_oldtrackPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("_oldtranslation", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        # where we are at a press...
        ("_origPoint", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),

        ("translationOffset", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("rotationOffset", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("scaleOffset", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("minScale", "SFVec3f", ("0.1", "0.1", "0.1"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("maxScale", "SFVec3f", ("10", "10", "10"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # translation_changed SFVec3f [out]
        ("rotation_changed", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("scale_changed", "SFVec3f", ("1", "1", "1"), "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        # hitNormalizedCoord_changed => ["MFVec3f", [], "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"],#ff
        ("trackPoints_changed", "MFVec3f", (), "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("touches_changed", "MFInt32", (), "outputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_lastframe", "SFInt32", "0", "outputOnly", "0", "0"),
        ("_drag_count", "SFInt32", "0", "outputOnly", "0", "0"),
        ("_orig_count", "SFInt32", "0", "outputOnly", "0", "0"),
        ("_orig_points", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_drag_points", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_oldrotation", "SFRotation", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("_oldscale", "SFVec3f", ("1", "1", "1"), "initializeOnly", "0", "0"),
        ("_lastTao", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DDragSensorNode"),

    #
    # Experimental node: LineSensor
    #
    ("LineSensor", "LineSensor", (
        ("autoOffset", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("direction", "SFVec3f", ("1", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxPosition", "SFFloat", "-1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("minPosition", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("offset", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isOver", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("trackPoint_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("translation_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_oldtrackPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("_oldtranslation", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        # where we are at a press...
        ("_origPoint", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DDragSensorNode"),

    #
    # Experimental node: PointSensor
    #

    ("PointSensor", "PointSensor", (
        ("autoOffset", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxPosition", "SFVec3f", ("-1", "-1", "-1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("minPosition", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("offset", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isOver", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("trackPoint_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("translation_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_oldtrackPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("_oldtranslation", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        # where we are at a press...
        ("_origPoint", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DDragSensorNode"),

    ("SphereSensor", "SphereSensor", (
        ("autoOffset", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("offset", "SFRotation", ("0", "1", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rotation_changed", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("trackPoint_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_oldtrackPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("_oldrotation", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "0", "0"),
        ("isOver", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        # where we are at a press...
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_origPoint", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_origNormalizedPoint", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_radius", "SFFloat", "0", "initializeOnly", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DDragSensorNode"),

    ("CylinderSensor", "CylinderSensor", (
        ("autoOffset", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("axisRotation", "SFRotation", ("0", "1", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("diskAngle", "SFFloat", "0.262", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxAngle", "SFFloat", "-1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("minAngle", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("offset", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isOver", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("rotation_changed", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("trackPoint_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sensorLocalOutput", "SFBool", "FALSE", "initializeOnly", "0", "UNCA_NONE"),
        ("_oldtrackPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("_oldrotation", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "0", "0"),
        # where we are at a press...
        ("_origPoint", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_radius", "SFFloat", "0", "initializeOnly", "0", "0"),
        ("_usingDisk", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DDragSensorNode"),

    ###################################################################################

    #   21  Key Device Component

    ###################################################################################

    # KeySensor
    ("KeySensor", "KeySensor", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),  # see note top of file
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("actionKeyPress", "SFInt32", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("actionKeyRelease", "SFInt32", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("altKey", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlKey", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyPress", "SFString", "", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyRelease", "SFString", "", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shiftKey", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DKeyDeviceSensorNode"),

    # StringSensor
    ("StringSensor", "StringSensor", (
        ("deletionAllowed", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),  # see note top of file
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enteredText", "SFString", "", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("finalText", "SFString", "", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("singleton", "SFBool", "TRUE", "inputOutput", "0", "UNCA_NONE"),  # //if true, then shut off all other stringsensors when this enabled
        ("_initialized", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DKeyDeviceSensorNode"),

    ###################################################################################

    #   22  Environmental Sensor Component

    ###################################################################################

    ("ProximitySensor", "ProximitySensor", (
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("size", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),  # see note top of file
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("position_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation_changed", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enterTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("exitTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("centerOfRotation_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # These fields are used for the info.
        ("__hit", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__t1", "SFVec3f", ("10000000", "0", "0"), "inputOutput", "0", "0"),
        ("__t2", "SFRotation", ("0", "1", "0", "0"), "inputOutput", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DEnvironmentalSensorNode"),

    ("TransformSensor", "TransformSensor", (
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("size", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),  # see note top of file
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("position_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation_changed", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enterTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("exitTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("targetObject", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # These fields are used for the info.
        ("__hit", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__t1", "SFVec3f", ("10000000", "0", "0"), "inputOutput", "0", "0"),
        ("__t2", "SFRotation", ("0", "1", "0", "0"), "inputOutput", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DEnvironmentalSensorNode"),

    ("VisibilitySensor", "VisibilitySensor", (
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),  # see note top of file
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("size", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("enterTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("exitTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__visible", "SFInt32", "0", "initializeOnly", "0", "0"),  # for Occlusion tests.
        ("__occludeCheckCount", "SFInt32", "-1", "initializeOnly", "0", "0"),  # for Occlusion tests.
        ("__points", "MFVec3f", (), "initializeOnly", "0", "0"),  # for Occlude Box.
        ("__Samples", "SFInt32", "0", "initializeOnly", "0", "0"),  # Occlude samples from last pass
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DEnvironmentalSensorNode"),

    ###################################################################################

    #   23  Navigation Component

    ###################################################################################

    ("LOD", "LOD", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("level", "MFNode", (), "inputOutput", "(SPEC_VRML)", "UNCA_NONE"),  # for VRML spec
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # for X3D spec
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("range", "MFFloat", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("level_changed", "SFInt32", "0", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("forceTransitions", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # __isX3D => ["SFBool", "(inputFileVersion[0]==3)" , "initializeOnly", 0,0],#ff # "TRUE" for X3D V3.x files
        ("_lastMethod", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_selected", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGroupingNode"),

    # "TileContent"  => new VRML::NodeType("TileContent", [
    # boundingVolume => ["MFDouble",[],"inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
    # boundingVolumeType => ["SFString","BBOX","initializeOnly", "(SPEC_X3D40)","UNCA_NONE"],#ff
    # content => ["SFNode", "NULL", "inputOutput", "(SPEC_X3D40)","UNCA_NONE"],#ff
    # ],"X3DChildNode"),

    ("Tile", "Tile", (
        # grouping interface
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # tile interface
        ("content", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("geometricError", "SFFloat", "0", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("refine", "SFString", "REPLACE", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("showContent", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("boundingVolume", "MFFloat", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("boundingVolumeType", "SFString", "BBOX", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("contentVolume", "MFFloat", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("contentVolumeType", "SFString", "BBOX", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DGroupingNode"),

    ("Billboard", "Billboard", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("axisOfRotation", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_rotationAngle", "SFDouble", "0", "initializeOnly", "0", "0"),
        # JAS _sortedChildren => ["MFNode", [], "inputOutput", 0,0],#ff
    ), "X3DGroupingNode"),

    ("Collision", "Collision", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),  # see note top of file
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("collide", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("proxy", "SFNode", "NULL", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("collideTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # JAS _sortedChildren => ["MFNode", [], "inputOutput", 0,0],#ff
        # return info for collisions
        # bit 0 : collision or not
        # bit 1: changed from previous of not
        ("__hit", "SFInt32", "0", "inputOutput", "0", "0"),
    ), "X3DEnvironmentalSensorNode"),

    ("Viewpoint", "Viewpoint", (
        # generic Viewpoint fields
        ("_layerId", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_donethispass", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_reachablethispass", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "-1", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("jump", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fieldOfView", "SFFloat", "0.785398", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("position", "SFVec3f", ("0", "0", "10"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("centerOfRotation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("retainUserOffsets", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # augmented reality extensions:
        ("fovMode", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("aspectRatio", "SFFloat", "0.785398", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # user offsets:
        ("_initializedOnce", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("_orientation", "SFRotation", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("_position", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_pin_point", "SFVec3d", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_show_pin_point", "SFBool", "FALSE", "inputOnly", "0", "0"),

        ("farClippingPlane", "SFFloat", "-1", "inputOutput", "(SPEC_X3D30)", "UNCA_NONE"),
        ("nearClippingPlane", "SFFloat", "-1", "inputOutput", "(SPEC_X3D30)", "UNCA_NONE"),
        ("vIewAll", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("navigationInfo", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DBindableNode"),

    ("OrthoViewpoint", "OrthoViewpoint", (
        # generic Viewpoint fields
        ("_layerId", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_donethispass", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_reachablethispass", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "-1", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("jump", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fieldOfView", "MFFloat", ("-1", "-1", "1", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("position", "SFVec3f", ("0", "0", "10"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("centerOfRotation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("retainUserOffsets", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # user offsets:
        ("_initializedOnce", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("_orientation", "SFRotation", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("_position", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_pin_point", "SFVec3d", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_show_pin_point", "SFBool", "FALSE", "inputOnly", "0", "0"),

        ("farClippingPlane", "SFFloat", "-1", "inputOutput", "(SPEC_X3D30)", "UNCA_NONE"),
        ("nearClippingPlane", "SFFloat", "-1", "inputOutput", "(SPEC_X3D30)", "UNCA_NONE"),
        ("vIewAll", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("navigationInfo", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DBindableNode"),

    ("NavigationInfo", "NavigationInfo", (
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("avatarSize", "MFFloat", ("0.25", "1.6", "0.75"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("headlight", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("speed", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("type", "MFString", ("EXAMINE", "ANY"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("visibilityLimit", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_layerId", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("transitionType", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "-1", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transitionTime", "SFTime", "1", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transitionComplete", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DBindableNode"),

    ("ViewpointGroup", "ViewpointGroup", (
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("displayed", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("retainUserOffsets", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("size", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("__proxNode", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
    ), "X3DGroupingNode"),

    ###################################################################################

    #   24  Environmental Effects Component

    ###################################################################################

    ("Background", "Background", (
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("groundAngle", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("groundColor", "MFColor", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skyAngle", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("skyColor", "MFColor", (("0", "0", "0"),), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_layerId", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__points", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__colours", "MFColor", (), "initializeOnly", "0", "0"),
        ("__quadcount", "SFInt32", "0", "initializeOnly", "0", "0"),
        # __combined => ["SFNode","NULL","initializeOnly",0,0],#ff
        ("transparency", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("frontUrl", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("backUrl", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("topUrl", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bottomUrl", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("leftUrl", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rightUrl", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__textureright", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__frontTexture", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__backTexture", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__topTexture", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__bottomTexture", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__leftTexture", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__rightTexture", "SFNode", "NULL", "inputOutput", "0", "0"),

        ("__VBO", "SFInt32", "0", "initializeOnly", "0", "0"),  # Vertex Buffer Object, if required.
    ), "X3DBackgroundNode"),

    ("Fog", "Fog", (
        # Fog interface - keep same order, offsets as LocalFog
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogType", "SFString", "LINEAR", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("visibilityRange", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("__fogScale", "SFFloat", "1", "inputOutput", "0", "0"),
        ("__fogType", "SFInt32", "1", "initializeOnly", "0", "0"),
        # Bindable interface
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "-1", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_layerId", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DBindableNode"),

    ("FogCoordinate", "FogCoordinate", (
        ("depth", "MFFloat", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DGeometricPropertyNode"),

    ("LocalFog", "Fog", (
        # Fog interface - keep same order, offsets as Fog
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogType", "SFString", "LINEAR", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("visibilityRange", "SFFloat", "0", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("__fogScale", "SFFloat", "1", "inputOutput", "0", "0"),
        ("__fogType", "SFInt32", "1", "initializeOnly", "0", "0"),
        # other
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("TextureBackground", "TextureBackground", (
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("groundAngle", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("groundColor", "MFColor", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skyAngle", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("skyColor", "MFColor", (("0", "0", "0"),), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_layerId", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__points", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__colours", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__quadcount", "SFInt32", "0", "initializeOnly", "0", "0"),
        # __combined => ["SFNode","NULL","initializeOnly",0,0],#ff
        ("__VBO", "SFInt32", "0", "initializeOnly", "0", "0"),  # Vertex Buffer Object, if required.

        ("frontTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("backTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("topTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bottomTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("leftTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rightTexture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transparency", "MFFloat", ("0",), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DBackgroundNode"),

    # see augmented reality for 2 more background nodes

    ###################################################################################

    #   25  Geospatial Component

    ###################################################################################

    ("GeoCoordinate", "GeoCoordinate", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("point", "MFVec3d", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_GEO"),  # v3.2 GD degrees, v3.3 GD angle units # see note top of file
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__movedCoords", "MFVec3f", (), "inputOutput", "0", "0"),
    ), "X3DCoordinateNode"),

    ("GeoElevationGrid", "GeoElevationGrid", (
        ("set_height", "MFDouble", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("yScale", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("creaseAngle", "SFDouble", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("geoGridOrigin", "SFVec3d", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_GEO"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("height", "MFDouble", ("0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("xDimension", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("xSpacing", "SFDouble", "1", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_GEO"),
        ("zDimension", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("zSpacing", "SFDouble", "1", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_GEO"),
        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),

        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__autoOffset", "SFVec3d", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("__localOrient", "SFVec4d", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("__planets", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DGeometryNode"),

    ("GeoLOD", "GeoLOD", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # the following screws up routing in the old VRML parser, because children can
        # be an "EXPOSED_FIELD" AND an "EVENT_OUT", so by changing this to an ""inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)"
        # we can have only one field, the EXPOSED_FIELD_children
        # children => ["MFNode",[],"outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff

        ("children", "MFNode", (), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("level_changed", "SFInt32", "0", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("center", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_GEO"),  # see note top of file
        ("child1Url", "MFString", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("child2Url", "MFString", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("child3Url", "MFString", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("child4Url", "MFString", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("range", "SFFloat", "10", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("rootUrl", "MFString", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rootNode", "MFNode", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__movedCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__inRange", "SFBool", "FALSE", "inputOutput", "0", "0"),
        ("__child1Node", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__child2Node", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__child3Node", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__child4Node", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__rootUrl", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__childloadstatus", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__rooturlloadstatus", "SFInt32", "0", "inputOutput", "0", "0"),

        # ProximitySensor copies.
        # __t1 => ["SFVec3d", [10000000, 0, 0], "inputOutput", 0,0],#ff
        ("__level", "SFInt32", "-1", "inputOutput", "0", "0"),  # only for debugging purposes
    ), "X3DGroupingNode"),

    ("GeoMetadata", "GeoMetadata", (
        ("data", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("summary", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("refresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),  # see note top of file
    ), "X3DChildNode"),

    ("GeoPositionInterpolator", "GeoPositionInterpolator", (
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFVec3d", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_GEO"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geovalue_changed", "SFVec3d", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__movedValue", "MFVec3f", (), "inputOutput", "0", "0"),
        ("__oldKeyPtr", "MFFloat", "NULL", "outputOnly", "0", "0"),
        ("__oldKeyValuePtr", "MFVec3d", "NULL", "outputOnly", "0", "0"),
    ), "X3DInterpolatorNode"),

    ("GeoProximitySensor", "ProximitySensor", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),  # see note top of file
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoCenter", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32)", "UNCA_GEO"),
        ("center", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_GEO"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("size", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_LENGTH"),
        ("centerOfRotation_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("enterTime", "SFTime", "-1", "outputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("exitTime", "SFTime", "-1", "outputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoCoord_changed", "SFVec3d", ("0", "0", "0"), "outputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("orientation_changed", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("position_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32)", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),

        # These fields are used for the info.
        ("__hit", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__t1", "SFVec3f", ("10000000", "0", "0"), "inputOutput", "0", "0"),
        ("__t2", "SFRotation", ("0", "1", "0", "0"), "inputOutput", "0", "0"),
        ("__t3", "SFVec3d", ("10000000", "0", "0"), "inputOutput", "0", "0"),

        # "compiled" versions of strings above
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__movedCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__localOrient", "SFVec4d", ("0", "0", "1", "0"), "inputOutput", "0", "0"),
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
        ("__oldGeoCenter", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__oldSize", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
    ), "X3DEnvironmentalSensorNode"),

    ("GeoTouchSensor", "GeoTouchSensor", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hitNormal_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hitPoint_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hitTexCoord_changed", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hitGeoCoord_changed", "SFVec3d", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isOver", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("touchTime", "SFTime", "-1", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("_oldhitNormal", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),  # send event only if changed
        ("_oldhitPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),  # send event only if changed
        ("_oldhitTexCoord", "SFVec2f", ("0", "0"), "outputOnly", "0", "0"),  # send event only if changed
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DPointingDeviceSensorNode"),

    ("GeoTransform", "GeoTransform", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "0", "0"),
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "UNCA_LENGTH"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoCenter", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_GEO"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_ANGLE"),
        ("scale", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("scaleOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_ANGLE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_LENGTH"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32)", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),

        # fields for reducing redundant calls
        ("__do_center", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_trans", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_rotation", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_scaleO", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_scale", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_anything", "SFInt32", "FALSE", "initializeOnly", "0", "0"),

        # "compiled" versions of strings above
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__movedCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__localOrient", "SFVec4d", ("0", "0", "1", "0"), "inputOutput", "0", "0"),
        ("__oldGeoCenter", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__oldChildren", "MFNode", (), "inputOutput", "0", "0"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
    ), "X3DGroupingNode"),

    ("GeoViewpoint", "GeoViewpoint", (
        # generic Viewpoint fields - except watch it, the position is double (vs viewpoint and orthoviewpoint - single)
        ("_layerId", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_donethispass", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_reachablethispass", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "-1", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("jump", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fieldOfView", "SFFloat", "0.785398", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),  # see note top of file, AND spec changed to in/out in 3.3
        ("position", "SFVec3d", ("0", "0", "100000"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_GEO"),  # ditto
        ("centerOfRotation", "SFVec3d", ("0", "0", "0"), "inputOutput", "( SPEC_X3D33)", "UNCA_NONE"),
        # the following sets were in v3.2 but v3.3 changed position,orientation to [inout] and (I think) that's backward compat in freewrl
        # set_orientation => ["SFRotation", ["IO_FLOAT", "IO_FLOAT", "IO_FLOAT", "IO_FLOAT"], "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )","UNCA_NONE"],#ff
        # set_position => ["SFVec3d", ["IO_FLOAT", "IO_FLOAT", "IO_FLOAT"], "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )","UNCA_NONE"],#ff
        # GeoViewpoint fields
        ("headlight", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("navType", "MFString", ("EXAMINE", "ANY"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("speedFactor", "SFFloat", "1", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("retainUserOffsets", "SFBool", "FALSE", "inputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        # user offsets:
        ("_initializedOnce", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("_orientation", "SFRotation", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("_position", "SFVec3d", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_pin_point", "SFVec3d", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_show_pin_point", "SFBool", "FALSE", "inputOnly", "0", "0"),

        ("relativeHeight", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("_resetRelativeHeight", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("walkSurface", "MFString", ("HIGHEST",), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_walkSurfacePriority", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("prioritySurfaces", "MFNode", (), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("translucencySurfaces", "MFNode", (), "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        ("translucencyRange", "SFVec2d", ("0", "0"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("translucency", "SFFloat", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("navigationType", "MFString", ("WALK", "ANY"), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("nearClippingPlane", "SFFloat", "-1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("farClippingPlane", "SFFloat", "-1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        ("_prepped_planet", "SFInt32", "0", "initializeOnly", "0", "0"),
        # "compiled" versions of strings above
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__movedPosition", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__movedOrientation", "SFRotation", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("__movedOrientationB", "SFRotation", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("__movedgd", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),

        ("__oldSFString", "SFString", "", "inputOutput", "0", "0"),  # the description field
        ("__oldFieldOfView", "SFFloat", "0.785398", "inputOutput", "0", "0"),
        ("__oldHeadlight", "SFBool", "TRUE", "inputOutput", "0", "0"),
        ("__oldJump", "SFBool", "TRUE", "inputOutput", "0", "0"),
        ("__oldMFString", "MFString", (), "inputOutput", "0", "0"),  # the navType

    ), "X3DBindableNode"),

    # deprecated in v3.3
    ("GeoOrigin", "GeoOrigin", (
        ("geoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_GEO"),  # v3.2 GD degrees, v3.3 GD angle units
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("rotateYUp", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),

        # these are now static in CFuncs/GeoVRML.c
        # "compiled" versions of strings above
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__movedCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__movedgd", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__oldgeoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__oldMFString", "MFString", (), "inputOutput", "0", "0"),  # the navType
        ("__rotyup", "SFVec4d", ("0", "1", "0", "0"), "inputOutput", "0", "0"),

    ), "X3DChildNode"),

    ("GeoLocation", "GeoLocation", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_GEO"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("relativeHeight", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("_gridHeight", "SFDouble", "0.0", "inputOnly", "0", "0"),

        # "compiled" versions of strings above
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__position", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__movedCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__movedgd", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__localOrient", "SFVec4d", ("0", "0", "1", "0"), "inputOutput", "0", "0"),
        ("__offsetOrient", "SFVec4d", ("0", "0", "1", "0"), "inputOutput", "0", "0"),
        ("__oldgeoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__oldChildren", "MFNode", (), "inputOutput", "0", "0"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
    ), "X3DGroupingNode"),

    # non-spec nodes geoPlanet and geoConvert by dug9
    ("GeoPlanet", "GeoPlanet", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("planetId", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        # "compiled" versions of strings above
        ("__oldChildren", "MFNode", (), "inputOutput", "0", "0"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
    ), "X3DGroupingNode"),

    ("GeoConvert", "GeoConvert", (
        ("set_geoCoords", "SFVec3d", ("0", "0", "0"), "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_GEO"),  # v3.2 GD degrees, v3.3 GD angle units
        ("set_gcCoords", "SFVec3d", ("0", "0", "0"), "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_GEO"),  # v3.2 GD degrees, v3.3 GD angle units
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_NONE"),
        ("gcCoords_changed", "SFVec3d", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_GEO"),  # v3.2 GD degrees, v3.3 GD angle units
        ("geoCoords_changed", "SFVec3d", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 )", "UNCA_GEO"),  # v3.2 GD degrees, v3.3 GD angle units
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("__oldgeoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__oldgcCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "0", "0"),
    ), "X3DInterpolatorNode"),

    # proposed v4 SRF nodes
    # generally are just to help you type - in theory all the parameters can go in geoSystem MFString, the nodes don't 'do' anything

    # the SANDEN node
    ("GeoSRF", "GeoSRF", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoKeyValue", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geoJson", "SFString", "", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
    ), "X3DChildNode"),  # would/should be a X3DGeoSystemNode - later

    # the BRUTZMAN nodes
    ("GeoEllipsoid", "GeoEllipsoid", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("code", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("name", "SFString", "", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("A", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("F", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("B", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("C", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("axisCount", "SFInt32", "2", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("GeoSystemParameters", "GeoSystemParameters", (
        ("paramterName", "MFString", (), "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("paramterValue", "MFDouble", (), "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFParametersInfoNode"),

    ("GeoSpatialReferenceFrame", "GeoSpatialReferenceFrame", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("dssCode", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("name", "SFString", "", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("rtCode", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("ellipsoid", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("systemParameters", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DChildNode"),

    # the PUK nodes
    # 1 top node / level - takes a 2nd level as parameter

    ("GeoReferenceSurfaceInfo", "GeoReferenceSurfaceInfo", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("dssCode", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("name", "SFString", "", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("srfParametersInfo", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DChildNode"),

    # 2nd level - takes 3rd level as parameter
    ("GeoSRFParametersInfo", "GeoSRFParametersInfo", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("rtCode", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("srfParameters", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),  # draft says srfParametersInfo but thats circular
    ), "X3DGeoSRFParametersInfoNode"),

    # 3rd level #1
    ("GeoSRFSet", "GeoSRFSet", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("ormCode", "SFInt32", "250", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("srfsCode", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("srfsMember", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFParametersNode"),

    # 3rd level #2
    ("GeoSRFInstance", "GeoSRFInstance", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("srfCode", "SFInt32", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFParametersNode"),

    # 3rd level #3 - takes 4th level as parameter
    ("GeoSRFTemplate", "GeoSRFTemplate", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("ormCode", "SFInt32", "250", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("srftode", "SFInt32", "1", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("srftParameters", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFParametersNode"),

    # 4th level #1 EC
    ("GeoECParameters", "GeoECParameters", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("centralScale", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("falseEasting", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("falseNorthing", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("originLongitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("srftode", "SFString", "NORTH", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #2 LCC
    ("GeoLCCParameters", "GeoLCCParameters", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("falseEasting", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("falseNorthing", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("latitude1", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("latitude2", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("originLongitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("originLatitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #3 M
    ("GeoMParameters", "GeoMParameters", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("centralScale", "SFDouble", "1", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),  # spec draft had 0 as default
        ("falseEasting", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("falseNorthing", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("originLongitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #4 OM ObliqueMercator
    ("GeoOMParameters", "GeoOMParameters", (  # spec draft had ObliqueMercator, we use OM
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("centralScale", "SFDouble", "1", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),  # spec draft had 0 as default
        ("falseEasting", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("falseNorthing", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("longitude1", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("latitude1", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("longitude2", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("latitude2", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #5 PS polar stereographc
    ("GeoPSParameters", "GeoPSParameters", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("centralScale", "SFDouble", "1", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),  # spec draft had 0 as default
        ("falseEasting", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("falseNorthing", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("originLongitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("polarAspect", "SFString", "NORTH", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #6 TM Transverse Mercator
    ("GeoTMParameters", "GeoTMParameters", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("centralScale", "SFDouble", "1", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),  # spec draft had 0 as default
        ("falseEasting", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("falseNorthing", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("originLongitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("originLatitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #7 LocoCentric Euclidean - do we need?
    ("GeoLCE3DParameters", "GeoLCE3DParameters", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("lococentre", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("primaryAxis", "SFVec3f", ("0", "1", "0"), "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("secondaryAxis", "SFVec3f", ("0", "0", "1"), "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #8 LSR3d local space rectangular - do we need?
    ("GeoLSR3DParameters", "GeoLSR3D3DParameters", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("forwardDirection", "SFInt32", "2", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("upDirection", "SFInt32", "1", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #9 Local Tangent Space Euclidean
    ("GeoTMParameters", "GeoTMParameters", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("azimuth", "SFDouble", "1", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("geodeticLatitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),  # ?? is there a non-geodetic lat,lon?
        ("geodeticLongitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("heightOffset", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("x_false_origin", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("y_false_origin", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # 4th level #10 Local Tangent Paramters - used for both LTSAS local tangent space azimuthal spherical, and LTSC local tangent space cylindrical
    ("GeoLTParameters", "GeoLTParameters", (  # draft spec calls LocalTangent we call LT
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("azimuth", "SFDouble", "1", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("geodeticLatitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),  # ?? is there a non-geodetic lat,lon?
        ("geodeticLongitude", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("heightOffset", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("x_false_origin", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
        ("y_false_origin", "SFDouble", "0", "initializeOnly", "(SPEC_X3D40 )", "UNCA_NONE"),
    ), "X3DGeoSRFTParametersNode"),

    # geo tiles
    ("GeoTile", "GeoTile", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DGroupingNode"),

    ("GeoTileSet", "GeoTileSet", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("geoOrigin", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32)", "UNCA_NONE"),
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoSRF", "SFNode", "NULL", "initializeOnly", "0", "0"),

    ), "X3DChildNode"),

    ###################################################################################

    #   26  H-Anim Component

    ###################################################################################

    ("HAnimDisplacer", "HAnimDisplacer", (
        ("coordIndex", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("displacements", "MFVec3f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_dindex", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DGeometricPropertyNode"),

    ("HAnimHumanoid", "HAnimHumanoid", (
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("info", "MFString", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # see note top of file
        ("joints", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skeletalConfiguration", "SFString", "BASIC", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("scale", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("scaleOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("segments", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sites", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skeleton", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skin", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skinCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skinNormal", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("version", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("viewpoints", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("motions", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("motionsEnabled", "MFBool", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_lastMotionsEnabled", "MFBool", (), "inputOutput", "0", "0"),
        ("transitionTime", "SFTime", "0.01", "inputOutput", "0", "0"),
        ("loa", "SFInt32", "-1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        # _JT => ["FreeWRLPTR",0,"initializeOnly", 0,0],#ff moved to _intern HanimRep
        # _PVI => ["FreeWRLPTR",0,"initializeOnly", 0,0],#ff
        # _PVW => ["FreeWRLPTR",0,"initializeOnly", 0,0],#ff
        # _NV => ["SFInt32", 0, "initializeOnly", 0,0],#ff
        ("_origCoords", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_origNorms", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("jointBindingPositions", "MFVec3f", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("jointBindingRotations", "MFRotation", (), "inputOutput", "(SPEC_X3D40)", "UNCA_ANGLE"),
        ("jointBindingScales", "MFVec3f", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("skinBindingCoords", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("skinBindingNormals", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("HAnimPermuter", "HAnimPermuter", (
        # ParticleSystem > HANIM uses this node to randomize humanoids
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("description", "SFString", "", "inputOutput", "0", "0"),
        ("humanoids", "MFNode", (), "inputOutput", "0", "0"),
        ("motions", "MFNode", (), "inputOutput", "0", "0"),
        ("compute", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("permutations", "MFInt32", (), "inputOutput", "0", "0"),
        ("index", "SFInt32", "0", "inputOutput", "0", "0"),
        ("humanoid", "SFNode", "NULL", "outputOnly", "0", "0"),
        ("_play", "MFNode", (), "initializeOnly", "0", "0"),
    ), "X3DChildNode"),

    ("HAnimMotionInterpolator", "HAnimMotionInterpolator", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # MotionPlay
        ("transitionWeight", "SFFloat", "0", "initializeOnly", "0", "0"),
        ("transitionStart", "SFTime", "0", "initializeOnly", "0", "0"),
        ("channelsEnabled", "MFBool", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_lastenabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_framevalues", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # Extra
        ("joints", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_jointnames", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DMotionNode"),

    ("HAnimMotion", "HAnimMotion", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # MotionPlay
        ("transitionWeight", "SFFloat", "0", "initializeOnly", "0", "0"),
        ("transitionStart", "SFTime", "0", "initializeOnly", "0", "0"),
        ("channelsEnabled", "MFBool", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("cycleTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_startTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_lastenabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_isActive", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameIncrement", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameIndex", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("startFrame", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("endFrame", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("loop", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("next", "SFBool", "FALSE", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("previous", "SFBool", "FALSE", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_framevalues", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # MotionData
        ("loa", "SFInt32", "-1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameCount", "SFInt32", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameDuration", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_channelcount", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_njoints", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_channels", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_fvalues", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # extra
        ("channels", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("joints", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("values", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DMotionNode"),

    ("HAnimMotionPlay", "HAnimMotionPlay", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # MotionPlay
        ("transitionWeight", "SFFloat", "0", "initializeOnly", "0", "0"),
        ("transitionStart", "SFTime", "0", "initializeOnly", "0", "0"),
        ("channelsEnabled", "MFBool", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("cycleTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("elapsedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_startTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_lastenabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_isActive", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameIncrement", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameIndex", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("startFrame", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("endFrame", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("loop", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("next", "SFBool", "FALSE", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("previous", "SFBool", "FALSE", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_framevalues", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # extra
        ("data", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("mapping", "MFString", (), "initializeOnly", "0", "0"),
    ), "X3DMotionNode"),

    ("HAnimMotionData", "HAnimMotionData", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # MotionData
        ("loa", "SFInt32", "-1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameCount", "SFInt32", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameDuration", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_channelcount", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_njoints", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_channels", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_fvalues", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # extra
        ("__loadstatus", "SFInt32", "1", "initializeOnly", "0", "0"),
        ("channels", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("joints", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("values", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DMotionDataNode"),

    ("HAnimMotionDataFile", "HAnimMotionDataFile", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # MotionData
        ("loa", "SFInt32", "-1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameCount", "SFInt32", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameDuration", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_channelcount", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_njoints", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_channels", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_fvalues", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # extra
        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("ignorePosition", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("ignoreFirstFrame", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("flipZ", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("mapping", "MFString", (), "initializeOnly", "0", "0"),
        ("scale", "SFFloat", "1", "initializeOnly", "0", "0"),
        ("teePose", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("yUp", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("legAngle", "SFFloat", "21", "initializeOnly", "0", "0"),
        ("armAngle", "SFFloat", "90", "initializeOnly", "0", "0"),
    ), "X3DMotionDataNode"),

    ("HAnimMotionClip", "HAnimMotionClip", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        # MotionData
        ("loa", "SFInt32", "-1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameCount", "SFInt32", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("frameDuration", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("_channelcount", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_njoints", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_channels", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_fvalues", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # extra - DataFile
        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # extra - Data / inline
        ("channels", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("joints", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
        ("values", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33  | SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DMotionDataNode"),

    ("HAnimJoint", "HAnimJoint", (

        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("scale", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("scaleOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("displacers", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("limitOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("llimit", "MFFloat", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skinCoordIndex", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("skinCoordWeight", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stiffness", "MFFloat", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ulimit", "MFFloat", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # fields for reducing redundant calls
        ("__do_center", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_trans", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_rotation", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_scaleO", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_scale", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_anything", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DChildNode"),

    ("HAnimSegment", "HAnimSegment", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("centerOfMass", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("displacers", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mass", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_MASS"),
        ("momentsOfInertia", "MFFloat", ("0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_MOMENT"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_origCoords", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DChildNode"),

    ("HAnimSite", "HAnimSite", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("scale", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("scaleOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # fields for reducing redundant calls
        ("__do_center", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_trans", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_rotation", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_scaleO", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_scale", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__do_anything", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DGroupingNode"),

    ###################################################################################

    #   27  NURBS Component

    ###################################################################################

    ("Contour2D", "Contour2D", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSFNode"),

    ("ContourPolyline2D", "ContourPolyline2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "MFVec2d", (), "inputOutput", "( SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),  # v3.1 changed to this...
        ("point", "MFVec2f", (), "inputOutput", "(SPEC_X3D30 )", "UNCA_NONE"),  # ...from this, because point not in specs
    ), "X3DNurbsControlCurveNode"),

    ("NurbsCurve", "NurbsCurve", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("knot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tessellation", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("closed", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tscale", "SFFloat", "1", "initializeOnly", "0", "0"),
        ("__points", "MFVec3f", (), "initializeOnly", "0", "0"),
        ("__numPoints", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DParametricGeometryNode"),

    ("NurbsCurve2D", "NurbsCurve2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "MFVec2d", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("knot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tessellation", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("closed", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tscale", "SFFloat", "1", "initializeOnly", "0", "0"),
    ), "X3DNurbsControlCurveNode"),

    ("NurbsOrientationInterpolator", "NurbsOrientationInterpolator", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("knot", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFRotation", ("0", "0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_knot", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_xyzw", "MFVec4f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_OK", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_knotrange", "SFVec2f", ("0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("NurbsPatchSurface", "NurbsPatchSurface", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uKnot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uOrder", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uDimension", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uTessellation", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uClosed", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vKnot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vOrder", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vDimension", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vTessellation", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vClosed", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tscale", "SFFloat", "1", "initializeOnly", "0", "0"),
    ), "X3DNurbsSurfaceGeometryNode"),

    ("NurbsPositionInterpolator", "NurbsPositionInterpolator", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("knot", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_knot", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_xyzw", "MFVec4f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_OK", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_knotrange", "SFVec2f", ("0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("NurbsSet", "NurbsSet", (
        ("addGeometry", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeGeometry", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geometry", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tessellationScale", "SFFloat", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("NurbsSurfaceInterpolator", "NurbsSurfaceInterpolator", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uKnot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uOrder", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uDimension", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vKnot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vOrder", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vDimension", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_fraction", "SFVec2f", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("position_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_uKnot", "MFFloat", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_vKnot", "MFFloat", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_controlPoint", "MFVec4f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_OK", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("NurbsSweptSurface", "NurbsSweptSurface", (
        ("crossSectionCurve", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("trajectoryCurve", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("method", "SFString", "FULL", "inputOnly", "0", "0"),  # TRANSLATE / FULL
        ("_patch", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("_method", "SFInt32", "2", "initializeOnly", "0", "0"),  # 1. Suv = Tv + Cu and delegate to patch 2. insert xsection at each profile tess point, and skin
    ), "X3DParametricGeometryNode"),

    ("NurbsSwungSurface", "NurbsSwungSurface", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("profileCurve", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("trajectoryCurve", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_patch", "SFNode", "NULL", "initializeOnly", "0", "0"),
    ), "X3DParametricGeometryNode"),

    ("NurbsTextureCoordinate", "NurbsTextureCoordinate", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "MFVec2f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uKnot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uOrder", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uDimension", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vKnot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vOrder", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vDimension", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_uKnot", "MFFloat", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_vKnot", "MFFloat", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_controlPoint", "MFVec4f", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSFNode"),

    # TrimmedSurface == PatchSurface + trimmingContour - keep them in the same order so Trimmed can be downcast to Patch
    ("NurbsTrimmedSurface", "NurbsTrimmedSurface", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("controlPoint", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weight", "MFDouble", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uKnot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uOrder", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uDimension", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uTessellation", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("uClosed", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vKnot", "MFDouble", (), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vOrder", "SFInt32", "3", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vDimension", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vTessellation", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("vClosed", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("addTrimmingContour", "MFNode", (), "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeTrimmingContour", "MFNode", (), "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("trimmingContour", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tscale", "SFFloat", "1", "initializeOnly", "0", "0"),
    ), "X3DNurbsSurfaceGeometryNode"),

    ###################################################################################

    # Chapter 28: Distributed Interactive Simulation Component

    ###################################################################################

    ("DISEntityManager", "DISEntityManager", (
        # freewrl replaced a few fields with the full network sensor and DIS entity interfaces, to match espduTransform and others
        # network sensor
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("timestamp", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("address", "SFString", "localhost", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("port", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayHost", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayPort", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("networkMode", "SFString", "standAlone", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkReader", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkWriter", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isStandAlone", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("readInterval", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("writeInterval", "SFTime", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rtpHeaderExpected", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isRtpHeaderHeard", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_registered", "SFBool", "FALSE", "initializeOnly", "0", "UNCA_NONE"),
        ("_dsock", "SFNode", "NULL", "initializeOnly", "0", "UNCA_NONE"),
        ("_lasttime", "SFTime", "0", "initializeOnly", "0", "UNCA_NONE"),
        ("_pduchange_networksensor", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_oldState", "SFNode", "NULL", "initializeOnly", "0", "0"),

        # DIS Entity
        ("entityID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("applicationID", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("siteID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # specs fields
        # address => ["SFString", "localhost", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        # port => ["SFInt32", 0, "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        # applicationID => ["SFInt32", 1, "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
        # siteID => ["SFInt32", 0, "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff

        ("mapping", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "( SPEC_X3D40)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("addedEntities", "MFNode", (), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removedEntities", "MFNode", (), "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # freewrl extra fields
        ("addEntities", "MFNode", (), "inputOnly", "0", "UNCA_NONE"),
        ("removeEntities", "MFNode", (), "inputOnly", "0", "UNCA_NONE"),
        ("entities", "MFNode", (), "inputOutput", "0", "UNCA_NONE"),
        # DIS createEntityPdu / removeEntityPdu (not sure what / how this works)
        ("_pduchange_create", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_pduchange_remove", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_pduchange_em_info", "SFInt32", "0", "initializeOnly", "0", "0"),
        # Field Change Detection

    ), "X3DChildNode"),

    ("DISEntityTypeMapping", "DISEntityTypeMapping", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("refresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),

        # Entity Type record:
        ("kind", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("domain", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("country", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("category", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("subcategory", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("specific", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("extra", "SFInt32", "0", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_child", "SFNode", "NULL", "initializeOnly", "0", "0"),
    ), "X3DInfoNode"),

    ("EspduTransform", "EspduTransform", (
        # network sensor
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("timestamp", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("address", "SFString", "localhost", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("port", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayHost", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayPort", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("networkMode", "SFString", "standAlone", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkReader", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkWriter", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isStandAlone", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("readInterval", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("writeInterval", "SFTime", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rtpHeaderExpected", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isRtpHeaderHeard", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_registered", "SFBool", "FALSE", "initializeOnly", "0", "UNCA_NONE"),
        ("_dsock", "SFNode", "NULL", "initializeOnly", "0", "UNCA_NONE"),
        ("_lasttime", "SFTime", "0", "initializeOnly", "0", "UNCA_NONE"),
        ("_pduchange_networksensor", "SFInt32", "0", "initializeOnly", "0", "0"),
        # Field Change Detection
        ("_oldState", "SFNode", "NULL", "initializeOnly", "0", "0"),

        # DIS Entity
        ("entityID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("applicationID", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("siteID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # Geo
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_GEO"),
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),

        # Info aka Entity Type Record, p262 of 2012 DIS draft specs (all are 8bit except country)
        ("entityKind", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("entityDomain", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("entityCountry", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("entityCategory", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("entitySubCategory", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("entitySpecific", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("entityExtra", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # _pduchange_es_info => ["SFInt32", 0, "initializeOnly", 0,0],#ff

        # team / side / force
        ("forceID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("marking", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # _pduchange_es_force => ["SFInt32", 0, "initializeOnly", 0,0],#ff

        # DIS EntityState > deadReckoning
        ("deadReckoning", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("linearVelocity", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("linearAcceleration", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ACCEL"),
        ("_p0", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("_v0", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_a0", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_angularVelocity", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "0", "0"),
        ("_r0", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "0", "0"),
        ("_change_count", "SFInt32", "0", "inputOutput", "0", "0"),
        ("_sent", "SFInt32", "0", "inputOutput", "0", "0"),
        ("_lastp0", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("_lastr0", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "0", "0"),
        ("_lastp0time", "SFTime", "0", "initializeOnly", "0", "UNCA_NONE"),
        ("_lastframetime", "SFTime", "0", "initializeOnly", "0", "UNCA_NONE"),
        ("_smoothingDelta", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("_smoothingCount", "SFInt32", "0", "initializeOnly", "0", "0"),
        # _pduchange_es_deadreckoning => ["SFInt32", 0, "initializeOnly", 0,0],#ff

        # DIS EntityState > articulationParameters
        ("set_articulationParameterValue0", "SFFloat", "0", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_articulationParameterValue1", "SFFloat", "0", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_articulationParameterValue2", "SFFloat", "0", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_articulationParameterValue3", "SFFloat", "0", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_articulationParameterValue4", "SFFloat", "0", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_articulationParameterValue5", "SFFloat", "0", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_articulationParameterValue6", "SFFloat", "0", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_articulationParameterValue7", "SFFloat", "0", "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterCount", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterDesignatorArray", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterChangeIndicatorArr", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterIdPartAttachedToAr", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterTypeArray", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterArray", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterValue0_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterValue1_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterValue2_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterValue3_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterValue4_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterValue5_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterValue6_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("articulationParameterValue7_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # _pduchange_es_articulation => ["SFInt32", 0, "initializeOnly", 0,0],#ff
        ("_pduchange_es", "SFInt32", "0", "initializeOnly", "0", "0"),

        # DIS collision
        ("collisionType", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("collideTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isCollided", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_pduchange_collision", "SFInt32", "0", "initializeOnly", "0", "0"),

        # DIS shared fire/collision
        ("eventEntityID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("eventApplicationID", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("eventSiteID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("eventNumber", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # DIS fire (as in 'fire weapon')
        ("fired1", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fired2", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fireMissionIndex", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("firingRange", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("firedTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_pduchange_fire", "SFInt32", "0", "initializeOnly", "0", "0"),

        # DIS detonation
        ("detonationLocation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("detonationRelativeLocation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("detonationResult", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("detonateTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isDetonated", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_pduchange_detonation", "SFInt32", "0", "initializeOnly", "0", "0"),

        # DIS shared fire/detonation
        ("munitionEntityID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("munitionApplicationID", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("munitionSiteID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("munitionStartPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("munitionEndPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        # > burst descriptor information
        ("munitionQuantity", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("firingRate", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fuse", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("warhead", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # DIS createEntityPdu / removeEntityPdu (not sure what / how this works)
        # _pduchange_create => ["SFInt32", 0, "initializeOnly", 0,0],#ff
        # _pduchange_remove => ["SFInt32", 0, "initializeOnly", 0,0],#ff

        # start same order as Transform >>>
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("scale", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("scaleOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        # fields for reducing redundant calls
        ("__do_center", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_trans", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_rotation", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_scaleO", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_scale", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_anything", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
        # << end same order as Transform
        # _pduchange_es_transform => ["SFInt32", 0, "initializeOnly", 0,0],#ff

    ), "X3DGroupingNode"),

    ("ReceiverPdu", "ReceiverPdu", (
        # network sensor
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("timestamp", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("address", "SFString", "localhost", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("port", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayHost", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayPort", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("networkMode", "SFString", "standAlone", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkReader", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkWriter", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isStandAlone", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("readInterval", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("writeInterval", "SFTime", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rtpHeaderExpected", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isRtpHeaderHeard", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_registered", "SFBool", "FALSE", "initializeOnly", "0", "UNCA_NONE"),
        ("_dsock", "SFNode", "NULL", "initializeOnly", "0", "UNCA_NONE"),
        ("_lasttime", "SFTime", "0", "initializeOnly", "0", "UNCA_NONE"),
        ("_pduchange_networksensor", "SFInt32", "0", "initializeOnly", "0", "0"),
        # Field Change Detection
        ("_oldState", "SFNode", "NULL", "initializeOnly", "0", "0"),

        # DIS Entity
        ("entityID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("applicationID", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("siteID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # Geo
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_GEO"),
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # DIS Receiver
        ("radioID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("whichGeometry", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("receiverState", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("receivedPower", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transmitterEntityID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transmitterApplicationID", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transmitterSiteID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transmitterRadioID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_pduchange_receiver", "SFInt32", "0", "initializeOnly", "0", "0"),

    ), "X3DChildNode"),

    ("SignalPdu", "SignalPdu", (
        # network sensor
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("timestamp", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("address", "SFString", "localhost", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("port", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayHost", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayPort", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("networkMode", "SFString", "standAlone", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkReader", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkWriter", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isStandAlone", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("readInterval", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("writeInterval", "SFTime", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rtpHeaderExpected", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isRtpHeaderHeard", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_registered", "SFBool", "FALSE", "initializeOnly", "0", "UNCA_NONE"),
        ("_dsock", "SFNode", "NULL", "initializeOnly", "0", "UNCA_NONE"),
        ("_lasttime", "SFTime", "0", "initializeOnly", "0", "UNCA_NONE"),
        ("_pduchange_networksensor", "SFInt32", "0", "initializeOnly", "0", "0"),
        # Field Change Detection
        ("_oldState", "SFNode", "NULL", "initializeOnly", "0", "0"),

        # DIS Entity
        ("entityID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("applicationID", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("siteID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # Geo
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_GEO"),
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # DIS SignalPdu
        ("radioID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("whichGeometry", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("data", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("dataLength", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("encodingScheme", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sampleRate", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("samples", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tdlType", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_pduchange_signal", "SFInt32", "0", "initializeOnly", "0", "0"),

    ), "X3DChildNode"),

    ("TransmitterPdu", "TransmitterPdu", (
        # network sensor
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("timestamp", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("address", "SFString", "localhost", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("port", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayHost", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("multicastRelayPort", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("networkMode", "SFString", "standAlone", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkReader", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isNetworkWriter", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isStandAlone", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("readInterval", "SFTime", "0.1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("writeInterval", "SFTime", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rtpHeaderExpected", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isRtpHeaderHeard", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_registered", "SFBool", "FALSE", "initializeOnly", "0", "UNCA_NONE"),
        ("_dsock", "SFNode", "NULL", "initializeOnly", "0", "UNCA_NONE"),
        ("_lasttime", "SFTime", "0", "initializeOnly", "0", "UNCA_NONE"),
        ("_pduchange_networksensor", "SFInt32", "0", "initializeOnly", "0", "0"),
        # Field Change Detection
        ("_oldState", "SFNode", "NULL", "initializeOnly", "0", "0"),

        # DIS Entity
        ("entityID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("applicationID", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("siteID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # Geo
        ("geoSystem", "MFString", ("GD", "WE"), "initializeOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("geoCoords", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_X3D33)", "UNCA_GEO"),
        ("__geoSystem", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # DIS Transmitter
        ("radioID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("whichGeometry", "SFInt32", "1", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("radioEntityTypeKind", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("radioEntityTypeDomain", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("radioEntityTypeCountry", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("radioEntityTypeCategory", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("radioEntityTypeNomenclature", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("radioEntityTypeNomenclatureVersion", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("antennaLocation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("antennaPatternLength", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("antennaPatternType", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("relativeAntennaLocation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),

        ("inputSource", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("transmitState", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("power", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("frequency", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transmitFrequencyBandwidth", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("lengthOfModulationParameters", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("modulationTypeDetail", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("modulationTypeMajor", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("modulationTypeSpreadSpectrum", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("modulationTypeSystem", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("cryptoSystem", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("cryptoKeyID", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_pduchange_transmitter", "SFInt32", "0", "initializeOnly", "0", "0"),

    ), "X3DChildNode"),

    ###################################################################################

    #   29. Scripting Component

    ###################################################################################
    ("Script", "Script", (
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("refresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),

        ("directOutput", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mustEvaluate", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__scriptObj", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DScriptNode"),

    ###################################################################################

    #   32. CAD Component

    ###################################################################################

    ("CADAssembly", "CADAssembly", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
    ), "X3DGroupingNode"),

    ("CADFace", "CADFace", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shape", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DProductStructureChildNode"),

    ("CADLayer", "CADLayer", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("visibles", "MFBool", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DGroupingNode"),

    ("CADPart", "CADPart", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("scale", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("scaleOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # fields for reducing redundant calls
        ("__do_center", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_trans", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_rotation", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_scaleO", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_scale", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_anything", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("_sortedChildren", "MFNode", (), "inputOutput", "0", "0"),
    ), "X3DGroupingNode"),

    ("IndexedQuadSet", "IndexedQuadSet", (
        ("set_index", "MFInt32", None, "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("index", "MFInt32", (), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DComposedGeometryNode"),

    ("QuadSet", "QuadSet", (
        ("attrib", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fogCoord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normal", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("ccw", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("normalPerVertex", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("solid", "SFBool", "TRUE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_coordIndex", "MFInt32", (), "initializeOnly", "0", "0"),
    ), "X3DComposedGeometryNode"),

    ###################################################################################

    #   30. EventUtilities Component

    ###################################################################################

    ("BooleanFilter", "BooleanFilter", (
        ("set_boolean", "SFBool", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("inputFalse", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("inputNegate", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("inputTrue", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("BooleanSequencer", "BooleanSequencer", (
        ("next", "SFBool", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("previous", "SFBool", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFBool", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_index", "SFInt32", "-1", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # web3d.org debate 0 vs -1
    ), "X3DSequencerNode"),

    ("BooleanToggle", "BooleanToggle", (
        ("set_boolean", "SFBool", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("toggle", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DChildNode"),

    ("BooleanTrigger", "BooleanTrigger", (
        ("set_triggerTime", "SFTime", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("triggerTrue", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTriggerNode"),

    ("IntegerSequencer", "IntegerSequencer", (
        ("next", "SFBool", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("previous", "SFBool", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_fraction", "SFFloat", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("key", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("keyValue", "MFInt32", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value_changed", "SFInt32", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_index", "SFInt32", "-1", "initializeOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSequencerNode"),

    ("IntegerTrigger", "IntegerTrigger", (
        ("set_boolean", "SFBool", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("integerKey", "SFInt32", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("triggerValue", "SFInt32", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTriggerNode"),

    ("TimeTrigger", "TimeTrigger", (
        ("set_boolean", "SFBool", None, "inputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("triggerTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DTriggerNode"),

    ###################################################################################

    #   31. ProgrammableShaders Component

    ###################################################################################

    ("ComposedShader", "ComposedShader", (
        ("activate", "SFBool", None, "inputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("parts", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isSelected", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isValid", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("language", "SFString", "", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_initialized", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("_shaderUserDefinedFields", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("_shaderUserNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),
        ("_shaderLoadThread", "FreeWRLThread", "0", "initializeOnly", "0", "0"),
        ("_retrievedURLData", "SFBool", "FALSE", "initializeOnly", "0", "0"),
    ), "X3DShaderNode"),

    ("FloatVertexAttribute", "FloatVertexAttribute", (
        ("value", "MFFloat", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("numComponents", "SFInt32", "4", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # 1...4 valid values
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DVertexAttributeNode"),

    ("Matrix3VertexAttribute", "Matrix3VertexAttribute", (
        ("value", "MFMatrix3f", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DVertexAttributeNode"),

    ("Matrix4VertexAttribute", "Matrix4VertexAttribute", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("value", "MFMatrix4f", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("name", "SFString", "", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DVertexAttributeNode"),

    ("PackagedShader", "PackagedShader", (
        ("activate", "SFBool", None, "inputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("refresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("isSelected", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isValid", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("language", "SFString", "", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_initialized", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("_shaderUserNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),
        ("_shaderUserDefinedFields", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("_shaderLoadThread", "FreeWRLThread", "0", "initializeOnly", "0", "0"),
        ("_retrievedURLData", "SFBool", "FALSE", "initializeOnly", "0", "0"),
    ), "X3DProgrammableShaderObject"),

    ("ProgramShader", "ProgramShader", (
        ("activate", "SFBool", None, "inputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("programs", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isSelected", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isValid", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("language", "SFString", "", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_initialized", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("_shaderUserNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),
        ("_shaderLoadThread", "FreeWRLThread", "0", "initializeOnly", "0", "0"),
        ("_retrievedURLData", "SFBool", "FALSE", "initializeOnly", "0", "0"),
    ), "X3DProgrammableShaderObject"),

    ("ShaderPart", "ShaderPart", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("refresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("type", "SFString", "VERTEX", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_shaderUserDefinedFields", "SFNode", "NULL", "initializeOnly", "0", "0"),
    ), "X3DUrlObject"),

    ("ShaderProgram", "ShaderProgram", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("refresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("type", "SFString", "", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_shaderUserDefinedFields", "SFNode", "NULL", "initializeOnly", "0", "0"),
    ), "X3DUrlObject"),

    # castle EffectPart made from ShaderPart - fields in same order
    ("EffectPart", "EffectPart", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("type", "SFString", "VERTEX", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_shaderUserDefinedFields", "SFNode", "NULL", "initializeOnly", "0", "0"),
    ), "X3DUrlObject"),

    # castle Effect made from ComposedShader - fields in same order
    ("Effect", "Effect", (
        ("activate", "SFBool", None, "inputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("parts", "MFNode", (), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isSelected", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isValid", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("language", "SFString", "", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_initialized", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("_shaderUserDefinedFields", "SFNode", "NULL", "initializeOnly", "0", "0"),
        ("_shaderUserNumber", "SFInt32", "-1", "initializeOnly", "0", "0"),
        ("_shaderLoadThread", "FreeWRLThread", "0", "initializeOnly", "0", "0"),
        ("_retrievedURLData", "SFBool", "FALSE", "initializeOnly", "0", "0"),
    ), "X3DShaderNode"),

    ###################################################################################

    #   33. Texturing3D Component

    ###################################################################################
    ("ImageTexture3D", "ImageTexture3D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("load", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__oldload", "SFBool", "FALSE", "initializeOnly", "0", "0"),
        ("autoRefresh", "SFTime", "0", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("autoRefreshTimeLimit", "SFTime", "3600", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__lasttime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("repeatS", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatT", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatR", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "0", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_needs_gradient", "SFBool", "FALSE", "initializeOnly", "0", "0"),
    ), "X3DTextureNode"),

    ("PixelTexture3D", "PixelTexture3D", (
        ("image", "MFInt32", "0, 0, 0, 0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatS", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatT", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatR", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "0", "initializeOnly", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_needs_gradient", "SFBool", "FALSE", "initializeOnly", "0", "0"),
    ), "X3DTextureNode"),

    ("TextureCoordinate3D", "TextureCoordinate3D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("point", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DTextureCoordinateNode"),

    ("TextureCoordinate4D", "TextureCoordinate4D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("point", "MFVec4f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DTextureCoordinateNode"),

    ("TextureTransformMatrix3D", "TextureTransformMatrix3D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("matrix", "SFMatrix4f", ("1", "0", "0", "0", "0", "1", "0", "0", "0", "0", "1", "0", "0", "0", "0", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DTextureTransformNode"),

    ("TextureTransform3D", "TextureTransform3D", (
        ("center", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("scale", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mapping", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DTextureTransformNode"),

    ("ComposedTexture3D", "ComposedTexture3D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texture", "MFNode", None, "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("textureProperties", "SFNode", "0", "initializeOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("repeatS", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatT", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("repeatR", "SFBool", "FALSE", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__textureTableIndex", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DTexture3DNode"),

    ###################################################################################

    #   35. Layering Component

    ###################################################################################

    ("Viewport", "Viewport", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("clipBoundary", "MFFloat", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DViewportNode"),

    ("Layer", "Layer", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPickable", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickable", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("viewport", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("objectType", "MFString", ("ALL",), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DLayerNode"),

    ("LayerSet", "LayerSet", (
        ("activeLayer", "SFInt32", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("layers", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "MFInt32", ("0",), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DLayerSetNode"),

    ###################################################################################

    #   36. Layout Component

    ###################################################################################
    ("Layout", "Layout", (
        ("align", "MFString", ("CENTER", "CENTER"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("offset", "MFFloat", ("0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("offsetUnits", "MFString", ("WORLD", "WORLD"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("scaleMode", "MFString", ("NONE", "NONE"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("size", "MFFloat", ("1", "1"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sizeUnits", "MFString", ("WORLD", "WORLD"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_align", "MFInt32", ("0", "0"), "initializeOnly", "0", "0"),
        ("_offsetUnits", "MFInt32", ("0", "0"), "initializeOnly", "0", "0"),
        ("_scaleMode", "MFInt32", ("0", "0"), "initializeOnly", "0", "0"),
        ("_sizeUnits", "MFInt32", ("0", "0"), "initializeOnly", "0", "0"),
        ("_scale", "MFFloat", ("1", "1"), "initializeOnly", "0", "0"),
    ), "X3DLayoutNode"),

    ("LayoutGroup", "LayoutGroup", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("layout", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("viewport", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DGroupingNode"),

    ("LayoutLayer", "LayoutLayer", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPickable", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickable", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("viewport", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("layout", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("objectType", "MFString", ("ALL",), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DGroupingNode"),

    ("ScreenFontStyle", "ScreenFontStyle", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("family", "MFString", ("SERIF",), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("horizontal", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("justify", "MFString", ("BEGIN",), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("language", "SFString", "", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("leftToRight", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pointSize", "SFFloat", "12", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("spacing", "SFFloat", "1", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("style", "SFString", "PLAIN", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("topToBottom", "SFBool", "TRUE", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DFontStyleNode"),

    ("ScreenGroup", "ScreenGroup", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DGroupingNode"),

    ###################################################################################

    #   37. Rigid Body Physics Component

    ###################################################################################

    ("BallJoint", "BallJoint", (
        ("anchorPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("body1", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("forceOutput", "MFString", ("NONE",), "inputOutput", "(SPEC_VRML | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1AnchorPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("body2AnchorPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("_joint", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_forceout", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__old_anchorPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_body1", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__old_body2", "SFNode", "NULL", "inputOutput", "0", "0"),
    ), "X3DRigidJointNode"),

    ("CollidableOffset", "CollidableOffset", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__do_trans", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_rotation", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("collidable", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_geom", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_initialRotation", "SFRotation", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("_initialTranslation", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_initialized", "SFBool", "0", "initializeOnly", "0", "0"),
        ("_csensor", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DNBodyCollidableNode"),

    ("CollidableShape", "CollidableShape", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("translation", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("__do_trans", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("__do_rotation", "SFInt32", "FALSE", "initializeOnly", "0", "0"),
        ("shape", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_geom", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_initialRotation", "SFRotation", ("0", "0", "1", "0"), "initializeOnly", "0", "0"),
        ("_initialTranslation", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_initialized", "SFBool", "0", "initializeOnly", "0", "0"),
        ("_csensor", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DNBodyCollidableNode"),

    ("CollisionCollection", "CollisionCollection", (
        ("appliedParameters", "MFString", ("BOUNCE",), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("collidables", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("frictionCoefficients", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("minBounceSpeed", "SFFloat", "0.1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),  # see note top of file
        ("slipFactors", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("softnessConstantForceMix", "SFFloat", "0.0001", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),  # see note top of file
        ("softnessErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("surfaceSpeed", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_class", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_csensor", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_appliedParametersMask", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DChildNode"),

    ("CollisionSensor", "CollsionSensor", (
        ("collider", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intersections", "MFNode", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("contacts", "MFNode", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSensorNode"),

    ("CollisionSpace", "CollisionSpace", (
        ("collidables", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("useGeometry", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_space", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DNBodyCollidableNode"),

    ("Contact", "Contact", (
        ("appliedParameters", "MFString", ("BOUNCE",), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("contactNormal", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("depth", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("frictionCoefficients", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("frictionDirection", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geometry1", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geometry2", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("minBounceSpeed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("position", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("slipCoefficients", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("softnessConstantForceMix", "SFFloat", "0.0001", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),
        ("softnessErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceSpeed", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("_appliedParameters", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DSFNode"),

    ("DoubleAxisHingeJoint", "DoubleAxisHingeJoint", (
        ("anchorPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("axis1", "SFVec3f", ("1", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("axis2", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("desiredAngularVelocity1", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLERATE"),
        ("desiredAngularVelocity2", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLERATE"),
        ("forceOutput", "MFString", ("NONE",), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxAngle1", "SFFloat", "PIF+", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("maxTorque1", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_TORQUE"),
        ("maxTorque2", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_TORQUE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("minAngle1", "SFFloat", "-PIF+", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        # v3.3-- names for stop
        ("stopBounce1", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopConstantForceMix1", "SFFloat", "0.001", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),
        ("stopErrorCorrection1", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # v4 names for stop
        ("stop1Bounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop1ConstantForceMix", "SFFloat", "0.001", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),
        ("stop1ErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("suspensionErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("suspensionForce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),
        ("body1AnchorPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("body1Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2AnchorPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("body2Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("hinge1Angle", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("hinge1AngleRate", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLERATE"),
        ("hinge2Angle", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("hinge2AngleRate", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLERATE"),
        ("_joint", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_forceout", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__old_anchorPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_axis1", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_axis2", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_body1", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__old_body2", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("_motor1", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_motor2", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("axis1Angle", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),  # NOT IN SPECS, DO WE USE THIS?
    ), "X3DRigidJointNode"),

    ("MotorJoint", "MotorJoint", (
        ("axis1Angle", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("axis1Torque", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_TORQUE"),
        ("axis2Angle", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("axis2Torque", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_TORQUE"),
        ("axis3Angle", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("axis3Torque", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_TORQUE"),
        ("body1", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabledAxes", "SFInt32", "1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("forceOutput", "MFString", ("NONE",), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("motor1Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("motor2Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("motor3Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop1Bounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop1ErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop2Bounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop2ErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop3Bounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop3ErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("motor1Angle", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("motor1AngleRate", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("motor2Angle", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("motor2AngleRate", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("motor3Angle", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("motor3AngleRate", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("autoCalc", "SFBool", "FALSE", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_joint", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_forceout", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__old_motor1Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("__old_motor2Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("__old_motor3Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "0", "0"),
        ("__old_body1", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__old_body2", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__old_axis1Angle", "SFFloat", "0", "inputOutput", "0", "0"),
        ("__old_axis2Angle", "SFFloat", "0", "inputOutput", "0", "0"),
        ("__old_axis3Angle", "SFFloat", "0", "inputOutput", "0", "0"),
    ), "X3DRigidJointNode"),

    ("RigidBody", "RigidBody", (
        ("angularDampingFactor", "SFFloat", "0.001", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # or UNCA_ANGLRATE
        ("angularVelocity", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLERATE"),
        ("autoDamp", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("autoDisable", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("centerOfMass", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("disableAngularSpeed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLERATE"),
        ("disableLinearSpeed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("disableTime", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("finiteRotationAxis", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fixed", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("forces", "MFVec3f", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),
        ("geometry", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("inertia", "SFMatrix3f", ("1", "0", "0", "0", "1", "0", "0", "0", "1"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_MOMENT"),
        ("linearDampingFactor", "SFFloat", "0.001", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("linearVelocity", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("mass", "SFFloat", "1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_MASS"),
        ("massDensityModel", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("position", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("torques", "MFVec3f", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_TORQUE"),
        ("useFiniteRotation", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("useGlobalGravity", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_body", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__old_angularVelocity", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_centerOfMass", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_finiteRotationAxis", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_linearVelocity", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_orientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "0", "0"),
        ("__old_position", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("_geomIdentityTransform", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DSFNode"),

    ("RigidBodyCollection", "RigidBodyCollection", (
        ("set_contacts", "MFNode", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("autoDisable", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bodies", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("constantForceMix", "SFFloat", "0.0001", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("contactSurfaceThickness", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("disableAngularSpeed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("disableLinearSpeed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("disableTime", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("errorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("gravity", "SFVec3f", ("0", "-9.8", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),
        ("iterations", "SFInt32", "10", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("joints", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxCorrectionSpeed", "SFFloat", "-1.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("preferAccuracy", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("collider", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_world", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        # _space => ["FreeWRLPTR", 0, "initializeOnly", 0,0],#ff
        ("_group", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
    ), "X3DChildNode"),

    ("SingleAxisHingeJoint", "SingleAxisHingeJoint", (
        ("anchorPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("axis", "SFVec3f", ("0", "0", "1"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("forceOutput", "MFString", ("NONE",), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxAngle", "SFFloat", "PIF+", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("minAngle", "SFFloat", "-PIF+", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("stopBounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("angle", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("angleRate", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1AnchorPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2AnchorPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_joint", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_forceout", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__old_anchorPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_axis", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_body1", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__old_body2", "SFNode", "NULL", "inputOutput", "0", "0"),
    ), "X3DRigidJointNode"),

    ("SliderJoint", "SliderJoint", (
        ("axis", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("forceOutput", "MFString", ("NONE",), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxSeparation", "SFFloat", "1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("minSeparation", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("sliderForce", "SFFloat", "0", "inputOutput", "( SPEC_X3D33)", "UNCA_FORCE"),
        ("stopBounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stopErrorCorrection", "SFFloat", "1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("separation", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("separationRate", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_joint", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_forceout", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__old_axis", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_body1", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__old_body2", "SFNode", "NULL", "inputOutput", "0", "0"),
    ), "X3DRigidJointNode"),

    ("UniversalJoint", "UniversalJoint", (
        ("anchorPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("axis1", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("axis2", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("forceOutput", "MFString", ("NONE",), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop1Bounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop1ErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop2Bounce", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stop2ErrorCorrection", "SFFloat", "0.8", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1AnchorPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body1Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2AnchorPoint", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("body2Axis", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_joint", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_forceout", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("__old_anchorPoint", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_axis1", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_axis2", "SFVec3f", ("0", "0", "0"), "inputOutput", "0", "0"),
        ("__old_body1", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("__old_body2", "SFNode", "NULL", "inputOutput", "0", "0"),
    ), "X3DRigidJointNode"),

    ###################################################################################

    #   38. Picking Component

    ###################################################################################

    # A PickableGroup node is an X3DGroupingNode that contains children that are marked
    # as being of a given classification of picking types, as well as the ability to enable or disable picking of the children.

    # DJTRACK_PICKSENSORS
    ("PickableGroup", "PickableGroup", (
        ("addChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("removeChildren", "MFNode", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__sibAffectors", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("objectType", "MFString", ("ALL", "NONE", "TERRAIN"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickable", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

        # FreeWRL__protoDef => ["SFInt32", "INT_ID_UNDEFINED", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)"], # tell renderer that this is a proto...
        # FreeWRL_PROTOInterfaceNodes =>["MFNode", [], "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)","UNCA_NONE"],#ff
    ), "X3DGroupingNode"),

    # The PointPickSensor node tests one or more points in space as lying inside the provided target geometry.
    # For each point that lies inside the geometry, the point coordinate is returned in the pickedGeometry field
    # with the corresponding geometry inside which the point lies.
    # Because points represent an infinitely small location in space, the "CLOSEST" and "ALL_SORTED" sort orders
    # are defined to mean "ANY" and "ALL" respectively.

    ("PointPickSensor", "PointPickSensor", (
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("objectType", "MFString", ("ALL", "NONE", "TERRAIN"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickingGeometry", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickTarget", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickedGeometry", "MFNode", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intersectionType", "SFString", "BOUNDS", "initializeOnly", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sortOrder", "SFString", "CLOSEST", "initializeOnly", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("matchCriterion", "SFString", "MATCH_ANY", "inputOutput", "(SPEC_X3D33)", "UNCA_NONE"),
        # These fields are used for the info.
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
        ("pickedPoint", "MFVec3f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        # DJTRACK
        ("_oldisActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_oldpickTarget", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_oldpickedGeometry", "MFNode", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_oldpickedPoint", "MFVec3f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("_bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("set_intersectionType", "SFString", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_sortOrder", "SFString", None, "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSensorNode"),

    ("LinePickSensor", "LinePickSensor", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("objectType", "MFString", ("ALL", "NONE", "TERRAIN"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickingGeometry", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickTarget", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickedGeometry", "MFNode", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intersectionType", "SFString", "BOUNDS", "initializeOnly", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sortOrder", "SFString", "CLOSEST", "initializeOnly", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("matchCriterion", "SFString", "MATCH_ANY", "inputOutput", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # These fields are used for the info.
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
        ("pickedPoint", "MFVec3f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickedNormal", "MFVec3f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickedTextureCoordinate", "MFVec3f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSensorNode"),

    # 38.4.4 PrimitivePickSensor
    ("PrimitivePickSensor", "PrimitivePickSensor", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("objectType", "MFString", ("ALL", "NONE", "TERRAIN"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickingGeometry", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickTarget", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickedGeometry", "MFNode", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intersectionType", "SFString", "BOUNDS", "initializeOnly", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sortOrder", "SFString", "CLOSEST", "initializeOnly", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("matchCriterion", "SFString", "MATCH_ANY", "inputOutput", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # These fields are used for the info.
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DSensorNode"),

    # 38.4.5 VolumePickSensor
    ("VolumePickSensor", "VolumePickSensor", (
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("objectType", "MFString", ("ALL", "NONE", "TERRAIN"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickingGeometry", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickTarget", "MFNode", (), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("pickedGeometry", "MFNode", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intersectionType", "SFString", "BOUNDS", "initializeOnly", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("sortOrder", "SFString", "CLOSEST", "initializeOnly", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("matchCriterion", "SFString", "MATCH_ANY", "inputOutput", "(SPEC_VRML | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # These fields are used for the info.
        ("__oldEnabled", "SFBool", "TRUE", "inputOutput", "0", "0"),
    ), "X3DSensorNode"),

    ###################################################################################

    #   39. Followers Component

    ###################################################################################

    # value_changed is the first field-type-sepcific field so that offsetof(,value_changed) will be generic for all chasers, and for all dampers
    ("ColorChaser", "ColorChaser", (
        ("metadata", "SFNode", "NULL", "inputOutput", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration", "SFTime", "1", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_bufferendtime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_steptime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("value_changed", "SFColor", ("0", "0", "0"), "outputOnly", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFColor", ("0.8", "0.8", "0.8"), "initializeOnly", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialValue", "SFColor", ("0.8", "0.8", "0.8"), "initializeOnly", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_destination", "SFColor", ("0", "0", "0"), "inputOnly", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFColor", ("0", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_buffer", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_previousvalue", "SFColor", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_destination", "SFColor", ("0", "0", "0"), "initializeOnly", "0", "0"),
    ), "X3DChaserNode"),

    ("ColorDamper", "ColorDamper", (
        ("metadata", "SFNode", "NULL", "inputOutput", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("tau", "SFTime", "0.3", "inputOutput", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tolerance", "SFFloat", "-1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_lasttick", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_takefirstinput", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("value_changed", "SFColor", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFColor", ("0.8", "0.8", "0.8"), "initializeOnly", "( SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialValue", "SFColor", ("0.8", "0.8", "0.8"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_destination", "SFColor", ("0", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFColor", ("0", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_values", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_input", "SFColor", ("0", "0", "0"), "initializeOnly", "0", "0"),

    ), "X3DDamperNode"),

    ("CoordinateChaser", "CoordinateChaser", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration", "SFTime", "1", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_bufferendtime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_steptime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("value_changed", "MFVec3f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "MFVec3f", (("0", "0", "0"),), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("initialValue", "MFVec3f", (("0", "0", "0"),), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("set_destination", "MFVec3f", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "MFVec3f", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_buffer", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_previousvalue", "MFVec3f", (("0", "0", "0"),), "initializeOnly", "0", "0"),
        ("_destination", "MFVec3f", (("0", "0", "0"),), "initializeOnly", "0", "0"),
    ), "X3DChaserNode"),

    ("CoordinateDamper", "CoordinateDamper", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tolerance", "SFFloat", "-1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_lasttick", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_takefirstinput", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("value_changed", "MFVec3f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "MFVec3f", (("0", "0", "0"),), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("initialValue", "MFVec3f", (("0", "0", "0"),), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("set_destination", "MFVec3f", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "MFVec3f", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_values", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_input", "MFVec3f", (), "initializeOnly", "0", "0"),
    ), "X3DDamperNode"),

    ("OrientationChaser", "OrientationChaser", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration", "SFTime", "1", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_bufferendtime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_steptime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("value_changed", "SFRotation", ("0", "1", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("initialValue", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("set_destination", "SFRotation", ("0", "1", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFRotation", ("0", "1", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_buffer", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_previousvalue", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "0", "0"),
        ("_destination", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "0", "0"),
    ), "X3DChaserNode"),

    ("OrientationDamper", "OrientationDamper", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tolerance", "SFFloat", "-1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_lasttick", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_takefirstinput", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("value_changed", "SFRotation", ("0", "1", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("initialValue", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("set_destination", "SFRotation", ("0", "1", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFRotation", ("0", "1", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_values", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_input", "SFRotation", ("0", "1", "0", "0"), "initializeOnly", "0", "0"),
    ), "X3DDamperNode"),

    ("PositionChaser", "PositionChaser", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration", "SFTime", "1", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_bufferendtime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_steptime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("value_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("initialValue", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("set_destination", "SFVec3f", ("0", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFVec3f", ("0", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_buffer", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_previousvalue", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_destination", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
    ), "X3DChaserNode"),

    ("PositionDamper", "PositionDamper", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tolerance", "SFFloat", "-1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_lasttick", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_takefirstinput", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("value_changed", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("initialValue", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("set_destination", "SFVec3f", ("0", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFVec3f", ("0", "0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_values", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_input", "SFVec3f", ("0", "0", "0"), "initializeOnly", "0", "0"),
    ), "X3DDamperNode"),

    ("PositionChaser2D", "PositionChaser2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration", "SFTime", "1", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_bufferendtime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_steptime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("value_changed", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFVec2f", ("0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("initialValue", "SFVec2f", ("0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("set_destination", "SFVec2f", ("0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFVec2f", ("0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_buffer", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_previousvalue", "SFVec2f", ("0", "0"), "initializeOnly", "0", "0"),
        ("_destination", "SFVec2f", ("0", "0"), "initializeOnly", "0", "0"),
    ), "X3DChaserNode"),

    ("PositionDamper2D", "PositionDamper2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tolerance", "SFFloat", "-1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_lasttick", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_takefirstinput", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("value_changed", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFVec2f", ("0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("initialValue", "SFVec2f", ("0", "0"), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("set_destination", "SFVec2f", ("0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFVec2f", ("0", "0"), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_values", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_input", "SFVec2f", ("0", "0"), "initializeOnly", "0", "0"),
    ), "X3DDamperNode"),

    ("ScalarChaser", "ScalarChaser", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration", "SFTime", "1", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_bufferendtime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_steptime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("value_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFFloat", "0", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialValue", "SFFloat", "0", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_destination", "SFFloat", "0", "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFFloat", "0", "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_buffer", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_previousvalue", "SFFloat", "0", "initializeOnly", "0", "0"),
        ("_destination", "SFFloat", "0", "initializeOnly", "0", "0"),
    ), "X3DChaserNode"),

    ("ScalarDamper", "ScalarDamper", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tolerance", "SFFloat", "-1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_lasttick", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_takefirstinput", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("value_changed", "SFFloat", "0", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "SFFloat", "0", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialValue", "SFFloat", "0", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_destination", "SFFloat", "0", "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "SFFloat", "0", "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_values", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_input", "SFFloat", "0", "initializeOnly", "0", "0"),
    ), "X3DDamperNode"),

    ("TexCoordChaser2D", "TexCoordChaser2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("duration", "SFTime", "1", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_bufferendtime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_steptime", "SFTime", "0", "initializeOnly", "0", "0"),
        ("value_changed", "MFVec2f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "MFVec2f", (("0", "0"),), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialValue", "MFVec2f", (("0", "0"),), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_destination", "MFVec2f", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "MFVec2f", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_buffer", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_previousvalue", "MFVec2f", (("0", "0"),), "initializeOnly", "0", "0"),
        ("_destination", "MFVec2f", (("0", "0"),), "initializeOnly", "0", "0"),
    ), "X3DChaserNode"),

    ("TexCoordDamper2D", "TexCoordDamper2D", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_p", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_t", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tolerance", "SFFloat", "-1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("order", "SFInt32", "3", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tau", "SFTime", "0.3", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_lasttick", "SFTime", "0", "initializeOnly", "0", "0"),
        ("_takefirstinput", "SFBool", "TRUE", "initializeOnly", "0", "0"),
        ("value_changed", "MFVec2f", (), "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialDestination", "MFVec2f", (("0", "0"),), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("initialValue", "MFVec2f", (("0", "0"),), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_destination", "MFVec2f", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("set_value", "MFVec2f", (), "inputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_values", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_input", "MFVec2f", (), "initializeOnly", "0", "0"),
    ), "X3DDamperNode"),

    ###################################################################################

    #   40. Particle Systems Component

    ###################################################################################
    # 40.4.1 BoundedPhysicsModel
    ("BoundedPhysicsModel", "BoundedPhysicsModel", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geometry", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DParticlePhysicsModelNode"),

    # 40.4.2 ConeEmitter
    ("ConeEmitter", "ConeEmitter", (
        ("angle", "SFFloat", "PIF*.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("direction", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("position", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("speed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("variation", "SFFloat", "0.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mass", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_MASS"),
        ("surfaceArea", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_AREA"),
    ), "X3DParticleEmitterNode"),

    # 40.4.3 ExplosionEmitter
    ("ExplosionEmitter", "ExplosionEmitter", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("position", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("speed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("variation", "SFFloat", "0.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mass", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_MASS"),
        ("surfaceArea", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_AREA"),
    ), "X3DParticleEmitterNode"),

    # 40.4.4 ForcePhysicsModel
    ("ForcePhysicsModel", "ForcePhysicsModel", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("force", "SFVec3f", ("0", "-9.8", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DParticlePhysicsModelNode"),

    # Extra ResistancePhysicsModel
    ("ResistancePhysicsModel", "ResistancePhysicsModel", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("force", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_FORCE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DParticlePhysicsModelNode"),

    # 40.4.5 ParticleSystem
    ("ParticleSystem", "ParticleSystem", (
        # shared with Shape, keep in same order as Shape:
        ("appearance", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geometry", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_X3D40)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_X3D40)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("castShadow", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_shaderflags_base", "SFInt32", "0", "initializeOnly", "0", "0"),  # shaders
        ("_shaderflags_effects", "SFInt32", "0", "initializeOnly", "0", "0"),  # shaders
        ("_shaderflags_usershaders", "SFInt32", "0", "initializeOnly", "0", "0"),  # shaders
        # particlesystem specific:
        ("createParticles", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("lifetimeVariation", "SFFloat", "0.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("maxParticles", "SFInt32", "200", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("particleLifetime", "SFFloat", "5", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("particleSize", "SFVec2f", ("0.02", "0.02"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("particleOrientation", "SFRotation", ("0", "0", "1", "0"), "inputOutput", "0", "0"),
        ("isActive", "SFBool", "TRUE", "outputOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorRamp", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("colorKey", "MFFloat", (), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("emitter", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geometryType", "SFString", "QUAD", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("physics", "MFNode", (), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoordRamp", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("texCoord", "SFNode", "NULL", "initializeOnly", "(SPEC_X3D40)", "UNCA_NONE"),
        ("texCoordKey", "MFFloat", (), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_tris", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_ttex", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_ltex", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_particles", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_lasttime", "SFDouble", "0", "initializeOnly", "0", "0"),
        ("_lastEnabled", "SFBool", "FALSE", "inputOutput", "0", "0"),
        ("_geometryType", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_remainder", "SFFloat", "0", "initializeOnly", "0", "0"),
    ), "X3DShapeNode"),

    # 40.4.6 PointEmitter
    ("PointEmitter", "PointEmitter", (
        ("direction", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("position", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("speed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("variation", "SFFloat", "0.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mass", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_MASS"),
        ("surfaceArea", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_AREA"),
    ), "X3DParticleEmitterNode"),

    # 40.4.7 PolylineEmitter
    ("PolylineEmitter", "PolylineEmitter", (
        ("set_coordIndex", "MFInt32", (), "inputOnly", "(SPEC_X3D33)", "UNCA_NONE"),
        ("set_coordinate", "SFInt32", "0", "inputOnly", "(SPEC_X3D32)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("direction", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("speed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("variation", "SFFloat", "0.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("coordIndex", "MFInt32", ("-1",), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mass", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_MASS"),
        ("surfaceArea", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_AREA"),
        ("_method", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_nseg", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_segs", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("_portions", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
    ), "X3DParticleEmitterNode"),

    # 40.4.8 SurfaceEmitter
    ("SurfaceEmitter", "SurfaceEmitter", (
        ("set_coordIndex", "MFInt32", (), "inputOnly", "( SPEC_X3D33)", "UNCA_NONE"),
        ("set_coordinate", "SFInt32", "0", "inputOnly", "(SPEC_X3D32)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("speed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("variation", "SFFloat", "0.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("coordIndex", "MFInt32", ("-1",), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mass", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_MASS"),
        ("surfaceArea", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_AREA"),
        ("surface", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("geometry", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_ifs", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
    ), "X3DParticleEmitterNode"),

    # 40.4.9 VolumeEmitter
    ("VolumeEmitter", "VolumeEmitter", (
        ("set_coordIndex", "MFInt32", (), "inputOnly", "( SPEC_X3D33)", "UNCA_NONE"),
        ("set_coordinate", "SFInt32", "0", "inputOnly", "(SPEC_X3D32)", "UNCA_NONE"),
        ("coord", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("direction", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("speed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("variation", "SFFloat", "0.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("coordIndex", "MFInt32", ("-1",), "initializeOnly", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("internal", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("mass", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_MASS"),
        ("surfaceArea", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_AREA"),
        ("_ifs", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
    ), "X3DParticleEmitterNode"),

    # 40.4.10 WindPhysicsModel
    ("WindPhysicsModel", "WindPhysicsModel", (
        ("direction", "SFVec3f", ("1", "0", "0"), "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("gustiness", "SFFloat", "0.1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("speed", "SFFloat", "0.1", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("turbulence", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_frameSpeed", "SFFloat", "0", "initializeOnly", "0", "0"),
    ), "X3DParticlePhysicsModelNode"),

    # dug9 Humanoid Particle experiment
    ("MapEmitter", "MapEmitter", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("on", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("speed", "SFFloat", "0", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_SPEED"),
        ("variation", "SFFloat", "0.25", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("functionMap", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("gridSize", "SFVec2f", ("1", "1"), "initializeOnly", "0", "0"),
        ("emitterColor", "MFColor", (), "inputOutput", "0", "0"),
        ("colorMatchTolerance", "SFFloat", "0.01", "initializeOnly", "0", "0"),
        ("classified", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("eboxes", "MFVec4f", (), "inputOnly", "0", "0"),
        ("iboxes", "MFVec4f", (), "inputOnly", "0", "0"),
    ), "X3DParticleEmitterNode"),

    ("MapPhysicsModel", "MapPhysicsModel", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("gridSize", "SFVec2f", ("1", "1"), "initializeOnly", "0", "0"),
        ("functionMap", "SFNode", "NULL", "inputOutput", "0", "0"),
        ("obstacleColor", "SFColor", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("sinkColor", "MFColor", (), "initializeOnly", "0", "0"),
        ("pauseColor", "SFColor", ("1", "0", "0"), "initializeOnly", "0", "0"),
        ("pauseState", "SFBool", "FALSE", "inputOutput", "0", "0"),
        ("colorMatchTolerance", "SFFloat", "0.01", "initializeOnly", "0", "0"),
        ("classified", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("eboxes", "MFVec4f", (), "inputOnly", "0", "0"),
        ("iboxes", "MFVec4f", (), "inputOnly", "0", "0"),
        ("_sinkmaps", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
    ), "X3DParticlePhysicsModelNode"),

    ###################################################################################

    #   41. Volume Rendering Component

    ###################################################################################
    # LEVEL 1

    ("OpacityMapVolumeStyle", "OpacityMapVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transferFunction", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DComposableVolumeRenderStyleNode"),

    ("VolumeData", "VolumeData", (
        ("dimensions", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("voxels", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_boxtris", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("renderStyle", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DVolumeDataNode"),

    # level 2
    # BoundaryEnhancementVolumeStyle    All fields fully supported.
    ("BoundaryEnhancementVolumeStyle", "BoundaryEnhancementVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("boundaryOpacity", "SFFloat", "0.9", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("opacityFactor", "SFFloat", "2", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("retainedOpacity", "SFFloat", "0.2", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceNormals", "SFNode", "NULL", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # ComposedVolumeStyle   ordered field is always treated as FALSE. All other fields fully supported.
    ("ComposedVolumeStyle", "ComposedVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("renderStyle", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # EdgeEnhancementVolumeStyle    All fields fully supported.
    ("EdgeEnhancementVolumeStyle", "EdgeEnhancementVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceNormals", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("edgeColor", "SFColorRGBA", ("0", "0", "0", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("gradientThreshold", "SFFloat", "0.4", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # IsoSurfaceVolumeData  All fields fully supported.
    ("IsoSurfaceVolumeData", "IsoSurfaceVolumeData", (
        ("dimensions", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("voxels", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_boxtris", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("renderStyle", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("contourStepSize", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("gradients", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceTolerance", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceValues", "MFFloat", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
    ), "X3DVolumeDataNode"),

    # see level1: OpacityMapVolumeStyle All fields fully supported. 3D transfer functions shall be supported.
    # ProjectionVolumeStyle All fields fully supported
    ("ProjectionVolumeStyle", "ProjectionVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensityThreshold", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("type", "SFString", "MAX", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_type", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # SegmentedVolumeData   All fields fully supported.
    ("SegmentedVolumeData", "SegmentedVolumeData", (
        ("dimensions", "SFVec3f", ("1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_LENGTH"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("voxels", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bboxCenter", "SFVec3f", ("0", "0", "0"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("bboxSize", "SFVec3f", ("-1", "-1", "-1"), "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_BLENGTH"),
        ("visible", "SFBool", "TRUE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("bboxDisplay", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("_boxtris", "FreeWRLPTR", "NULL", "initializeOnly", "0", "0"),
        ("renderStyle", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("segmentEnabled", "MFBool", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),  # see note top of file
        ("segmentIdentifiers", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DVolumeDataNode"),

    # SilhouetteEnhancementVolumeStyle  All fields fully supported.
    ("SilhouetteEnhancementVolumeStyle", "SilhouetteEnhancementVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceNormals", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("silhouetteBoundaryOpacity", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("silhouetteRetainedOpacity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("silhouetteSharpness", "SFFloat", "0.5", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # ToneMappedVolumeStyle All fields fully supported.
    ("ToneMappedVolumeStyle", "ToneMappedVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceNormals", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("coolColor", "SFColorRGBA", ("0", "0", "1", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("warmColor", "SFColorRGBA", ("1", "1", "0", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # level 3
    # BlendedVolumeStyle    All fields fully supported.
    ("BlendedVolumeStyle", "BlendedVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceNormals", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("renderStyle", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("voxels", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weightConstant1", "SFFloat", "0.5", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weightConstant2", "SFFloat", "0.5", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weightFunction1", "SFString", "CONSTANT", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weightFunction2", "SFString", "CONSTANT", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weightTransferFunction1", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("weightTransferFunction2", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_fbohandles", "MFInt32", ("0", "0", "0"), "initializeOnly", "0", "0"),
        ("_weightFunction1", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_weightFunction2", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # CartoonVolumeStyle    All fields fully supported.
    ("CartoonVolumeStyle", "CartoonVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceNormals", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("orthogonalColor", "SFColorRGBA", ("1", "1", "1", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("parallelColor", "SFColorRGBA", ("0", "0", "0", "1"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("colorSteps", "SFInt32", "4", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # CompositeVolumeStyle  All fields fully supported.
    ("CompositeVolumeStyle", "CompositeVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        # the other renderStyles are SF, this one MF
        ("renderStyle", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DComposableVolumeRenderStyleNode"),

    # ShadedVolumeStyle All fields fully supported except shadows. Shadows supported with at least Phong shading.
    # level 4
    # ShadedVolumeStyle All fields fully supported with at least Phong shading and  Henyey-Greenstein phase function. Shadows fully supported.
    ("ShadedVolumeStyle", "ShadedVolumeStyle", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("surfaceNormals", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("lighting", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("shadows", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("material", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("phaseFunction", "SFString", "Henyey-Greenstein", "initializeOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("_phaseFunction", "SFInt32", "0", "initializeOnly", "0", "0"),
    ), "X3DComposableVolumeRenderStyleNode"),

    ###################################################################################

    # Chapter 42:       Texture Projector Component (aka ProjectiveTextureMapping PTM)

    ###################################################################################

    ("TextureProjector", "TextureProjector", (
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("global", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("on", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("shadows", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("shadowIntensity", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("ambientIntensity", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("location", "SFVec3f", ("0", "0", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("direction", "SFVec3f", ("0", "0", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("nearDistance", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("farDistance", "SFFloat", "10", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("texture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("backCull", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),

        ("_dir", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("_loc", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("_upVec", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("upVector", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("aspectRatio", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("fieldOfView", "SFFloat", "45", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DTextureProjectorNode"),

    ("TextureProjectorParallel", "TextureProjectorParallel", (
        # same field order as TextureProjector, except fieldOfView last, which is different
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("global", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("on", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("shadows", "SFBool", "FALSE", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("shadowIntensity", "SFFloat", "1", "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
        ("ambientIntensity", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("location", "SFVec3f", ("0", "0", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("direction", "SFVec3f", ("0", "0", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("nearDistance", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("farDistance", "SFFloat", "10", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("texture", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("backCull", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),

        ("_dir", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("_loc", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("_upVec", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("upVector", "SFVec3f", ("0", "1", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("aspectRatio", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),
        ("fieldOfView", "SFVec4f", ("-1", "-1", "1", "1"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33 | SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DTextureProjectorNode"),

    ("TextureProjectorPoint", "TextureProjectorPoint", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("global", "SFBool", "FALSE", "inputOutput", "0", "UNCA_NONE"),
        ("on", "SFBool", "FALSE", "inputOutput", "0", "UNCA_NONE"),
        ("shadows", "SFBool", "FALSE", "inputOutput", "0", "UNCA_NONE"),
        ("shadowIntensity", "SFFloat", "1", "inputOutput", "0", "UNCA_NONE"),
        ("ambientIntensity", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("1", "1", "1"), "inputOutput", "(SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("intensity", "SFFloat", "1", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("location", "SFVec3f", ("0", "0", "1"), "inputOutput", "0", "UNCA_NONE"),
        ("direction", "SFVec3f", ("0", "0", "1"), "inputOutput", "0", "UNCA_NONE"),
        ("nearDistance", "SFFloat", "1", "inputOutput", "0", "UNCA_NONE"),
        ("farDistance", "SFFloat", "10", "inputOutput", "0", "UNCA_NONE"),
        ("texture", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("backCull", "SFBool", "TRUE", "inputOutput", "0", "UNCA_NONE"),

        ("_dir", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("_loc", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("_upVec", "SFVec4f", ("0", "0", "0", "0"), "initializeOnly", "0", "0"),
        ("upVector", "SFVec3f", ("0", "1", "0"), "inputOutput", "0", "UNCA_NONE"),
        # aspectRatio => ["SFFloat", 1, "inputOutput", 0,"UNCA_NONE"],#ff
        # fieldOfView => ["SFFloat", 45, "inputOutput", 0,"UNCA_NONE"],#ff

    ), "X3DTextureProjectorNode"),

    ###################################################################################

    #   43. MIDI Component (proposed July 2023)

    ###################################################################################

    ("MIDIFileSource", "MIDIFileSource", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("__loadstatus", "SFInt32", "0", "initializeOnly", "0", "0"),
        ("_parentResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__loadResource", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__blob", "MFInt32", "NULL", "initializeOnly", "0", "0"),

    ), "X3DMIDISourceNode"),

    ("MIDIPortSource", "MIDIPortSource", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("port", "SFInt32", "0", "inputOutput", "0", "UNCA_NONE"),

    ), "X3DMIDISourceNode"),

    ("MIDIFileDestination", "MIDIFileDestination", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("url", "MFString", (), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DMIDIDestinationNode"),

    ("MIDIPortDestination", "MIDIPortDestination", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("port", "SFInt32", "0", "inputOutput", "0", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DMIDIDestinationNode"),

    ("MIDIPrintDestination", "MIDIPortDestination", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DMIDIDestinationNode"),

    ("MIDIOut", "MIDIOut", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("midiMsg", "MFInt32", (), "outputOnly", "0", "0"),
        ("midiUmp", "MFDouble", (), "outputOnly", "0", "0"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),

    ), "X3DMIDIProcessingNode"),

    ("MIDIIn", "MIDIIn", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("midiMsg", "MFInt32", (), "inputOnly", "0", "0"),
        ("midiUmp", "MFDouble", (), "inputOnly", "0", "0"),

    ), "X3DMIDISourceNode"),

    ("MIDIProgram", "MIDIProgram", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("instrument", "SFInt32", "1", "inputOutput", "0", "0"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DMIDIProcessingNode"),

    ("MIDIDelay", "MIDIDelay", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("delay", "SFTime", "0", "inputOutput", "0", "0"),
        ("children", "MFNode", (), "inputOutput", "(SPEC_X3D40)", "UNCA_NONE"),
    ), "X3DMIDIProcessingNode"),

    ("MIDIConverterOut", "MIDIConverterOut", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("octave", "MFInt32", (), "outputOnly", "0", "0"),
        ("key12", "MFInt32", (), "outputOnly", "0", "0"),
        ("key88", "MFInt32", (), "outputOnly", "0", "0"),
        ("keyPiano", "MFInt32", (), "outputOnly", "0", "0"),
        ("pedal", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("midiMsg", "MFInt32", (), "inputOnly", "0", "0"),
        ("midiUmp", "MFDouble", (), "inputOnly", "0", "0"),

    ), "X3DMIDINode"),
    ("MIDIConverterIn", "MIDIConverterIn", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("octave", "MFInt32", (), "inputOnly", "0", "0"),
        ("key12", "MFInt32", (), "inputOnly", "0", "0"),
        ("key88", "MFInt32", (), "inputOnly", "0", "0"),
        ("keyPiano", "MFInt32", (), "inputOnly", "0", "0"),
        ("pedal", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("midiMsg", "MFInt32", (), "outputOnly", "0", "0"),
        ("midiUmp", "MFDouble", (), "outputOnly", "0", "0"),

    ), "X3DMIDINode"),

    ("MIDIToneSplitter", "MIDIToneSplitter", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("octaveFilter", "SFInt32", "-1", "inputOutput", "0", "0"),
        ("channelFilter", "SFInt32", "-1", "inputOutput", "0", "0"),
        ("midiMsg", "MFInt32", (), "inputOnly", "0", "0"),
        ("midiUmp", "MFDouble", (), "inputOnly", "0", "0"),

        ("C", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("Cs", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("D", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("Ds", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("E", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("F", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("Fs", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("G", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("Gs", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("A", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("As", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("B", "SFBool", "FALSE", "outputOnly", "0", "0"),
        ("pedal", "SFBool", "FALSE", "outputOnly", "0", "0"),
    ), "X3DMIDINode"),
    ("MIDIToneMerger", "MIDIToneMerger", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("octave", "SFInt32", "5", "inputOutput", "0", "0"),
        ("channel", "SFInt32", "1", "inputOutput", "0", "0"),
        ("midiMsg", "MFInt32", (), "outputOnly", "0", "0"),
        ("midiUmp", "MFDouble", (), "outputOnly", "0", "0"),

        ("C", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("Cs", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("D", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("Ds", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("E", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("F", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("Fs", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("G", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("Gs", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("A", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("As", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("B", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("pedal", "SFBool", "FALSE", "inputOnly", "0", "0"),
        ("_lastnote", "MFBool", (), "inputOnly", "0", "0"),

    ), "X3DMIDINode"),

    ("MIDIAudioSynth", "MIDIAudioSynth", (
        ("metadata", "SFNode", "NULL", "inputOutput", "0", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "0", "UNCA_NONE"),
        ("polyphony", "SFInt32", "10", "inputOutput", "0", "0"),

    ), "X3DSoundSourceNode"),

    ###################################################################################

    # Augmented Reality - not in specs, proposed:
    # http://www.web3d.org/wiki/index.php?title=AR_Proposal_Public_Review

    ###################################################################################

    ("BackdropBackground", "BackdropBackground", (
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transparency", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__texture", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__VBO", "SFInt32", "0", "initializeOnly", "0", "0"),  # Vertex Buffer Object, if required.
        ("url", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DBackgroundNode"),

    ("ImageBackdropBackground", "ImageBackdropBackground", (
        ("set_bind", "SFBool", "100", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("bindTime", "SFTime", "0", "outputOnly", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isBound", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("transparency", "SFFloat", "0", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("color", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("__texture", "SFInt32", "0", "inputOutput", "0", "0"),
        ("__VBO", "SFInt32", "0", "initializeOnly", "0", "0"),  # Vertex Buffer Object, if required.
        ("image", "SFImage", "0, 0, 0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DBackgroundNode"),

    ("CalibratedCameraSensor", "CalibratedCameraSensor", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("image", "SFImage", "0, 0, 0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("focalPoint", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fieldOfView", "SFFloat", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("fovMode", "SFString", "", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("aspectRatio", "SFFloat", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSensorNode"),

    ("TrackingSensor", "TrackingSensor", (
        ("enabled", "SFBool", "TRUE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("position", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("rotation", "SFRotation", ("0", "0", "1", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isActive", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isPositionAvailable", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("isRotationAvailable", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
    ), "X3DSensorNode"),

    # Metadata nodes ...

    ###################################################################################

    # used mainly for (pre-2014 era text-based PROTOs attached to Group nodes aka TROTO) PROTO invocation parameters
    # (2014+ era: switched to binary PROTOs (aka Brotos) with their own (not Group) node, which uses routing to go from
    #  BrotoInterface to BrotoBody nodes - don't need the following now, or the __protoDEF thing in Group,
    #   except to compile left-over code)
    ("MetadataSFFloat", "MetadataSFFloat", (
        ("value", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFFloat", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFFloat", "0", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFFloat", "MetadataMFFloat", (
        ("value", "MFFloat", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFFloat", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFFloat", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFRotation", "MetadataSFRotation", (
        ("value", "SFRotation", ("0", "0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("valueChanged", "SFRotation", ("0", "0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFRotation", ("0", "0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFRotation", "MetadataMFRotation", (
        ("value", "MFRotation", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_ANGLE"),
        ("valueChanged", "MFRotation", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFRotation", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFVec3f", "MetadataSFVec3f", (
        ("value", "SFVec3f", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFVec3f", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFVec3f", ("0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFVec3f", "MetadataMFVec3f", (
        ("value", "MFVec3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFVec3f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFVec3f", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFBool", "MetadataSFBool", (
        ("value", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFBool", "FALSE", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFBool", "FALSE", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFBool", "MetadataMFBool", (
        ("value", "MFBool", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFBool", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFBool", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFInt32", "MetadataSFInt32", (
        ("value", "SFInt32", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFInt32", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFInt32", "0", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFInt32", "MetadataMFInt32", (
        ("value", "MFInt32", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFInt32", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFInt32", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFNode", "MetadataSFNode", (
        ("value", "SFNode", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFNode", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFNode", "0", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFNode", "MetadataMFNode", (
        ("value", "MFNode", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFNode", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFNode", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFColor", "MetadataSFColor", (
        ("value", "SFColor", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFColor", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFColor", ("0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFColor", "MetadataMFColor", (
        ("value", "MFColor", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFColor", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFColor", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFColorRGBA", "MetadataSFColorRGBA", (
        ("value", "SFColorRGBA", ("0", "0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFColorRGBA", ("0", "0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFColorRGBA", ("0", "0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFColorRGBA", "MetadataMFColorRGBA", (
        ("value", "MFColorRGBA", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFColorRGBA", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFColorRGBA", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFTime", "MetadataSFTime", (
        ("value", "SFTime", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFTime", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFTime", "0", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFTime", "MetadataMFTime", (
        ("value", "MFTime", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFTime", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFTime", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFString", "MetadataSFString", (
        ("value", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFString", "", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFString", "", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFString", "MetadataMFString", (
        ("value", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFString", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFString", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFVec2f", "MetadataSFVec2f", (
        ("value", "SFVec2f", ("0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFVec2f", ("0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFVec2f", ("0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFVec2f", "MetadataMFVec2f", (
        ("value", "MFVec2f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFVec2f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFVec2f", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFImage", "MetadataSFImage", (
        ("value", "SFImage", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFImage", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFImage", ("0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFVec3d", "MetadataSFVec3d", (
        ("value", "SFVec3d", ("0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFVec3d", ("0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFVec3d", ("0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFVec3d", "MetadataMFVec3d", (
        ("value", "MFVec3d", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFVec3d", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFVec3d", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFDouble", "MetadataSFDouble", (
        ("value", "SFDouble", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFDouble", "0", "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFDouble", "0", "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFDouble", "MetadataMFDouble", (
        ("value", "MFDouble", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFDouble", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFDouble", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFMatrix3f", "MetadataSFMatrix3f", (
        ("value", "SFMatrix3f", ("0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFMatrix3f", ("0", "0", "0", "0", "0", "0", "0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFMatrix3f", ("0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFMatrix3f", "MetadataMFMatrix3f", (
        ("value", "MFMatrix3f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFMatrix3f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFMatrix3f", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFMatrix3d", "MetadataSFMatrix3d", (
        ("value", "SFMatrix3d", ("0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFMatrix3d", ("0", "0", "0", "0", "0", "0", "0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFMatrix3d", ("0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFMatrix3d", "MetadataMFMatrix3d", (
        ("value", "MFMatrix3d", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFMatrix3d", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFMatrix3d", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFMatrix4f", "MetadataSFMatrix4f", (
        ("value", "SFMatrix4f", ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFMatrix4f", ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFMatrix4f", ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFMatrix4f", "MetadataMFMatrix4f", (
        ("value", "MFMatrix4f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFMatrix4f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFMatrix4f", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFMatrix4d", "MetadataSFMatrix4d", (
        ("value", "SFMatrix4d", ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFMatrix4d", ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFMatrix4d", ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFMatrix4d", "MetadataMFMatrix4d", (
        ("value", "MFMatrix4d", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFMatrix4d", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFMatrix4d", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFVec2d", "MetadataSFVec2d", (
        ("value", "SFVec2d", ("0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFVec2d", ("0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFVec2d", ("0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFVec2d", "MetadataMFVec2d", (
        ("value", "MFVec2d", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFVec2d", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFVec2d", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFVec4f", "MetadataSFVec4f", (
        ("value", "SFVec4f", ("0", "0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFVec4f", ("0", "0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFVec4f", ("0", "0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFVec4f", "MetadataMFVec4f", (
        ("value", "MFVec4f", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFVec4f", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFVec4f", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataSFVec4d", "MetadataSFVec4d", (
        ("value", "SFVec4d", ("0", "0", "0", "0"), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "SFVec4d", ("0", "0", "0", "0"), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "SFVec4d", ("0", "0", "0", "0"), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    # used mainly for PROTO invocation parameters
    ("MetadataMFVec4d", "MetadataMFVec4d", (
        ("value", "MFVec4d", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("valueChanged", "MFVec4d", (), "outputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("setValue", "MFVec4d", (), "inputOnly", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("tickTime", "SFTime", "0", "inputOnly", "0", "0"),
    ), "X3DChildNode"),

    ###################################################################################

    # testing...

    ###################################################################################
    #
    # Experimental node: OSC_Sensor
    #
    # Theory:
    # You define one or more OSC_Sensor node in your VRML file,
    # and route 'gotEvent' to a JavaScript node which triggers
    # when incoming data is received. Vague plans for a OSC_transmitter.
    #
    # Caveat: Only UDP is supported because that seems to be a hole in liblo.
    # *It defines  lo_server_thread_new_with_proto but does not seem to implement it.*
    #
    # See sample WRL: freewrl/tests/18-OSC-1.wrl
    #
    # listenfor: typical OSC data spec, for example iii
    # filter: typical OSC filter, for example /alpha/beta/gamma
    #
    # handler: You can choose to write your own handler in src/lib/scenegraph/OSCcallbacks.c
    # Uses: You may choose to take 3 incoming delta values and turn it into a vector.
    #   You may want to examine the values and turn a stream of packets into a single gesture
    # 2 handlers are supplied to use 'as is' or to use as a template for your own code:
    # nullOSC_handler - just swallows the callback. This is invoked if handler is undefined (or "")
    # defaultOSC_handler - just puts the data into the FIFOs; invoked if handler is defined as "default"
    #
    # Incoming values are placed into a set of FIFOs. So, if the external agent sent 3 deltas values,
    # all 3 values are placed into the FIFO. So, the dummy values intVal, strVal and fltVal are there
    # merely so that the JavaScript has something to talk about. The actaul Javascript utility routines
    # have been modified to look at FIFOsize. If FIFOsize > 0, then instead of doing a memcpy the
    # utility routines retrieve a single value out of the respective FIFO
    #
    ("OSC_Sensor", "OSC_Sensor", (

        ("enabled", "SFBool", "FALSE", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("description", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("protocol", "SFString", "UDP", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("listenfor", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("port", "SFInt32", "7000", "inputOutput", "0", "0"),
        ("filter", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("handler", "SFString", "", "inputOutput", "(SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("talksTo", "MFString", (), "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("FIFOsize", "SFInt32", "64", "inputOutput", "0", "0"),
        ("int32Inp", "SFInt32", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("floatInp", "SFFloat", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("stringInp", "SFString", "", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),
        ("gotEvents", "SFInt32", "0", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("metadata", "SFNode", "NULL", "inputOutput", "(SPEC_VRML | SPEC_X3D30 | SPEC_X3D31 | SPEC_X3D32 | SPEC_X3D33)", "UNCA_NONE"),

        ("_talkToNodes", "MFNode", (), "inputOutput", "0", "0"),
        ("_status", "SFInt32", "-1", "inputOutput", "0", "0"),
        ("_int32InpFIFO", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_floatInpFIFO", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_stringInpFIFO", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_int32OutFIFO", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_floatOutFIFO", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("_stringOutFIFO", "FreeWRLPTR", "0", "initializeOnly", "0", "0"),
        ("__oldmetadata", "SFNode", "0", "inputOutput", "0", "0"),  # see code for event macro

    ), "X3DNetworkSensorNode"),
)

FIELD_KINDS = ("initializeOnly", "inputOnly", "outputOnly", "inputOutput")

_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Defaults go into C source without escaping.
_TEXT_RE = re.compile(r"[ !#-\[\]-~]*")


class NodeDataError(ValueError):
    """Node data that the generator must not use."""


class Field(NamedTuple):
    name: str
    type: str
    default: object
    kind: str
    spec: str
    unca: str


class Node(NamedTuple):
    name: str
    x3d_type: str
    fields: tuple


def _check_default(where, value, depth=0):
    if value is None and depth == 0:
        return
    if isinstance(value, str):
        if not _TEXT_RE.fullmatch(value):
            raise NodeDataError(f"{where}: unsafe default text {value!r}")
        return
    if isinstance(value, tuple) and depth < 2:
        for item in value:
            _check_default(where, item, depth + 1)
        return
    raise NodeDataError(f"{where}: bad default {value!r}")


def _make_node(key, x3d_type, fields):
    if not _NAME_RE.fullmatch(key):
        raise NodeDataError(f"bad node name {key!r}")
    if not isinstance(x3d_type, str) or not x3d_type:
        raise NodeDataError(f"{key}: X3D node type is empty")
    seen = set()
    rows = []
    for row in fields:
        if len(row) != 6:
            raise NodeDataError(f"{key}: field row needs 6 values: {row!r}")
        field = Field(*row)
        where = f"{key}.{field.name}"
        if not isinstance(field.name, str) or not _NAME_RE.fullmatch(field.name):
            raise NodeDataError(f"{key}: bad field name {field.name!r}")
        if field.name in seen:
            raise NodeDataError(f"{where}: duplicate field")
        seen.add(field.name)
        if field.type not in FIELD_TYPES:
            raise NodeDataError(f"{where}: unknown field type {field.type!r}")
        if field.kind not in FIELD_KINDS:
            raise NodeDataError(f"{where}: bad field kind {field.kind!r}")
        for label, value in (("spec", field.spec), ("unca", field.unca)):
            if not isinstance(value, str) or not value or not _TEXT_RE.fullmatch(value):
                raise NodeDataError(f"{where}: missing or bad {label} {value!r}")
        _check_default(where, field.default)
        rows.append(field)
    return Node(key, x3d_type, tuple(rows))


def load_nodes(source=NODE_SOURCE):
    """Return {key: Node} with the Perl hash result: the last entry wins."""
    nodes = {}
    for entry in source:
        if len(entry) != 4:
            raise NodeDataError(f"node entry needs 4 values: {entry[:2]!r}")
        key, _name, fields, x3d_type = entry
        nodes[key] = _make_node(key, x3d_type, fields)
    return nodes


NODES = load_nodes()
