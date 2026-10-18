#!/usr/bin/env python3
"""Turn bug-scan logs into one findings file for file_issues.py. Standard library only.

Usage: findings.py ROOT OUTDIR
  ROOT    the repository checkout that was scanned
  OUTDIR  holds gcc.log, cppcheck.log and todo.txt from scan.sh; findings.json is written there

Only diagnostics in files under ROOT/freex3d are kept, deduplicated on (file, line, rule): a
header warning appears once per translation unit. Groups are one (tool, rule, file) each, most
severe first:
  high    gcc -Wanalyzer-* definite findings, cppcheck error
  medium  gcc -Wanalyzer-possible-*, the gcc warnings in SIGNAL, cppcheck warning
Every other warning (unused parameters, comments, sign compares...) is only counted, in the
rolling inventory. The fingerprint has no line numbers, so an edit that moves code does not
file the same group again.
"""
import collections, hashlib, json, os, re, sys

GCC = re.compile(r"^(?P<file>[^\s:]+):(?P<line>\d+):\d+: (?P<sev>warning|error): (?P<msg>.*?) \[-W(?P<rule>[\w=+-]+)\]$")
CPPCHECK = re.compile(r"^(?P<file>[^\s:]+):(?P<line>\d+):\d+: (?P<sev>\w+): (?P<msg>.*) \[(?P<rule>\w+)\]$")
TODO = re.compile(r"^(?P<file>[^:]+):\d+:")
OOM = re.compile(r"virtual memory exhausted|out of memory|internal compiler error")
SIGNAL = {"incompatible-pointer-types", "misleading-indentation", "sequence-point", "maybe-uninitialized",
	"uninitialized", "format-truncation=", "format-overflow=", "format=", "stringop-truncation",
	"stringop-overflow=", "sizeof-pointer-memaccess", "overflow", "dangling-else", "logical-not-parentheses",
	"char-subscripts", "address", "absolute-value", "int-in-bool-context", "enum-conversion",
	"cast-function-type", "discarded-qualifiers", "array-bounds=", "restrict", "return-type",
	"implicit-function-declaration", "int-conversion"}
RANK = {"high": 0, "medium": 1}


def severity(tool, rule, sev):
	if tool == "gcc":
		if rule.startswith("analyzer-"):
			return "medium" if rule.startswith("analyzer-possible-") else "high"
		return "medium" if rule in SIGNAL or sev == "error" else None
	return {"error": "high", "warning": "medium"}.get(sev)


def relative(root, path):
	path = os.path.relpath(os.path.realpath(os.path.join(root, path)), root)
	return path if path.startswith("freex3d" + os.sep) else None


def read(path):
	try:
		with open(path, errors="replace") as fh:
			return fh.read().splitlines()
	except FileNotFoundError:
		return []


def main():
	root, out = os.path.realpath(sys.argv[1]), sys.argv[2]
	seen, groups, unfiled = set(), {}, collections.Counter()
	for tool, pattern, log in (("gcc", GCC, "gcc.log"), ("cppcheck", CPPCHECK, "cppcheck.log")):
		for text in read(os.path.join(out, log)):
			m = pattern.match(text)
			if not m:
				continue
			path = relative(root, m["file"])
			if not path or (path, m["line"], m["rule"]) in seen:
				continue
			seen.add((path, m["line"], m["rule"]))
			sev = severity(tool, m["rule"], m["sev"])
			if not sev:
				unfiled[(tool, m["rule"])] += 1
				continue
			key = (tool, m["rule"], path)
			if key not in groups:
				fp = hashlib.sha1("|".join(key).encode()).hexdigest()[:16]
				groups[key] = {"tool": tool, "rule": m["rule"], "file": path, "severity": sev,
					"marker": f"<!-- bug-scan:fp={fp} -->", "items": []}
			groups[key]["items"].append({"line": int(m["line"]), "message": m["msg"]})

	oom = sum(bool(OOM.search(text)) for text in read(os.path.join(out, "gcc.log")))
	if oom:
		unfiled[("gcc", "memory limit or compiler crash (file not analyzed)")] = oom

	todo_dirs = collections.Counter()
	todo_lines = read(os.path.join(out, "todo.txt"))
	for text in todo_lines:
		m = TODO.match(text)
		if m:
			todo_dirs[os.path.dirname(m["file"])] += 1

	ordered = sorted(groups.values(), key=lambda g: (RANK[g["severity"]], -len(g["items"]), g["file"], g["rule"]))
	for g in ordered:
		g["items"].sort(key=lambda f: f["line"])
	data = {"groups": ordered,
		"unfiled": [{"tool": t, "rule": r, "count": n} for (t, r), n in unfiled.most_common()],
		"todo": {"total": len(todo_lines), "by_dir": todo_dirs.most_common(40)}}
	with open(os.path.join(out, "findings.json"), "w") as fh:
		json.dump(data, fh, indent=1)
	high = sum(g["severity"] == "high" for g in ordered)
	print(f"bug-scan: {len(ordered)} groups ({high} high), {sum(unfiled.values())} unfiled warnings, "
		f"{len(todo_lines)} TODO/FIXME/XXX")


if __name__ == "__main__":
	main()
