# Spec-driven workflow

Before any dev task, read `docs/specs/in-progress/` for current context.

To start a new feature, pick a spec from `docs/specs/todo/` and move it to
`docs/specs/in-progress/` with `git mv`. When the work is merged, move it to
`docs/specs/done/`.

See `docs/specs/README.md` for the full lifecycle.

# Releases

Bumper et releaser sont deux actes séparés :

- **Bump** — `/commit` bumpe `VERSION` à chaque changement fonctionnel, commit et push.
  Il ne tague **jamais**.
- **Release** — `/release` (skill repo, `.claude/skills/release/`) tague la version courante
  (`v<version>`) et pousse le tag. Ce push déclenche `.github/workflows/release.yml`, qui build
  l'installeur sur un runner Windows (via `scripts/build_installer.ps1`) et publie une GitHub
  Release contenant `Protocol0-Setup-<version>.exe` (notes tirées du message du tag annoté).

Concrètement : on `/commit` plusieurs fois (la version monte), puis quand on veut publier, on dit
« release » → `/release` crée le tag et la CI fait le reste. Le « Check for updates » du Jalon 2
et la future landing page « one-click download » consomment `releases/latest` de cette même release.
