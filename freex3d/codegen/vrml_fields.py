"""Field type data for vrmlc.py.

This is the Python form of VRMLFields.pm. It holds the field type order,
the C type names, the C structs and the default-value initializers.

The output must stay byte-identical to the Perl output. The initializers
keep every quirk of VRMLFields.pm, for example missing semicolons and
missing newlines. Do not fix them here. Fix them in a separate change
that also updates the generated files.

A default value is the text that Perl makes from the VRMLNodes.pm value:
a str, None (Perl undef), or a tuple of such values. Python never formats
a number here.
"""

# Order sets the FIELDTYPE_* numbers. It must match the PARSE_TYPE table.
FIELD_TYPES = (
    "SFFloat",
    "MFFloat",
    "SFBool",
    "MFBool",
    "SFInt32",
    "MFInt32",
    "SFTime",
    "MFTime",
    "SFDouble",
    "MFDouble",
    "SFNode",
    "MFNode",
    "SFColor",
    "MFColor",
    "SFColorRGBA",
    "MFColorRGBA",
    "SFRotation",
    "MFRotation",
    "SFVec2f",
    "MFVec2f",
    "SFVec3f",
    "MFVec3f",
    "SFVec4f",
    "MFVec4f",
    "SFVec2d",
    "MFVec2d",
    "SFVec3d",
    "MFVec3d",
    "SFVec4d",
    "MFVec4d",
    "SFString",
    "MFString",
    "SFImage",
    "MFImage",
    "SFMatrix3f",
    "MFMatrix3f",
    "SFMatrix4f",
    "MFMatrix4f",
    "SFMatrix3d",
    "MFMatrix3d",
    "SFMatrix4d",
    "MFMatrix4d",
    "FreeWRLPTR",
    "FreeWRLThread",
)

# C struct types of the fixed-size SF types: (C element type, length).
SF_ARRAY_TYPES = {
    "SFColor": ("float", 3),
    "SFColorRGBA": ("float", 4),
    "SFRotation": ("float", 4),
    "SFVec2f": ("float", 2),
    "SFVec3f": ("float", 3),
    "SFVec4f": ("float", 4),
    "SFVec2d": ("double", 2),
    "SFVec3d": ("double", 3),
    "SFVec4d": ("double", 4),
    "SFMatrix3f": ("float", 9),
    "SFMatrix4f": ("float", 16),
    "SFMatrix3d": ("double", 9),
    "SFMatrix4d": ("double", 16),
}

# Struct member type text of the types that are not "struct <type> ".
C_TYPE_PREFIX = {
    "SFFloat": "float ",
    "SFBool": "int ",
    "SFInt32": "int ",
    "SFTime": "double ",
    "SFDouble": "double ",
    "SFNode": "struct X3D_Node *",
    "SFString": "struct Uni_String *",
    "SFImage": "struct SFImage ",
    "FreeWRLPTR": "void * ",
    "FreeWRLThread": "pthread_t ",
}

# One line of Structs.h for each field type, in FIELD_TYPES order.
C_STRUCT = {
    "SFFloat": "/*cstruct*/",
    "MFFloat": "struct Multi_Float { int n; float  *p; };",
    "SFBool": "/*cstruct*/",
    "MFBool": "struct Multi_Bool { int n; int  *p; };",
    "SFInt32": "/*cstruct*/",
    "MFInt32": "struct Multi_Int32 { int n; int  *p; };",
    "SFTime": "/*cstruct*/",
    "MFTime": "struct Multi_Time { int n; double  *p; };",
    "SFDouble": "/*cstruct*/",
    "MFDouble": "struct Multi_Double { int n; double  *p; };",
    "SFNode": "",
    "MFNode": "struct Multi_Node { int n; struct X3D_Node * *p; };",
    "SFColor": "struct SFColor { float c[3]; };",
    "MFColor": "struct Multi_Color { int n; struct SFColor  *p; };",
    "SFColorRGBA": "struct SFColorRGBA { float c[4]; };",
    "MFColorRGBA": "struct Multi_ColorRGBA { int n; struct SFColorRGBA  *p; };",
    "SFRotation": "struct SFRotation { float c[4]; };",
    "MFRotation": "struct Multi_Rotation { int n; struct SFRotation  *p; };",
    "SFVec2f": "struct SFVec2f { float c[2]; };",
    "MFVec2f": "struct Multi_Vec2f { int n; struct SFVec2f  *p; };",
    "SFVec3f": "struct SFVec3f { float c[3]; };",
    "MFVec3f": "struct Multi_Vec3f { int n; struct SFVec3f  *p; };",
    "SFVec4f": "struct SFVec4f { float c[4]; };",
    "MFVec4f": "struct Multi_Vec4f { int n; struct SFVec4f  *p; };",
    "SFVec2d": "struct SFVec2d { double c[2]; };",
    "MFVec2d": "struct Multi_Vec2d { int n; struct SFVec2d  *p; };",
    "SFVec3d": "struct SFVec3d { double c[3]; };",
    "MFVec3d": "struct Multi_Vec3d { int n; struct SFVec3d  *p; };",
    "SFVec4d": "struct SFVec4d { double c[4]; };",
    "MFVec4d": "struct Multi_Vec4d { int n; struct SFVec4d  *p; };",
    "SFString": "/*cstruct*/",
    "MFString": "struct Multi_String { int n; struct Uni_String * *p; };",
    "SFImage": "struct SFImage { int whc[3]; struct Multi_Int32 arr; };",
    "MFImage": "struct Multi_Image { int n; struct SFImage  *p; };",
    "SFMatrix3f": "struct SFMatrix3f { float c[9]; };",
    "MFMatrix3f": "struct Multi_Matrix3f { int n; struct SFMatrix3f  *p; };",
    "SFMatrix4f": "struct SFMatrix4f { float c[16]; };",
    "MFMatrix4f": "struct Multi_Matrix4f { int n; struct SFMatrix4f  *p; };",
    "SFMatrix3d": "struct SFMatrix3d { double c[9]; };",
    "MFMatrix3d": "struct Multi_Matrix3d { int n; struct SFMatrix3d  *p; };",
    "SFMatrix4d": "struct SFMatrix4d { double c[16]; };",
    "MFMatrix4d": "struct Multi_Matrix4d { int n; struct SFMatrix4d  *p; };",
    "FreeWRLPTR": "/*cstruct*/",
    "FreeWRLThread": "/*cstruct*/",
}


class FieldDataError(ValueError):
    """A default value that VRMLFields.pm cannot turn into C."""


def ctype(ftype, name):
    """Return the struct member declaration of one field, without ';'."""
    if ftype in C_TYPE_PREFIX:
        return C_TYPE_PREFIX[ftype] + name
    if ftype.startswith("MF"):
        return f"struct Multi_{ftype[2:]} " + name
    if ftype in SF_ARRAY_TYPES:
        return f"struct {ftype} " + name
    raise FieldDataError(f"unknown field type {ftype}")


def _float_text(value):
    # VRMLFields.pm: add ".0f" when the Perl text has no ".", else add "f".
    return value + (".0f" if "." not in value else "f")


def _scalar(field, value):
    # An undef list element: Perl writes undef as "". Each caller handles
    # an undef default before it gets here.
    if value is None:
        return ""
    if not isinstance(value, str):
        raise FieldDataError(f"{field}: expected a single value, got {value!r}")
    return value


def _list(field, value):
    # Perl dereferences these with @{$val} under "use strict", so a value
    # that is not a list stops Perl.
    if not isinstance(value, tuple):
        raise FieldDataError(f"{field}: expected a list, got {value!r}")
    return value


def _list_or_empty(value):
    # Perl: "ref $val eq ARRAY ? @{$val} : 0". A scalar or undef is empty.
    return value if isinstance(value, tuple) else ()


def _items(field, value, length):
    # Perl reads "@{$val}[i]" for i < length. Perl reads undef as an empty
    # list, and an index past the end gives undef, which Perl writes as "".
    # A scalar value stops Perl (strict refs).
    values = () if value is None else _list(field, value)
    return tuple(_scalar(field, values[i]) if i < len(values) else "" for i in range(length))


def _sf_array(field, value, length, suffix, last_semicolon=True):
    values = _items(field, value, length)
    out = ""
    for i in range(length):
        text = values[i]
        out += f"{field}.c[{i}] = {_float_text(text) if suffix else text};"
    # SFVec3f: Perl leaves out the last ';'.
    return out if last_semicolon else out[:-1]


def _mf_scalar(field, values, ctype_name, suffix):
    if not values:
        return f"{field}.n=0; {field}.p=0"
    out = f"{field}.p = MALLOC ({ctype_name} *, sizeof({ctype_name})*{len(values)});\n"
    for i, value in enumerate(values):
        text = _scalar(field, value)
        out += f"\t\t\t{field}.p[{i}] = {_float_text(text) if suffix else text};\n"
    return out + f"\t\t\t{field}.n={len(values)};"


def _mf_struct(field, values, struct, width, suffix, alloc_newline=True, last_semicolon=True):
    if not values:
        return f"{field}.n=0; {field}.p=0"
    out = f"{field}.p = MALLOC (struct {struct} *, sizeof(struct {struct})*{len(values)});"
    if alloc_newline:
        out += "\n"
    for i, item in enumerate(values):
        row = _items(field, item, width)
        for w in range(width):
            text = row[w]
            out += f"\n\t\t\t{field}.p[{i}].c[{w}] = {_float_text(text) if suffix else text}; "
    out += f"\n\t\t\t{field}.n={len(values)}"
    return out + (";" if last_semicolon else "")


def _init_sffloat(field, value):
    return f"{field} = " + _float_text("0.0" if value is None else _scalar(field, value))


def _init_sf_plain(field, value):
    # SFBool, SFInt32, SFTime and SFDouble. Perl prints undef 0 and 0.0 as "0".
    return f"{field} = " + ("0" if value is None else _scalar(field, value))


def _note(text):
    # VRMLFields.pm prints these notes to stdout and continues.
    print(text)


def _init_sfnode(field, value):
    if value is None:
        # Perl prints a note and writes "<field> = " (broken C). Keep it.
        _note("undefined in SFNode")
        return f"{field} = "
    return f"{field} = " + _scalar(field, value)


def _init_sfstring(field, value):
    text = "" if value is None else _scalar(field, value)
    return f'{field} = newASCIIString("{text}")'


def _init_sfvec2f(field, value):
    if value is None:
        return f"{field}.c[0] = 0; {field}.c[1] = 1;"
    return _sf_array(field, value, 2, True)


def _init_sfimage(field, value):
    if value is None:
        _note("undefined in SFImage")
    values = _list_or_empty(value)
    if not values:
        return (f"{field}.arr.n=0; {field}.arr.p=NULL; "
                f"{field}.whc[0] = 0; {field}.whc[1] = 0; {field}.whc[2] = 0;")
    count = len(values)
    out = f"{field}.arr.p = MALLOC (int *, sizeof(int)*{count}-3);"
    for i in range(3):
        out += f"{field}.whc[{i}] = {_scalar(field, values[i]) if i < count else ''};"
    for i in range(3, count):
        out += f"{field}.arr[{i}-3] = {_scalar(field, values[i])};"
    return out + f"{field}.arr.n={count} -3; "


def _init_freewrlptr(field, value):
    if field == "tmp2->_parentResource":
        return f"{field} = getInputResource()"
    return f"{field} = " + ("0" if value is None else _scalar(field, value))


def _init_freewrlthread(field, value):
    return f"{field} = _THREAD_NULL_"


def _init_mfbool(field, value):
    values = _list(field, value)
    if not values:
        return f"{field}.n=0; {field}.p=0"
    out = f"{field}.p = MALLOC (int *, sizeof(int)*{len(values)});\n"
    for i, item in enumerate(values):
        out += f"\n\t\t\t{field}.p[{i}] = {_scalar(field, item)}; "
    return out + f"{field}.n={len(values)};"


def _init_mf_empty_only(field, values, label):
    # MFTime and MFNode: for a non-empty default, Perl prints
    # "<label> HAVE TO MALLOC HERE" and the sub returns the value of
    # print, which is 1. So Perl writes "1" (broken C). Keep it.
    if values:
        _note(f"{label} HAVE TO MALLOC HERE")
        return "1"
    return f"{field}.n=0; {field}.p=0"


def _init_mfstring(field, value):
    values = _list(field, value)
    if not values:
        return f"{field}.n=0; {field}.p=0"
    out = f"{field}.p = MALLOC (struct Uni_String **, sizeof(struct Uni_String)*{len(values)});"
    for i, item in enumerate(values):
        out += f'{field}.p[{i}] = newASCIIString("{_scalar(field, item)}");'
    return out + f"{field}.n={len(values)}; "


def _init_mfimage(field, value):
    values = _list(field, value)
    if not values:
        # Perl writes n=3 here.
        return f"{field}.n=3; {field}.p=0"
    out = f"{field}.p = MALLOC (struct SFImage *, sizeof(struct SFImage)*{len(values)});"
    for i, item in enumerate(values):
        out += f"{field}.p[{i}] = {_scalar(field, item)};"
    return out + f"{field}.n={len(values)}; "


def _sf_array_init(ftype, suffix, last_semicolon=True):
    length = SF_ARRAY_TYPES[ftype][1]
    # Perl prints this note for undef and continues. The SFMatrix types
    # print "SFColor". Keep it.
    note = "undefined in " + ("SFColor" if ftype.startswith("SFMatrix") else ftype)

    def init(field, value):
        if value is None:
            _note(note)
        return _sf_array(field, value, length, suffix, last_semicolon)
    return init


def _mf_struct_init(struct, suffix, guarded, alloc_newline=True, last_semicolon=True):
    width = SF_ARRAY_TYPES[struct][1]

    def init(field, value):
        values = _list_or_empty(value) if guarded else _list(field, value)
        return _mf_struct(field, values, struct, width, suffix, alloc_newline, last_semicolon)
    return init


# "guarded" types use "ref $val eq ARRAY" in Perl, so a scalar or undef
# default gives an empty list. The other MF types need a list.
C_INITIALIZE = {
    "SFFloat": _init_sffloat,
    "MFFloat": lambda f, v: _mf_scalar(f, _list_or_empty(v), "float", True),
    "SFBool": _init_sf_plain,
    "MFBool": _init_mfbool,
    "SFInt32": _init_sf_plain,
    "MFInt32": lambda f, v: _mf_scalar(f, _list_or_empty(v), "int", False),
    "SFTime": _init_sf_plain,
    "MFTime": lambda f, v: _init_mf_empty_only(f, _list(f, v), "MFTIME"),
    "SFDouble": _init_sf_plain,
    "MFDouble": lambda f, v: _mf_scalar(f, _list_or_empty(v), "double", False),
    "SFNode": _init_sfnode,
    "MFNode": lambda f, v: _init_mf_empty_only(f, _list_or_empty(v), "MFNODE"),
    "SFColor": _sf_array_init("SFColor", True),
    "MFColor": _mf_struct_init("SFColor", True, False),
    "SFColorRGBA": _sf_array_init("SFColorRGBA", False),
    "MFColorRGBA": _mf_struct_init("SFColorRGBA", True, False),
    "SFRotation": _sf_array_init("SFRotation", False),
    "MFRotation": _mf_struct_init("SFRotation", True, True),
    "SFVec2f": _init_sfvec2f,
    "MFVec2f": _mf_struct_init("SFVec2f", True, True, alloc_newline=False, last_semicolon=False),
    "SFVec3f": _sf_array_init("SFVec3f", True, last_semicolon=False),
    "MFVec3f": _mf_struct_init("SFVec3f", True, True),
    "SFVec4f": _sf_array_init("SFVec4f", False),
    "MFVec4f": _mf_struct_init("SFVec4f", False, False),
    "SFVec2d": _sf_array_init("SFVec2d", False),
    "MFVec2d": _mf_struct_init("SFVec2d", False, False, alloc_newline=False, last_semicolon=False),
    "SFVec3d": _sf_array_init("SFVec3d", False),
    "MFVec3d": _mf_struct_init("SFVec3d", False, True),
    "SFVec4d": _sf_array_init("SFVec4d", False),
    "MFVec4d": _mf_struct_init("SFVec4d", False, False),
    "SFString": _init_sfstring,
    "MFString": _init_mfstring,
    "SFImage": _init_sfimage,
    "MFImage": _init_mfimage,
    "SFMatrix3f": _sf_array_init("SFMatrix3f", False),
    "MFMatrix3f": _mf_struct_init("SFMatrix3f", True, False),
    "SFMatrix4f": _sf_array_init("SFMatrix4f", False),
    "MFMatrix4f": _mf_struct_init("SFMatrix4f", True, False),
    "SFMatrix3d": _sf_array_init("SFMatrix3d", False),
    # Perl allocates MFMatrix3d with struct SFMatrix3f. Keep it.
    "MFMatrix3d": _mf_struct_init("SFMatrix3f", False, False),
    "SFMatrix4d": _sf_array_init("SFMatrix4d", False),
    "MFMatrix4d": _mf_struct_init("SFMatrix4d", False, False),
    "FreeWRLPTR": _init_freewrlptr,
    "FreeWRLThread": _init_freewrlthread,
}


def cinitialize(ftype, field, value):
    """Return the C statement (without ';') that sets one default."""
    return C_INITIALIZE[ftype](field, value)


def _check_tables():
    names = set(FIELD_TYPES)
    if len(names) != len(FIELD_TYPES):
        raise FieldDataError("FIELD_TYPES has a duplicate entry")
    for table in (C_STRUCT, C_INITIALIZE):
        if set(table) != names:
            raise FieldDataError("field tables do not match FIELD_TYPES")


_check_tables()
