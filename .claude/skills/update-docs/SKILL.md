---
name: update-docs
description: Update the project's human-facing documentation — CONSTITUTION.md (the vision and durable design intent) and README.md (the developer-facing entry point) — so they reflect the current, true state of the project. Use when the user says "mets à jour la doc", "update the docs", "regénère le README/la constitution", or after work lands and the docs have drifted.
---

# update-docs

Keep the project's two human-facing documents truthful and current:

- **`CONSTITUTION.md`** — the **vision** and the durable **design intent / key
  decisions**. The long-term *what* and *why*, not the *how* of any iteration.
- **`README.md`** — the **developer-facing** entry point: what the project is, how
  to install and run it, and where to go next.

This skill is intentionally **generic**. The project will evolve — features,
structure, even its core purpose may change — so do **not** assume any particular
shape here. Re-derive everything from the repository each run, and let the docs
follow what you find.

## How to update the docs

1. **Re-derive the truth, every run.** Never trust a previous version of a doc as
   ground truth — it may be stale. Read the project's own sources of truth:
   - the planning/spec material the project keeps (e.g. `docs/specs/` and its
     lifecycle README, if present) — for what's planned, in progress, and done;
   - recent **git history** — for what actually shipped;
   - the build/run/release entry points (Makefiles, installers, CI workflows,
     version files) — so install and usage instructions are accurate;
   - the current `CONSTITUTION.md` and `README.md` — to preserve good wording and
     the intent already captured.

   If the project's purpose or architecture has clearly moved on from what the
   docs say, update the docs to match reality — that's the point.

2. **Rewrite `CONSTITUTION.md`** to capture the vision and the durable decisions
   that still hold, with the reasoning behind them. Keep it aligned with the
   planning material and git history, and preserve its framing as the source of
   truth for *intent* (when an implementation invalidates a decision, the doc gets
   updated). Let the section structure follow the project as it is now rather than
   a fixed template.

   If a roadmap or "what's next" section is warranted, **point to the planning
   material rather than restating it** — e.g. link `docs/specs/todo/` and
   `docs/specs/backlog/`. Don't list individual specs or features in the doc; that
   only drifts out of sync with the directories.

3. **Rewrite `README.md`** for a developer arriving at the repo: a short pitch of
   what the project is, how to install and run it, a quick orientation to its
   architecture, and pointers onward (e.g. to `CONSTITUTION.md` and the planning
   material). Keep it terse.

4. **Consistency pass.** Make sure the two docs agree with each other and with the
   code — versions, ports, paths, commands, and any roadmap/status claims should
   all match what's actually in the repo and its history.

## Guardrails

- **Written for humans, in English, and readable.** Favor clarity over
  exhaustiveness.
- **Stay high-level.** Describe decisions and their rationale, not low-level
  implementation mechanics — keep the *why* and drop details that belong in code
  comments or specs (for example, name a runtime constraint without dissecting its
  internals).
- **Honest, not aspirational.** No badges, shields, or maturity claims the project
  hasn't earned.
- **Generic by design.** Don't hardcode the project's current features, file
  layout, or section names into this skill — derive them from the repo so the docs
  keep working as the project changes.
