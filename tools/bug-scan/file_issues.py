#!/usr/bin/env python3
"""File bug-scan findings as GitHub issues, queued for owner review. Standard library only.

Usage: file_issues.py FINDINGS.json --repo OWNER/NAME --sha COMMIT [--max-new N] [--dry-run]
  FINDINGS.json  written by findings.py
  --max-new      most new issues per run (default 10); the rest wait for the next run
  --dry-run      print what would be filed or updated; no network writes

Needs GITHUB_TOKEN (issues: write) unless --dry-run. One issue per (tool, rule, file). Each
issue body carries a fingerprint marker; any issue with the bug-scan label and that marker, open
or closed, blocks a new one, so a finding the owner closed is never filed again. New issues are
filed most severe first. The TODO/FIXME inventory and the low-signal warning counts go into one
rolling issue whose body is replaced each run.

Issues are reports, not tasks: Jules is dispatched only from an owner-approved JULES-NNN issue
(docs/automation/JULES_DISPATCH.md section 3.1).
"""
import argparse, json, os, sys, urllib.error, urllib.request

API = "https://api.github.com"
LABEL, QUEUED = "bug-scan", "queued-for-owner-review"
INVENTORY_TITLE = "bug-scan: TODO/FIXME and warning inventory"
INVENTORY_MARK = "<!-- bug-scan:inventory -->"
MAX_LINES = 30
BODY_LIMIT = 60000


def request(method, path, token, body=None):
	req = urllib.request.Request(API + path, method=method,
		data=None if body is None else json.dumps(body).encode(),
		headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
			"X-GitHub-Api-Version": "2022-11-28"})
	with urllib.request.urlopen(req, timeout=60) as r:
		return json.loads(r.read() or "null")


def existing_issues(repo, token):
	"""All issues with the bug-scan label, open and closed: {marker: issue}."""
	found, page = {}, 1
	while True:
		batch = request("GET", f"/repos/{repo}/issues?labels={LABEL}&state=all&per_page=100&page={page}", token)
		for issue in batch:
			for line in (issue.get("body") or "").splitlines():
				if line.startswith("<!-- bug-scan:"):
					found[line.strip()] = issue
		if len(batch) < 100:
			return found
		page += 1


def ensure_labels(repo, token):
	for name, color, desc in ((LABEL, "b60205", "Found by tools/bug-scan"),
			(QUEUED, "fbca04", "Waiting for the owner to accept, reject or turn into a JULES issue")):
		try:
			request("POST", f"/repos/{repo}/labels", token, {"name": name, "color": color, "description": desc})
		except urllib.error.HTTPError as e:
			if e.code != 422:  # 422: the label exists
				raise


def issue_body(group, repo, sha):
	lines = [f"**Tool:** `{group['tool']}` · **Rule:** `{group['rule']}` · **Severity:** {group['severity']}",
		f"**File:** `{group['file']}` · **Scan commit:** {sha}", ""]
	for f in group["items"][:MAX_LINES]:
		link = f"https://github.com/{repo}/blob/{sha}/{group['file']}#L{f['line']}"
		lines.append(f"- [L{f['line']}]({link}): {f['message']}")
	if len(group["items"]) > MAX_LINES:
		lines.append(f"- … and {len(group['items']) - MAX_LINES} more in the scan artifact")
	note = ("Queued for owner review. This may be a false positive. To fix it with Jules, the owner "
		"writes a `JULES-NNN` issue (docs/automation/JULES_DISPATCH.md §3.1); do not dispatch from this issue.")
	lines += ["", note, "", group["marker"]]
	return "\n".join(lines)


def inventory_body(data, sha):
	lines = [f"Rolling inventory from tools/bug-scan, replaced on every run. **Scan commit:** {sha}", "",
		"## Warnings not filed as issues", "", "| Tool | Rule | Count |", "|---|---|---|"]
	for row in data["unfiled"]:
		lines.append(f"| `{row['tool']}` | `{row['rule']}` | {row['count']} |")
	lines += ["", f"## TODO/FIXME/XXX comments: {data['todo']['total']}", "", "| Directory | Count |", "|---|---|"]
	for d, n in data["todo"]["by_dir"]:
		lines.append(f"| `{d}` | {n} |")
	lines += ["", "The full lists are in the workflow run's `bug-scan` artifact. Queued for owner review.", "", INVENTORY_MARK]
	return "\n".join(lines)[:BODY_LIMIT]


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("findings")
	ap.add_argument("--repo", required=True)
	ap.add_argument("--sha", required=True)
	ap.add_argument("--max-new", type=int, default=10)
	ap.add_argument("--dry-run", action="store_true")
	a = ap.parse_args()
	with open(a.findings) as fh:
		data = json.load(fh)
	token = os.environ.get("GITHUB_TOKEN", "")
	if not a.dry_run and not token:
		sys.exit("GITHUB_TOKEN is not set")
	known = {} if a.dry_run else existing_issues(a.repo, token)
	if not a.dry_run:
		ensure_labels(a.repo, token)

	new = [g for g in data["groups"] if g["marker"] not in known]
	print(f"bug-scan: {len(data['groups'])} groups, {len(data['groups']) - len(new)} already filed, "
		f"{len(new)} new, filing at most {a.max_new}")
	for g in new[:a.max_new]:
		title = f"bug-scan: {g['rule']} in {g['file']}"
		if a.dry_run:
			print(f"  would file: {title} ({len(g['items'])} findings)")
			continue
		try:
			issue = request("POST", f"/repos/{a.repo}/issues", token,
				{"title": title, "body": issue_body(g, a.repo, a.sha), "labels": [LABEL, QUEUED]})
		except urllib.error.HTTPError as e:
			print(f"  failed to file {title}: HTTP {e.code}", file=sys.stderr)
			if e.code in (403, 429):  # rate limited: file the rest next run
				break
			continue
		print(f"  filed #{issue['number']}: {title}")

	body = inventory_body(data, a.sha)
	inv = known.get(INVENTORY_MARK)
	if a.dry_run:
		print(f"  would {'update' if inv else 'create'} the inventory issue ({len(body)} chars)")
	elif inv:
		request("PATCH", f"/repos/{a.repo}/issues/{inv['number']}", token, {"body": body})
		print(f"  updated inventory #{inv['number']}")
	else:
		issue = request("POST", f"/repos/{a.repo}/issues", token,
			{"title": INVENTORY_TITLE, "body": body, "labels": [LABEL, QUEUED]})
		print(f"  filed inventory #{issue['number']}")


if __name__ == "__main__":
	main()
