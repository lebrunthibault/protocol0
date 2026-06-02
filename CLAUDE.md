# Spec-driven workflow

Before any dev task, read `docs/specs/in-progress/` for current context.

To start a new feature, pick a spec from `docs/specs/todo/` and move it to
`docs/specs/in-progress/` with `git mv`. When the work is merged, move it to
`docs/specs/done/`.

See `docs/specs/README.md` for the full lifecycle.

# Releases

Bumping and releasing are two separate acts:

- **Bump** — `/commit` (repo skill, `.claude/skills/commit/`) bumps `VERSION` on every
  functional change, commits and pushes. It **never** tags.
- **Release** — `/release` (repo skill, `.claude/skills/release/`) tags the current version
  (`v<version>`) and pushes the tag. That push triggers `.github/workflows/release.yml`, which
  builds the installer on a Windows runner (via `scripts/windows/build_installer.ps1`) and publishes a
  GitHub Release containing `Protocol0-Setup-<version>.exe` (notes taken from the annotated tag
  message).

In practice: you `/commit` several times (the version climbs), then when you want to publish you
say "release" → `/release` creates the tag and CI does the rest. The "Check for updates" of
Milestone 2 and the future "one-click download" landing page both consume `releases/latest` of
that same release.
