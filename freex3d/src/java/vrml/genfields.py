#!/usr/bin/env python3
# Copyright (C) 2002 Jochen Hoenicke
# DISTRIBUTED WITH NO WARRANTY, EXPRESS OR IMPLIED.
# See the GNU Library General Public License (file COPYING in the distribution)
# for conditions of use and redistribution.
"""Generate the vrml.field SF*, ConstSF*, MF* and ConstMF* Java classes.

Run from this directory. Writes field/<Class>.java.

The output must stay byte-identical to the committed generator output, so
the Java fragments below keep their original tabs and spacing. The file
header still names genfields.pl for the same reason.
"""

import re
import sys
from string import Template

if sys.version_info < (3, 12):
    sys.exit("genfields.py: Python 3.12 or later is required.")


def lines(*parts):
    return "\n".join(parts)


# Field type -> comma-separated "<java type> <member name>" list.
FIELD_TYPES = {
    "Bool": "boolean value",
    "Color": "float red,float green,float blue",
    "Float": "float f",
    "Image": "int width,int height,int components,byte[] pixels",
    "Int32": "int value",
    "Node": "BaseNode node",
    "Rotation": "float axisX,float axisY,float axisZ,float angle",
    "String": "String s",
    "Time": "double value",
    "Vec2f": "float x,float y",
    "Vec3f": "float x,float y,float z",
}

TO_STRING = {
    "Bool": 'return value ? "TRUE" : "FALSE";',
    "Color": 'return ""+red+" "+green+" "+blue;',
    "Float": "return String.valueOf(f);",
    "Image": lines(
        "StringBuffer sb = new StringBuffer();",
        "        sb.append(width).append(' ').append(height).append(' ').append(components);",
        "        for (int i = 0; i < pixels.length; i+=components) {",
        '\t    sb.append(" 0x");',
        "\t    for (int j = i; j < i+components; j++)",
        '\t\tsb.append("0123456789ABCDEF".charAt((pixels[j] & 0xf0) >> 4))',
        '\t\t    .append("0123456789ABCDEF".charAt(pixels[j] & 0x0f));',
        "\t}",
        "        return sb.toString();",
    ),
    "Int32": "return String.valueOf(value);",
    "Node": "return FWHelper.nodeToString(node);",
    "Rotation": 'return ""+axisX+" "+axisY+" "+axisZ+" "+angle;',
    "String": "return vrml.FWHelper.quote(s);",
    "Time": "return String.valueOf(value);",
    "Vec2f": 'return ""+x+" "+y;',
    "Vec3f": 'return ""+x+" "+y+" "+z;',
}

TO_PERL = {
    "Bool": "out.print (value);",
    "Color": 'out.print(red+ " "+green+" "+blue);',
    "Float": "out.print(f);",
    "Image": lines(
        "StringBuffer sb = new StringBuffer();",
        "        sb.append(width).append(' ').append(height).append(' ').append(components);",
        "        if (pixels == null) {",
        '            sb.append(" null");',
        "        } else {",
        "            for (int i = 0; i < pixels.length; i+=components) {",
        '\t\tsb.append(" 0x");',
        "\t\tfor (int j = i; j < i+components; j++)",
        '\t\t    sb.append("0123456789ABCDEF".charAt((pixels[j] & 0xf0) >> 4))',
        '\t\t\t.append("0123456789ABCDEF".charAt(pixels[j] & 0x0f));',
        "\t    }",
        "        }",
        "        out.print(sb.toString());",
    ),
    "Int32": "out.print(value);",
    "Node": "out.print(node._get_nodeid());",
    "Rotation": 'out.print(axisX+" "+axisY+" "+axisZ+" "+angle);',
    "String": "out.print(s);",
    "Time": "out.print(value);",
    "Vec2f": 'out.print(x + " " + y);',
    "Vec3f": 'out.print(x + " " + y + " " + z);',
}

FROM_PERL = {
    "Bool": lines(
        "",
        "\t\t\tString myline;",
        '\t\t//System.out.println ("fromPerl, Bool");',
        "\t\t\tmyline = in.readLine();",
        "\t\t\t// direct from perl, will be 0 or 1, from a route, TRUE, FALSE",
        '\t\t\tvalue = (myline.equals("TRUE") || myline.equals("1"));',
        '\t\t\t//System.out.println ("reading in a boolean value is " + value',
        '\t\t          //      + " for string " + myline);',
        "\t\t",
    ),
    "Color": lines(
        "",
        '\t//System.out.println ("fromPerl, Color");',
        "\t\tred = Float.parseFloat(in.readLine());",
        "        \tgreen = Float.parseFloat(in.readLine());",
        "        \tblue = Float.parseFloat(in.readLine());",
    ),
    "Float": lines(
        "",
        '\t//System.out.println ("fromPerl, Float");',
        "\t\tf = Float.parseFloat(in.readLine());",
    ),
    "Image": lines(
        "",
        '\t//System.out.println ("fromPerl, Image");',
        "\t\twidth = Integer.parseInt(in.readLine());",
        "        \theight = Integer.parseInt(in.readLine());",
        "        \tcomponents = Integer.parseInt(in.readLine());",
        "        \tpixels = new byte[height*width*components];",
        '\t//System.out.println ("JavaClass -- fix method to read in pixels");',
        "        \t// pixels = String.getBytes(pst);",
        "\t\t",
    ),
    "Int32": lines(
        "",
        '\t//System.out.println ("fromPerl, Int32");',
        "\t\tvalue = Integer.parseInt(in.readLine());",
    ),
    "Node": lines(
        "",
        '\t//System.out.println ("fromPerl, Node");',
        "\t\tnode = new vrml.node.Node(in.readLine());",
    ),
    "Rotation": lines(
        "",
        '\t//System.out.println ("fromPerl, Rotation");',
        "\t\taxisX = Float.parseFloat(in.readLine());",
        "\t        axisY = Float.parseFloat(in.readLine());",
        "        \taxisZ = Float.parseFloat(in.readLine());",
        "        \tangle = Float.parseFloat(in.readLine());",
    ),
    "String": lines(
        "",
        '\t//System.out.println ("fromPerl, String");',
        "\t\ts = in.readLine();",
    ),
    "Time": lines(
        "",
        '\t//System.out.println ("fromPerl, Time");',
        "\t\tvalue = Double.parseDouble(in.readLine());",
    ),
    "Vec2f": lines(
        "",
        '\t//System.out.println ("fromPerl, Vec2f");',
        "\t\tx = Float.parseFloat(in.readLine());",
        "        \ty = Float.parseFloat(in.readLine());",
    ),
    "Vec3f": lines(
        "",
        '\t//System.out.println ("fromPerl, Vec3f");',
        "\t\tx = Float.parseFloat(in.readLine());",
        "\t        y = Float.parseFloat(in.readLine());",
        "        \tz = Float.parseFloat(in.readLine());",
    ),
}

# Types with a getValue(T[])/setValue(T[]) array accessor.
MULTIVAL = re.compile("Color|Vec.f|Rotation")
# Types with one named getter per member, e.g. getRed().
MULTINAME = re.compile("Color|Vec.f|Image")

# There are no MF classes for these types.
NO_MF = re.compile("Bool|Image")

MEMBER_SEP = "\n        "


def emit(out, template, **values):
    out.write(Template(template).substitute(values))


def member_names(values):
    return [value.split()[1] for value in values]


### SF classes ###########################################################

def sf_constructor(out, cls, values):
    for value in values:
        out.write(f"     {value};\n")
    emit(out, """
    public $cls() { }

    public $cls($params) {
\t        $init
    }
""",
         cls=cls,
         params=", ".join(values),
         init=MEMBER_SEP.join(f"this.{n} = {n};" for n in member_names(values)))


def sf_getvalue(out, ft, values):
    if len(values) == 1:
        valtype, name = values[0].split()
        emit(out, """
    public $valtype getValue() {
        __updateRead();
        return $name;
    }
""", valtype=valtype, name=name)
        return

    if MULTIVAL.search(ft):
        body = MEMBER_SEP.join(
            f"values[{i}] = {n};" for i, n in enumerate(member_names(values)))
        emit(out, """
    public void getValue(${valtype}[] values) {
        __updateRead();
        $body
    }
""", valtype=values[0].split()[0], body=body)

    if MULTINAME.search(ft):
        for value in values:
            valtype, name = value.split()
            emit(out, """
    public $valtype get$upcase() {
        __updateRead();
        return $name;
    }
""", valtype=valtype, name=name, upcase=name[:1].upper() + name[1:])


def sf_setvalue(out, ft, values):
    names = member_names(values)
    emit(out, """
    public void setValue($params) {
        $body
        __updateWrite();
    }

""",
         params=", ".join(values),
         body=MEMBER_SEP.join(f"this.{n} = {n};" for n in names))

    if MULTIVAL.search(ft):
        emit(out, """
    public void setValue(${valtype}[] values) {
        $body
        __updateWrite();
    }
""",
             valtype=values[0].split()[0],
             body=MEMBER_SEP.join(
                 f"this.{n} = values[{i}];" for i, n in enumerate(names)))

    emit(out, """
    public void setValue(ConstSF$ft sf$ft) {
        sf$ft.__updateRead();
        $body
        __updateWrite();
    }

    public void setValue(SF$ft sf$ft) {
        sf$ft.__updateRead();
        $body
        __updateWrite();
    }

""", ft=ft, body=MEMBER_SEP.join(f"{n} = sf{ft}.{n};" for n in names))


def sf_stringfuncs(out, ft):
    emit(out, """
    public String toString() {
        __updateRead();
        $to_string
    }

    public void __fromPerl(BufferedReader in)  throws IOException {
        $from_perl
    }

    public void __toPerl(PrintWriter out)  throws IOException {
        $to_perl
\t//out.println();
    }
    //public void setOffset(String offs) { this.offset = offs; } //JAS2
    //public String getOffset() { return this.offset; } //JAS2
""", to_string=TO_STRING[ft], from_perl=FROM_PERL[ft], to_perl=TO_PERL[ft])


### MF classes ###########################################################

def mf_typename(ft, values):
    """Return the Java element type and the array parameter name."""
    valtype, valname = values[0].split()
    if len(values) > 1:
        valname = ft.lower() + "s"
    return valtype, valname


def mf_increment(numval):
    return "i++" if numval == 1 else f"i += {numval}"


def mf_flat_args(valname, numval):
    return ", ".join(f"{valname}[i{f'+{k}' if k else ''}]" for k in range(numval))


def mf_constructor(out, cls, ft, values):
    numval = len(values)
    valtype, valname = mf_typename(ft, values)
    fields = dict(cls=cls, ft=ft, valtype=valtype, valname=valname)

    emit(out, """    public $cls() {
    }

    public $cls(${valtype}[] $valname) {
        this($valname.length, $valname);
    }

    public $cls(int size, ${valtype}[] $valname) {
        for (int i = 0; i < size; $incr)
            __vect.addElement(new ConstSF$ft($args));
    }
""", **fields, incr=mf_increment(numval), args=mf_flat_args(valname, numval))

    if numval > 1:
        args = ", ".join(f"{valname}[i][{k}]" for k in range(numval))
        emit(out, """
    public $cls(${valtype}[][] $valname) {
        for (int i = 0; i < $valname.length; i++)
            __vect.addElement(new ConstSF$ft($args));
    }
""", **fields, args=args)


def mf_getvalue(out, ft, values):
    numval = len(values)
    valtype, valname = mf_typename(ft, values)
    fields = dict(ft=ft, valtype=valtype, valname=valname)

    forbody = f"ConstSF{ft} sf{ft} = (ConstSF{ft}) __vect.elementAt(i);"
    for i, name in enumerate(member_names(values)):
        index = "i" if numval == 1 else f"{numval}*i+{i}"
        forbody += f"\n            {valname}[{index}] = sf{ft}.{name};"

    emit(out, """
    public void getValue(${valtype}[] $valname) {
        __updateRead();
        int size = __vect.size();
        for (int i = 0; i < size; i++) {
            $forbody
        }
    }
""", **fields, forbody=forbody)

    if numval > 1:
        emit(out, """
    public void getValue(${valtype}[][] $valname) {
        __updateRead();
        int size = __vect.size();
        for (int i = 0; i < size; i++)
            ((ConstSF$ft) __vect.elementAt(i)).getValue(${valname}[i]);
    }
""", **fields)

    if numval == 1:
        emit(out, """
    public $valtype get1Value(int index) {
        __update1Read(index);
        return ((ConstSF$ft) __vect.elementAt(index)).getValue();
    }
""", **fields)
    else:
        emit(out, """
    public void get1Value(int index, ${valtype}[] $valname) {
        __update1Read(index);
        ((ConstSF$ft) __vect.elementAt(index)).getValue($valname);
    }

    public void get1Value(int index, SF$ft sf$ft) {
        __update1Read(index);
        sf$ft.setValue((ConstSF$ft) __vect.elementAt(index));
    }
""", **fields)


def mf_setvalue(out, ft, values):
    numval = len(values)
    valtype, valname = mf_typename(ft, values)
    names = member_names(values)

    emit(out, """
    public void setValue(${valtype}[] $valname) {
        setValue($valname.length, $valname);
    }

    public void setValue(int size, ${valtype}[] $valname) {
        __vect.clear();
        for (int i = 0; i < size; $incr)
            __vect.addElement(new ConstSF$ft($args));
        __updateWrite();
    }
""",
         ft=ft, valtype=valtype, valname=valname,
         incr=mf_increment(numval), args=mf_flat_args(valname, numval))

    for method in ("set1Value", "addValue", "insertValue"):
        has_index = method != "addValue"
        emit(out, """
    public void $method(${intindex}$params) {
        __$method(${index}new ConstSF$ft($namelist));
    }

    public void $method(${intindex}SF$ft sf$ft) {
        sf$ft.__updateRead();
        __$method(${index}new ConstSF$ft($sfnamelist));
    }

    public void $method(${intindex}ConstSF$ft sf$ft) {
        __$method(${index}sf$ft);
    }
""",
             method=method,
             ft=ft,
             intindex="int index, " if has_index else "",
             index="index, " if has_index else "",
             params=", ".join(values),
             namelist=", ".join(names),
             sfnamelist=", ".join(f"sf{ft}.{n}" for n in names))


def mf_stringfuncs(out, ft):
    emit(out, """
    public String toString() {
        __updateRead();
        StringBuffer sb = new StringBuffer("[");
        int size = __vect.size();
        for (int i = 0; i < size; i++) {
            if (i > 0) sb.append(", ");
            sb.append(__vect.elementAt(i));
        }
        return sb.append("]").toString();
    }

    public void __fromPerl(BufferedReader in)  throws IOException {
        __vect.clear();
\tString lenline = in.readLine();
\t//System.out.println ("__fromPerl, read in length as " + lenline);
        //int len = Integer.parseInt(in.readLine());
\tint len = Integer.parseInt(lenline);
        for (int i = 0; i < len; i++) {
            ConstSF$ft sf = new ConstSF$ft();
            sf.__fromPerl(in);
            __vect.addElement(sf);
        }
    }

    public void __toPerl(PrintWriter out)  throws IOException {
        StringBuffer sb = new StringBuffer("");
        int size = __vect.size();
\t//out.print(size);
        for (int i = 0; i < size; i++) {
            ((ConstSF$ft) __vect.elementAt(i)).__toPerl(out);
\t    if (i != (size-1)) out.print (", ");
\t}
\t//out.println();
    }
    //public void setOffset(String offs) { this.offset = offs; } //JAS2
    //public String getOffset() { return this.offset; } //JAS2
""", ft=ft)


### Class files ##########################################################

def write_class(cls, superclass, body):
    with open(f"field/{cls}.java", "w", encoding="ascii", newline="\n") as out:
        out.write("//AUTOMATICALLY GENERATED BY genfields.pl.\n")
        out.write("//DO NOT EDIT!!!!\n\n")
        out.write("package vrml.field;\n")
        out.write("import vrml.*;\n")
        out.write("import java.io.BufferedReader;\n")
        out.write("import java.io.PrintWriter;\n")
        out.write("import java.io.IOException;\n")
        out.write(f"\npublic class {cls} extends {superclass} {{\n")
        body(out)
        out.write("}")


def generate(ft, values):
    def sf_class(cls, mutable):
        def body(out):
            sf_constructor(out, cls, values)
            sf_getvalue(out, ft, values)
            if mutable:
                sf_setvalue(out, ft, values)
            sf_stringfuncs(out, ft)
        return body

    def mf_class(cls, mutable):
        def body(out):
            mf_constructor(out, cls, ft, values)
            mf_getvalue(out, ft, values)
            if mutable:
                mf_setvalue(out, ft, values)
            mf_stringfuncs(out, ft)
        return body

    write_class(f"SF{ft}", "Field", sf_class(f"SF{ft}", True))
    write_class(f"ConstSF{ft}", "ConstField", sf_class(f"ConstSF{ft}", False))

    if NO_MF.search(ft):
        return

    write_class(f"MF{ft}", "MField", mf_class(f"MF{ft}", True))
    write_class(f"ConstMF{ft}", "ConstMField", mf_class(f"ConstMF{ft}", False))


def main():
    for ft, spec in FIELD_TYPES.items():
        print(f"Generating {ft} fields")
        generate(ft, spec.split(","))


if __name__ == "__main__":
    main()
