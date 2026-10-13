# Agentic Government — a Claude Code skill

**Run Claude Code like a small, well-run government.** One *manager* model talks to you and plans the work. It delegates each piece to a cheaper or stronger worker model according to how hard the task is. A top-tier *checker* verifies the result before anything counts as done. A *ledger* records the cost, time, checker verdicts and rework of every job, so you can see whether the whole arrangement actually saves you tokens and time.

By Aleksandre Glonti · Nomad Devs (nomaddevs.club)

Status: **v0.1** — extracted from a few days of real use on a solo studio's release work. The structure is stable; the numbers below are early.

## The roles

Each worker is a Claude Code agent file (`agents/*.md`) with a pinned model and a restricted tool list. The manager is your own session.

| Role | Agent file | Model | Does | Never does |
|---|---|---|---|---|
| **Zeus, the Chancellor** (manager) | your session | Opus or top tier | talks to you, plans, delegates, decides, appends the ledger | long builds, watcher loops |
| **Pip, the Clerk** (runner) | `runner` | Haiku | read-only chores: find files, grep, read logs, watch a folder | edit, build, send, decide |
| **Iris, the Envoy** (researcher) | `researcher` | Sonnet | web research, policy checks, comparisons, drafts into a file | publish, send, change accounts |
| **Gela, the Engineer** (builder) | `builder` | Opus | real changes: code, scripts, assets, release prep | irreversible or outward actions |
| **Vera, the Auditor** (checker) | `checker` | top tier (Fable) | read-only audit: `PASS` or `FIX-NEEDED` with evidence | fix the work herself |
| **Clio, the Chronicler** | `chronicler` | Haiku | the ledger and its reports | project work |
| **Hestia, the Housekeeper** | `housekeeper` | Sonnet | finds clutter, moves it to a dated `_recycle` folder with a manifest; lists running tools | delete anything |
| **Dionysus, the Fool** | `muse` | Sonnet | three wild ideas per brief (odd, ambitious, crazy) | act on them |
| **Metis, the Treasurer** | `treasurer` | Sonnet | efficiency audits from the ledger and over-budget transcripts | stop anyone mid-job |

**If the top tier is scarce** (plan limit, budget), change `model: fable` to `model: opus` in `agents/checker.md`. The checker stays a separate, read-only reviewer, just on a lower tier; note the tier on each verdict. We ran this way for part of one week.

## The rules that keep it from collapsing

Most multi-agent setups stall the same way: nobody in charge, nobody checking, cheap bots doing things nobody can undo.

1. **Check by stakes.** Trivial read-only chores are glanced at by the manager. Anything that goes public, into a build, to a store, or is reported as "done" goes through the checker first. A FIX-NEEDED goes back to the same worker, then is re-checked once.
2. **Irreversible steps are human-only.** Publishing, submitting, buying, sending, deleting, pushing, store and account changes are done only by the manager, and only with your explicit OK. A check after the fact cannot undo them.
3. **Final screens are human-only.** On the last confirmation page of a store, bank or publishing service, the agent touches nothing, not even to open a panel, so there is never doubt about who confirmed.
4. **Tools stay dormant.** Servers, models, editors and watchers are not started unless the job needs them; whoever starts one stops it. At the end of the day the housekeeper lists what is still running.
5. **Two failures mean switch.** Two failed rounds on the same defect: change the tool or the tier, do not try a third time the same way. Every brief carries a budget ("at 70%, stop and report").

## Real-world example (generic)

A solo game studio used this setup to ship a mobile game update over a weekend, on Android and iOS, with one human in the loop. Counting by hand from the first three days of its ledger:

- About **57 logged jobs** in three days: builds, store-listing and website drafts, art and audio passes, research, clean-ups, media cuts.
- **12 jobs went through the checker with a PASS**, and **5 jobs drew at least one FIX-NEEDED** (8 FIX-NEEDED verdicts in total). Catches included confidential wording in a draft public text, a build number the store would have rejected, a draft that contradicted the real product, and image faults.
- **Rework rounds the human had to request: low, mostly 0 or 1 per job.** The heaviest cases were creative (an image redo needed two). The ledger counts a checker's FIX-NEEDED as rework too, so the numbers cannot hide behind the human's patience.
- A baseline script (`tools/measure_sessions.py`) compares sessions before and after adoption: tokens per user turn, rework turns, tool errors, delegated runs.

These are one team's numbers over a short window. Treat them as an example of what the ledger shows, not as a benchmark. The honest result so far is "fewer defects reach the human, and every claim has evidence", not a proven saving.

## Quick start

1. Copy into your Claude Code user folder (`~/.claude/` on macOS and Linux, `C:\Users\<you>\.claude\` on Windows):

   ```
   agents/*.md                    -> ~/.claude/agents/
   skills/agentic-government      -> ~/.claude/skills/
   ```
2. Copy `ledger-template.md` somewhere you keep notes. The manager appends one line per job; Clio turns it into reports.
3. Start a new Claude Code session and say **"use the government"** (or run `/agentic-government`) on any multi-part job.
4. Optional, read-only baseline of your own sessions: `python tools/measure_sessions.py --help`.

If your plan lacks a model, change the `model:` line in that agent file.

## When not to use it

A quick question or a one-file edit: just ask normally. Delegation has overhead and pays off on jobs with several independent pieces or long chores.

## What is inside

- `skills/agentic-government/SKILL.md` — the manager's playbook: tiers, how to run a job, when not to delegate, the efficiency rules
- `agents/` — the eight worker files (runner, researcher, builder, checker, chronicler, housekeeper, muse, treasurer)
- `ledger-template.md` — the ledger columns
- `tools/measure_sessions.py` — read-only session metrics (numbers only, no message text)

## Licence

MIT. See [LICENSE](LICENSE).

By Aleksandre Glonti · Nomad Devs (nomaddevs.club)
