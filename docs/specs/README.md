# Spec-driven development

Specs are short Markdown documents describing a unit of work — a feature,
refactor, or investigation — written before implementation. Each spec lives
in exactly one directory at any time; the directory it sits in **is** its
status.

## Lifecycle

```
backlog/  →  todo/  →  in-progress/  →  done/
```

- **backlog/** — ideas and future specs, not yet prioritized. May be rough or
  incomplete. Safe to ignore when picking work.
- **todo/** — prioritized and ready to be implemented. A spec here should
  have enough detail that someone can start without further clarification.
- **in-progress/** — currently being implemented. There should be at most
  one or two specs here at a time per contributor.
- **done/** — implementation merged. Kept for historical context and to
  trace decisions back to the spec that motivated them.

## Transitioning a spec

Move with `git mv` so history is preserved:

```sh
git mv docs/specs/<from>/<spec>.md docs/specs/<to>/
```

For example, to start work on a todo spec:

```sh
git mv docs/specs/todo/2026-05-17-backend-as-background-service.md docs/specs/in-progress/
```

## Naming convention

`YYYY-MM-DD-kebab-case-title.md` where the date is when the spec was first
written (not when it was promoted between directories). Examples:

- `2026-05-17-backend-as-background-service.md`
- `2026-06-02-replace-loopmidi-with-rtpmidi.md`

## Before starting any task

1. Read everything under `docs/specs/in-progress/` for current context.
2. Then check `docs/specs/todo/` to see what's queued next.

These directories are the source of truth for "what is being worked on" and
"what is planned" — prefer them over chat history or memory.
