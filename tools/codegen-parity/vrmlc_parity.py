#!/usr/bin/env python3
"""Three-way parity check of the Perl and Python node-table generators.

This tool is for the shadow stage only. Remove it when VRMLC.pm is removed.

It compares, byte for byte, the four generated files from:

  * the committed files (git HEAD, or --ref),
  * VRMLC.pm, run with PERL_HASH_SEED 0, 1 and 12345,
  * vrmlc.py, run two times.

Each generator runs in its own new temporary tree. The tree holds a copy of
freex3d/codegen/*.pm and *.py from the work tree and the license template.
The tool does not change the work tree.

Exit status 0 means that all copies of all four files are identical.
"""

import sys

if sys.version_info < (3, 12):
    sys.exit("vrmlc_parity.py: Python 3.12 or later is required.")

import argparse  # noqa: E402
import difflib  # noqa: E402
import hashlib  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
FREEX3D = REPO / "freex3d"
LICENSE = Path("versions/template/license.c.in")
OUTPUTS = (
    "src/lib/scenegraph/GeneratedCode.c",
    "src/libeai/GeneratedCode.c",
    "src/lib/vrml_parser/NodeFields.h",
    "src/lib/vrml_parser/Structs.h",
)
PERL_SEEDS = ("0", "1", "12345")
PYTHON_RUNS = 2


class ParityError(Exception):
    pass


def make_tree(base):
    """Make a minimal freex3d tree with empty output directories."""
    root = Path(tempfile.mkdtemp(prefix="vrmlc-parity-", dir=base)) / "freex3d"
    (root / "codegen").mkdir(parents=True)
    for src in sorted((FREEX3D / "codegen").iterdir()):
        if src.suffix in (".pm", ".py") and src.is_file():
            shutil.copy2(src, root / "codegen" / src.name)
    (root / LICENSE.parent).mkdir(parents=True)
    shutil.copy2(FREEX3D / LICENSE, root / LICENSE)
    for rel in OUTPUTS:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
    return root


def read_outputs(root):
    result = {}
    for rel in OUTPUTS:
        path = root / rel
        if not path.is_file():
            raise ParityError(f"{path} was not generated")
        result[rel] = path.read_bytes()
    return result


def run(cmd, cwd, env):
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise ParityError(f"{' '.join(cmd)} failed with exit {proc.returncode}:\n"
                          f"{proc.stdout}{proc.stderr}")
    if proc.stdout:
        raise ParityError(f"{' '.join(cmd)} wrote to stdout (a data problem):\n{proc.stdout}")
    return proc


def run_perl(perl, base, seed):
    root = make_tree(base)
    env = dict(os.environ, PERL_HASH_SEED=seed, PERL_PERTURB_KEYS="2")
    run([perl, "VRMLC.pm"], root / "codegen", env)
    return read_outputs(root)


def run_python(python, base):
    root = make_tree(base)
    # Run from another directory: vrmlc.py must not depend on the cwd.
    run([python, "-B", str(root / "codegen" / "vrmlc.py")], base, dict(os.environ))
    if list(root.rglob("__pycache__")):
        raise ParityError("vrmlc.py wrote __pycache__")
    return read_outputs(root)


def committed_outputs(ref):
    result = {}
    for rel in OUTPUTS:
        spec = f"{ref}:freex3d/{rel}"
        proc = subprocess.run(["git", "-C", str(REPO), "show", spec], capture_output=True, check=False)
        if proc.returncode != 0:
            raise ParityError(f"git show {spec} failed: {proc.stderr.decode(errors='replace')}")
        result[rel] = proc.stdout
    return result


def describe_difference(rel, name_a, a, name_b, b):
    first = next((i for i, (x, y) in enumerate(zip(a, b, strict=False)) if x != y), min(len(a), len(b)))
    line = a[:first].count(b"\n") + 1
    print(f"  MISMATCH {rel}: {name_a} vs {name_b}")
    print(f"    first different byte: {first}, line {line}")
    lines_a = a.decode("ascii", errors="replace").splitlines(keepends=True)
    lines_b = b.decode("ascii", errors="replace").splitlines(keepends=True)
    lo, hi = max(0, line - 6), line + 5
    diff = difflib.unified_diff(lines_a[lo:hi], lines_b[lo:hi], name_a, name_b, lineterm="")
    for text in list(diff)[:40]:
        print("    " + repr(text)[1:-1])


def tool_version(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return (proc.stdout or proc.stderr).strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", default="HEAD", help="git ref of the committed files")
    parser.add_argument("--perl", default="perl", help="Perl interpreter")
    parser.add_argument("--python", default=sys.executable, help="Python interpreter")
    parser.add_argument("--keep", action="store_true", help="keep the temporary trees")
    args = parser.parse_args(argv)

    print(f"perl:   {tool_version([args.perl, '-e', 'print $^V'])}")
    print(f"python: {tool_version([args.python, '--version'])}")
    print(f"ref:    {tool_version(['git', '-C', str(REPO), 'rev-parse', args.ref])}")

    base = tempfile.mkdtemp(prefix="vrmlc-parity-")
    try:
        results = {"committed": committed_outputs(args.ref)}
        for seed in PERL_SEEDS:
            results[f"perl-seed-{seed}"] = run_perl(args.perl, base, seed)
        for number in range(1, PYTHON_RUNS + 1):
            results[f"python-run-{number}"] = run_python(args.python, base)
    except ParityError as err:
        print(f"FAIL: {err}")
        return 2
    finally:
        if args.keep:
            print(f"temporary trees kept in {base}")
        else:
            shutil.rmtree(base, ignore_errors=True)

    status = 0
    reference = "committed"
    for rel in OUTPUTS:
        want = results[reference][rel]
        print(f"{rel}")
        for name, files in results.items():
            data = files[rel]
            mark = "same" if data == want else "DIFFERENT"
            print(f"  {name:16} {len(data):9} bytes  sha256 {hashlib.sha256(data).hexdigest()}  {mark}")
        for name, files in results.items():
            if files[rel] != want:
                describe_difference(rel, reference, want, name, files[rel])
                status = 1

    print("PASS: committed = Perl = Python for all four files" if status == 0
          else "FAIL: generated files differ")
    return status


if __name__ == "__main__":
    sys.exit(main())
