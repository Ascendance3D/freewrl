#!/usr/bin/env python3
"""Convert a scan.sh cppcheck.log into a GitLab SAST report (schema 15.0.7). Standard library only.

Usage: gitlab_sast.py CPPCHECK.log REPORT.json START END
  START, END  scan start and end times, ISO 8601 (YYYY-MM-DDTHH:MM:SS)

GitLab Ultimate shows the report in the Vulnerability report and on merge requests; on Free it is
only a job artifact. cppcheck error is High, warning Medium, portability Low. Vulnerability ids
are UUIDv5 of (rule, file, message, occurrence number), so a finding keeps its id when code above
it moves.
"""
import json, re, subprocess, sys, uuid

LINE = re.compile(r"^(?P<file>[^\s:]+):(?P<line>\d+):\d+: (?P<sev>\w+): (?P<msg>.*) \[(?P<rule>\w+)\]$")
SEVERITY = {"error": "High", "warning": "Medium", "portability": "Low"}
NS = uuid.UUID("6f0b3c1e-6d64-4b61-9a43-4d3c1e2a7f00")


def main():
	log, report, start, end = sys.argv[1:5]
	version = subprocess.run(["cppcheck", "--version"], capture_output=True, text=True).stdout.split()[-1]
	tool = {"id": "cppcheck", "name": "Cppcheck", "version": version, "vendor": {"name": "Cppcheck"}}
	vulns, seen, count = [], set(), {}
	with open(log, errors="replace") as fh:
		for text in fh:
			m = LINE.match(text.rstrip("\n"))
			if not m or m["sev"] not in SEVERITY or (m["file"], m["line"], m["rule"]) in seen:
				continue
			seen.add((m["file"], m["line"], m["rule"]))
			key = (m["rule"], m["file"], m["msg"])
			count[key] = count.get(key, 0) + 1
			vulns.append({
				"id": str(uuid.uuid5(NS, "|".join(key + (str(count[key]),)))),
				"name": f"cppcheck {m['rule']}",
				"description": m["msg"],
				"severity": SEVERITY[m["sev"]],
				"identifiers": [{"type": "cppcheck_rule", "name": f"cppcheck {m['rule']}", "value": m["rule"],
					"url": "https://cppcheck.sourceforge.io/"}],
				"location": {"file": m["file"], "start_line": int(m["line"])},
			})
	data = {"version": "15.0.7", "vulnerabilities": vulns,
		"scan": {"analyzer": tool, "scanner": tool, "type": "sast", "status": "success",
			"start_time": start, "end_time": end}}
	with open(report, "w") as fh:
		json.dump(data, fh, indent=1)
	print(f"gitlab_sast: {len(vulns)} cppcheck findings")


if __name__ == "__main__":
	main()
