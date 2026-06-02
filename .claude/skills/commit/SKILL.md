---
name: commit
description: Bump the project version, commit, and push in a clean OSS-friendly way, auto-detecting the version file across languages. Use when the user asks to "commit", "bump version", "push a version", or finishes a feature and wants it committed. Does NOT tag or publish a release — bumping and releasing are separate; if the user asks to "release"/"ship"/"publish a version", that's a release flow, not this skill. Do NOT use for plain `git commit` of work-in-progress with no intent to version or push.
allowed-tools: "Bash(git:*) Bash(python:*) Read Edit Write"
metadata:
  author: lebrunthibault
  version: 1.2.0
---

# Commit

The **bump → commit → push** flow, language-agnostic. You already know how to stage, write a clean
conventional-commit message, and push — this skill adds the three things that aren't obvious:
the concurrency guard, the deterministic version bump, and the push guardrails.

## 1. Guard against a concurrent commit

Before staging, check no other commit (another agent or terminal) is mid-write. Git's own lock
files are the signal — `index.lock` exists while staging/committing and is removed when done.

```bash
ls "$(git rev-parse --git-dir)"/index.lock "$(git rev-parse --git-dir)"/HEAD.lock 2>/dev/null
```

If a lock exists: **stop**, don't commit, don't delete it. Tell the user. (If it's clearly stale —
old timestamp, no running git — ask before removing.) Best-effort, not a hard mutex: if git itself
errors `Unable to create '.../index.lock': File exists`, treat it the same way.

## 2. Decide the bump, then apply it

Bump the version **only when the change affects what the software does or exposes** (new feature,
behavior change/removal, observable bug fix). Skip the bump for docs, tests, formatting, internal
refactors, CI/deps with no user-facing effect. Mixed change → the feature wins.

```bash
python scripts/detect_version.py detect          # current version + source file
python scripts/detect_version.py bump <major|minor|patch>
```

- **major** breaking · **minor** new feature · **patch** bug fix.
- Confirm the bump with the user (old → new, which file) before writing.
- `{"file": null}` → no version source. Offer to create a top-level `VERSION` file (plain `0.1.0`),
  then bump against it. See [references/version-files.md](references/version-files.md).
- `error` about non-semver (e.g. `2.0.0rc1`) → don't force it; ask for the target and edit by hand.

## 3. Commit & push

The version-file change goes in the **same commit** as the work. Conventional-commit subject
(`feat:`/`fix:`/`docs:`…), imperative, why in the body. Let hooks run — never `--no-verify`.

**This skill never tags or `git push --tags`** — that's the release flow's job (tagging on a `v*`
that CI releases from would publish on every bump). Push the commit only.

Push guardrails:

- Never `git push --force`/`--force-with-lease` unless the user explicitly asks.
- Pushing straight to `main`/`master` → mention it so the user can object.
- Never push secrets — if `git status` showed `.env`, keys, creds: stop and confirm.

## Notes

Version logic is delegated to `scripts/detect_version.py` (priority order + formats live there and
in [references/version-files.md](references/version-files.md)) so it's deterministic across runs.
