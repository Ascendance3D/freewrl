# Jules dispatch: environment check, setup and review flow

This is the hand-off for running Google Jules against this repository (`Ascendance3D/freewrl`) from a workstation. It covers:

- checking that an existing setup works;
- setting it up from scratch;
- the dispatch, review and merge flow, and the pitfalls already hit in practice.

The FreeWRL-specific values are in [Repository settings](#repository-settings).

Jules is an external, paid service. Dispatch only work the owner has approved, and never put credentials in a task, issue, PR or commit.

## Components

| Piece | What it is | Where it lives |
|---|---|---|
| `jules-dispatch` CLI | [`@yuuqq/jules-dispatch`](https://github.com/Yuuqq/jules-dispatch) (tested with 1.3.2). Batch dispatch, status, plans, messages, and an MCP server. | `npm install -g --prefix ~/.local`, giving `~/.local/bin/jules-dispatch` |
| Per-repo wrapper | A small script that loads **only** `JULES_API_KEY` from the repo's untracked `.env.local`, sets the default source and branch, and then runs the CLI. | `~/.local/bin/jules-dispatch-<repo>` (mode `700`) |
| Account wrapper | Like the per-repo wrapper, but it unsets `JULES_DEFAULT_SOURCE` and `JULES_DEFAULT_BRANCH`, so every task must name its own `source` and `branch`. The MCP server uses this one. | `~/.local/bin/jules-dispatch-account` (mode `700`) |
| MCP server | `jules-dispatch-account mcp`, registered for Claude Code and Codex. Exposes `jules_get_plan`, `jules_approve_plan`, `jules_send_message`, `jules_status`, and others. The key covers the whole Jules account, so the server sees every repository's sessions. | User-scope MCP config of each client |
| Skill | Agent instructions for using the tools. | `~/.claude/skills/jules-dispatch/`, `~/.codex/skills/jules-dispatch/` |
| API key | `JULES_API_KEY`, created at <https://jules.google.com/settings>. | The repo's `.env.local`, ignored by `.gitignore` (`.env*.local`). Never in MCP config. |
| Jules GitHub app | Must have access to the repo, so it appears as a Jules **source**. | Jules settings, GitHub app installation |

## 1. Check an existing environment

Run these checks first; they show what is missing. Each one prints no secret.

```bash
# CLI installed, at the expected version
jules-dispatch --version

# Wrapper present and private (expect -rwx------)
ls -l ~/.local/bin/jules-dispatch-freewrl

# The key variable exists in .env.local. This prints a count, not the value.
rg -c '^JULES_API_KEY=' <freewrl-checkout>/.env.local

# .env.local is ignored by git
git -C <freewrl-checkout> check-ignore -v .env.local

# Node >= 20, key set, config valid, API reachable: expect five ✓ lines
~/.local/bin/jules-dispatch-freewrl doctor

# The repo is a connected Jules source (expect sources/github/Ascendance3D/freewrl)
~/.local/bin/jules-dispatch-freewrl sources --json | jq -r '.sources[].name' | rg freewrl

# The MCP server is registered and connects
claude mcp get jules-dispatch        # Claude Code: Status ✔ Connected
codex mcp list | rg jules            # Codex: enabled

# Skills installed, with identical copies for both clients
diff -rq ~/.claude/skills/jules-dispatch ~/.codex/skills/jules-dispatch && echo identical

# Account load: count sessions by state. Every state except COMPLETED and FAILED
# takes a concurrency slot, including other repositories' sessions.
~/.local/bin/jules-dispatch-freewrl status --json \
  | jq -r '.results | group_by(.state)[] | "\(.[0].state): \(length)"'
```

If every check passes, skip to [Dispatch and review](#3-dispatch-and-review).

## 2. Set up from scratch

### 2.1 Install the CLI

```bash
npm install -g --prefix ~/.local @yuuqq/jules-dispatch
jules-dispatch --version
```

`~/.local/bin` must be on `PATH`.

### 2.2 API key

1. Create a key at <https://jules.google.com/settings>.
2. Add `JULES_API_KEY=<key>` to the repo checkout's `.env.local`. Do not paste the key into chat, an issue or a command line.
3. Confirm that `git check-ignore -v .env.local` reports the ignore rule.

### 2.3 Wrapper

The CLI reads `.env` from `--project`. The wrapper passes `--project /tmp` so no repo `.env` is picked up. It exports only the key, because `.env.local` also holds unrelated secrets (build-service and release tokens) that must not reach the Jules process. **Do not** use `set -a; . .env.local`, which exports every variable in the file.

```bash
cat > ~/.local/bin/jules-dispatch-freewrl <<'EOF'
#!/usr/bin/env bash
# Runs jules-dispatch for FreeWRL. Loads ONLY JULES_API_KEY from .env.local.
set -euo pipefail
ENV_FILE=<freewrl-checkout>/.env.local
key="$(sed -n 's/^JULES_API_KEY=//p' "$ENV_FILE" | head -n 1)"
key="${key%\"}"; key="${key#\"}"; key="${key%\'}"; key="${key#\'}"
[ -n "$key" ] || { echo "JULES_API_KEY missing in $ENV_FILE" >&2; exit 1; }
export JULES_API_KEY="$key"
export JULES_DEFAULT_SOURCE="${JULES_DEFAULT_SOURCE:-sources/github/Ascendance3D/freewrl}"
export JULES_DEFAULT_BRANCH="${JULES_DEFAULT_BRANCH:-master}"
exec "$HOME/.local/bin/jules-dispatch" --project /tmp "$@"
EOF
chmod 700 ~/.local/bin/jules-dispatch-freewrl
~/.local/bin/jules-dispatch-freewrl doctor
```

Use the absolute checkout path for `ENV_FILE`. The defaults only apply when a task omits `source` or `branch`; every task file should still set both explicitly.

### 2.4 Register the MCP server

Register the account wrapper, not a per-repo one. One MCP server serves every repository, and a per-repo default source would silently send a task that omits `source` to the wrong repository. The account wrapper is the per-repo wrapper with the two `JULES_DEFAULT_*` exports replaced by `unset JULES_DEFAULT_SOURCE JULES_DEFAULT_BRANCH`.

```bash
claude mcp add -s user jules-dispatch -- ~/.local/bin/jules-dispatch-account mcp
codex mcp add jules-dispatch -- ~/.local/bin/jules-dispatch-account mcp
```

Remove any older registration that points at a per-repo wrapper first (`claude mcp remove jules-dispatch -s user`). Restart the client after you register the server.

### 2.5 Install the skill

The skill ships in the GitHub repository (`skills/jules-dispatch`), not in the npm package.

```bash
git clone --depth 1 https://github.com/Yuuqq/jules-dispatch /tmp/jules-dispatch-src
cp -r /tmp/jules-dispatch-src/skills/jules-dispatch ~/.claude/skills/
cp -r /tmp/jules-dispatch-src/skills/jules-dispatch ~/.codex/skills/
```

Then rerun every check in [section 1](#1-check-an-existing-environment).

## Repository settings

| Setting | FreeWRL |
|---|---|
| Jules source | `sources/github/Ascendance3D/freewrl` |
| Base branch | **`master`** (canonical trunk; `develop` is retired) |
| Task branches | `fix-*` / `feature-*` from `master` (see `CLAUDE.md` › Git workflow) |
| CI on PRs | CodeQL analysis and a CodeRabbit review on every PR. **No build or test workflow runs on PRs.** `macos.yml` and `release-macos.yml` are `workflow_dispatch` only |
| Local verification | Linux autotools build and tests (see `CLAUDE.md` › Build), plus the macOS Xcode build where the change touches it |
| Merge method | Merge commit (`gh pr merge --merge`) |
| Review worktrees | `~/Projects/cybertown/.worktrees/freewrl/<lane>` |
| Wrapper | `jules-dispatch-freewrl` (CLI); `jules-dispatch-account` (MCP) |

FreeWRL PRs get no automatic build or test checks. CodeQL and CodeRabbit do not build or run FreeWRL, so the reviewer's local build and test run is the only pre-merge gate. A PR with only CodeQL and CodeRabbit passes is not a tested PR.

`macos.yml` cannot test a PR branch: its first step fails unless the run is on `master` and `github.sha` equals `expected_sha`. When a merged PR touched macOS code, start it once on `master` with the merge commit, then watch it:

```bash
gh workflow run macos.yml --repo Ascendance3D/freewrl --ref master -f expected_sha=<full merge sha>
gh run list --repo Ascendance3D/freewrl --workflow macos.yml --limit 1
gh run watch <run-id> --repo Ascendance3D/freewrl --exit-status
```

Start it only if `master` still points at that merge commit. If the run fails, open a fix-up PR. Do not rerun the run.

## 3. Dispatch and review

### 3.1 Issue first

Each task is an owner-authored GitHub issue titled `JULES-NNN — …`. The issue states:

- the goal;
- the exact allowed file or files;
- numbered cases;
- acceptance criteria;
- the limits.

Write limits as explicit rules: no dependency, workflow, licensing or security-policy changes; format only the code you add; do not commit scratch or patch files.

The issue starts as **"Queued for owner review"**. Dispatch only after the owner explicitly approves it.

### 3.2 Task file

Write one JSON file per task in a scratch directory, such as `/tmp/jules-review/<wave>/`:

```json
{
  "title": "JULES-NNN — short title",
  "prompt": "<issue text>\n\n## Delivery requirements\n- Branch `fix-NNN-<slug>` from master.\n- PR description begins `Fixes #<issue>`, lists only what the diff contains, and ends with `git diff --stat origin/master...HEAD`.\n- Run <exact build/test commands> and report exact pass/fail counts.\n- Format only the code you add or change; never run a formatter over whole files.\n- Do not commit scratch, patch or helper files.\n- No Signed-off-by trailers. Open a draft PR. Never merge.",
  "source": "sources/github/Ascendance3D/freewrl",
  "branch": "master",
  "autoMode": "AUTO_CREATE_PR",
  "requirePlanApproval": true
}
```

Dispatch a wave of three to five independent tasks:

```bash
~/.local/bin/jules-dispatch-freewrl batch /tmp/jules-review/<wave>/ --json \
  | jq -r '.results[] | "\(.title) \(.sessionId // "-") \(.error // "")"'
```

Post `Jules session started: sessions/<id>` on each issue.

### 3.3 Monitor

The CLI's `wait` (and `jules_monitor`) can return 404 for brand-new sessions. Poll `status` instead:

```bash
~/.local/bin/jules-dispatch-freewrl status --ids <id1> <id2> --json \
  | jq -r '.results[] | "\(.sessionId) \(.state) \(.prUrl // "")"'
```

The states that need action are `AWAITING_PLAN_APPROVAL`, `AWAITING_USER_FEEDBACK`, `COMPLETED` (PR ready) and `FAILED`.

**`cancel` deletes the session.** The CLI's `cancel` and the MCP `jules_cancel_session` send `DELETE /sessions/<id>`. The session, its plan and its activity log are gone afterwards (`get` returns 404). To stop a session, send it a message instead (`message <id> "Stop. Do not push or open a PR."`). Cancel only with the owner's approval.

### 3.4 Plan review

Read every plan (`plan <id>` or `jules_get_plan`) against the issue before approving it.

- **Already covered:** if a plan says a case is already covered, read the named test first.
- **Can't be built:** if a plan flags that a case cannot be built, verify that yourself before correcting it.
- **Corrections:** send them with `message <id> "<text>"` (`jules_send_message`) while the plan is pending. Read the revised plan, and approve it only when it matches the issue.

### 3.5 PR review

Review every PR in its own git worktree, outside the main checkout so its dirty state is untouched. Put it at the path in [Repository settings](#repository-settings), and remove it with `git worktree remove` when the review ends. Fetch `pull/<N>/head:refs/remotes/pr/<N>` first.

1. **Diff against the description.** Jules PR descriptions have claimed changes that were not in the diff. Confirm every claim with `git diff origin/master...refs/remotes/pr/<N>` and a targeted `rg`.
2. **Scope.** Check `git diff --stat`. Revert formatter churn in unrelated files and production code, and delete any stray patch or helper files.
3. **Build and tests.** Run them locally and record exact counts. Compare skipped counts with the base: a new skip needs a reason.
4. **Tests can fail.** Watch for `try/catch` blocks that swallow assertion errors, conditional `skip`s that hide regressions, and fixtures the code never reaches. Restore the old production code temporarily and confirm the new test fails (a mutation check).
5. **Second review.** Run a scoped `codex exec -s read-only -o <file> "<explicit requirements>"`, with a timeout of 900 s or more. A plain `codex review` has missed real defects.

Send findings back to the same session. If a session fails a fix round, either start a fresh session from the PR branch, or have the owner apply a fix-up commit. The owner chooses which.

### 3.6 Merge

Merge only with owner authorization:

1. Wait until your local build and test run passes on the final head, and until CodeQL and the CodeRabbit review are complete.
2. Resolve any open review threads. CodeRabbit threads count.
3. Merge with a merge commit:

```bash
gh pr ready <N>
gh pr merge <N> --merge --match-head-commit <full-sha> --subject "Merge PR #<N>: ..." --body "Fixes #<issue>. ..."
```

Then message the session: "PR merged. This task is complete. Do not push further commits or open new PRs." Sessions often briefly reactivate after this message. Check that the PR head did not change.

4. Delete the head branch. GitHub deletes it automatically only for a merged PR, so check after every merge **and** every close:

```bash
git ls-remote --heads origin <branch>      # expect no output after a merge
git push origin --delete <branch>          # needed after a close; first confirm the PR is MERGED or CLOSED
```

5. Check again after the session goes quiet. A Jules session can push its branch again after the PR is merged or closed. If the branch is back, send the session the stop message again and delete the branch again. The PR keeps its commits under `refs/pull/<N>/head`, so nothing is lost.

## Pitfalls already hit

| Symptom | Cause | What to do |
|---|---|---|
| `FAILED_PRECONDITION` (400) on dispatch | The account's concurrency is full, shared across all repositories | Count non-terminal sessions, then retry every 5 minutes |
| `wait` returns 404 | New sessions are not yet listable | Poll `status --ids` |
| PR reformats unrelated files | A "use rustfmt/clang-format style" instruction was applied to whole files | Say "format only the code you add"; revert the churn |
| PR description lists changes absent from the diff | The model's summary drifted | Verify each claim against the diff |
| A test passes against the old code | A swallowed assertion, a vacuous fixture, or a blanket skip | Run a mutation check (restore the old code; the test must fail) |
| `gh pr edit` fails (Projects classic deprecation) | A GraphQL deprecation in `gh` | `gh api -X PATCH repos/<owner>/<repo>/pulls/<N> -F body=@file` |
| Merge "prohibited by base branch policy" | CI still running, or an unresolved review thread | Wait for CI; resolve threads |
| A session or PR exists with no `JULES-NNN` issue; its prompt starts `## Task:` with `File:`, `Description:` and `Rationale:` | Not started by this flow: the dispatch CLI and MCP do not produce that prompt. It matches Jules's own TODO-comment suggestions in the web UI. | Treat the PR like any other: review it per §3.5, or close it. Do not merge without an issue. |
| Closed PR's branch still on `origin` | Auto-delete covers merged PRs only, and sessions can push again | §3.6 steps 4–5 |
| A session, plan or log is gone (404) | It was cancelled: `cancel` is a `DELETE` | Stop sessions by message, not `cancel` |
| `jules_list_sessions` result is too large for the MCP client | Each session carries its full prompt | Use the CLI `status --json` with `jq`, or a small `pageSize` |

## Security

- The key lives only in the untracked `.env.local`. The wrapper exports only `JULES_API_KEY`, and MCP configs hold no secrets.
- Never echo, log, or paste key values. Check a variable's presence with `rg -c '^NAME='`.
- Do not put signing, release or deployment secrets in Jules tasks or repository settings that Jules can read.
