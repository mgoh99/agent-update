---
name: agent-update
description: Build a one-page update about this agent — what it is, what it owns, its skills, connectors and schedule, and what it accomplished for the user in the last two weeks — as a polished static HTML page in a fixed layout. Use when the user asks for an agent update, a status page, "what have you done for me", "what are you working on", a two-week recap, or this agent's profile page.
---

# Agent update

One page about **this agent only**, rendered in a fixed design. Don't restyle it, add sections or reorder them. The look comes from `assets/style.css` and `scripts/build.py` in this skill's directory; your job is accurate, evidence-backed data.

Sections, in order: header (name, role, status pill, since line, counts) → Purpose → Skills → Connectors and CLIs → Scheduled jobs → **The last two weeks**.

"The user" below means the person you work for. Use their name on the page if you know it.

## 1. Work out who you are

Read whatever defines you in this environment, for example:

- Instruction files: `CLAUDE.md` / `AGENTS.md` in the project and in `~/.claude/`, plus any system prompt or persona you were given.
- Skills: `.claude/skills/*/SKILL.md` in the project, `~/.claude/skills/`, and skills from installed plugins.
- Connectors: `claude mcp list`, `.mcp.json`, settings files, and the CLIs your instructions tell you to use.
- Schedules: scheduled tasks or routines, cron entries, CI schedules, or whatever scheduler your instructions name.

Take **names only** from config. Never put keys, tokens, account IDs, environment values or private URLs on the page.

## 2. Fill the profile sections

- **name / role / since**: your name (or the project's name for you), a 2–5 word role, and `"Running since <month year> · update as of <today>"`. Set `live` to false and `statusLabel` to something like "Paused" if you are not currently running on a schedule or in use.
- **purpose**: 1–3 plain sentences on what you do for the user and what you own. **bounds**: 3–5 one-line limits (what you never do, what needs their yes, what you only read).
- **skills**: the skills that are specifically yours, grouped 2–6 per theme: `[slug, "Plain Title", "one-line outcome"]`. Put general-purpose skills you share with other agents in `shared.items`. Leave out built-in tools.
- **conn**: `[slug, "System name", "CLI | MCP server | Plugin | Files | API", "what it holds", "access level"]`. State access honestly (read, draft only, read / write, send / receive).
- **jobs**: active scheduled jobs as `[cadence, time, name, short note, sep]`. Use words for cadence ("Mon–Fri", "9:15 AM"), not cron syntax. Set the fifth element to `1` on the first row of each new cadence block. Order: frequent → daily → weekly → monthly. Set `jobsNote` to the timezone and source, e.g. `"Eastern time. From the scheduler on 5 October 2026"`. If you have no schedule, leave `jobs` empty and say so in `jobsFootnote`.

## 3. The last two weeks (the part the user cares about)

Window: today minus 14 days to today, unless the user asks for a different period. Gather evidence from what you can actually see, for example:

```sh
git log --since="14 days ago" --author="<you or the user>" --oneline   # in each repo you work in
ls -t ~/.claude/projects/*/ | head                                       # recent Claude Code sessions (JSONL transcripts)
```

Also use the run history of scheduled jobs, PRs and issues you opened or closed (`gh pr list --author @me --search "created:>=<date>"`), documents or pages you published, task trackers you update, and any notes or memory files you keep.

Write it for the user, not an engineer:

- Each item is an **outcome**: what changed for them, with a number where you have one ("Reconciled September — 4 unmatched items flagged", not "ran reconcile.py").
- Group into 2–4 themes, usually 4–12 items in total. Merge repeats ("Weekly report ×2").
- `result` is a short tag of at most three words ("Shipped", "2 replies", "Report", "Waiting on you"). Add `url` only for a link you have verified.
- `summary`: one or two sentences giving the headline of the fortnight and anything waiting on the user.
- Only claim what the evidence shows. Failed or unknown runs aren't accomplishments; mention a failure only if it affected the user. Skip routine health checks, heartbeats and runs that did nothing.
- If there's little or nothing, say so plainly. Don't pad.
- Summarise. No private message contents, third parties' personal details or credentials.

## 4. Build, check and deliver

1. Write the data as JSON in exactly the shape of [references/example.json](references/example.json). Keep it in one stable place (e.g. `agent-update/data.json` in your workspace) so the next update overwrites the same page.
2. Render it with the bundled script (Python 3, standard library only):
   ```sh
   python3 <this skill's directory>/scripts/build.py agent-update/data.json
   ```
   It writes `index.html` beside the data, or to a second path argument if you give one. It stops with a message if a required field is missing.
3. Open the HTML and check that every section rendered, the counts are right and nothing sensitive is on the page.
4. Deliver the page through whatever your environment offers: publish it as an artifact or hosted page if you have that tool, otherwise give the user the file path. Reply in one or two sentences with the fortnight's headline, anything waiting on them, and the link or path.

The page loads two Google Fonts (DM Serif Display and Outfit) and falls back to system fonts when offline. Everything else is inline, and the page needs no JavaScript.
