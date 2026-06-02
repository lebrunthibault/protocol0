# Version files — detection & the OSS-friendly default

How `scripts/detect_version.py` finds and bumps the project version, and what to do when nothing
exists.

## Detection priority order

The script checks these in order and uses the **first** that yields a version:

| # | File | Where the version lives |
|---|------|-------------------------|
| 1 | `pyproject.toml` | `[project].version` (PEP 621) or `[tool.poetry].version` |
| 2 | `package.json` | top-level `"version"` |
| 3 | `Cargo.toml` | `[package].version` |
| 4 | `VERSION` | the whole file, plain text (e.g. `1.2.3`) |
| 5 | `<pkg>/__init__.py` or `src/<pkg>/__init__.py` | `__version__ = "x.y.z"` (only if already present) |

It only edits a single, highest-priority source. If two sources disagree, that's a project smell —
surface it to the user rather than silently bumping one.

## The OSS-friendly default: a top-level `VERSION` file

When no version source exists, the cleanest cross-language choice is a plain `VERSION` file at the
repo root:

```
0.1.0
```

Why this is a good default:

- **Language-agnostic** — works whether or not the project is Python/JS/Rust.
- **Discoverable** — a human or a CI script can `cat VERSION` with zero parsing.
- **Single source of truth** — avoids the "which file holds the real version?" ambiguity.
- **Tooling-friendly** — most release tools can read a plain VERSION file.

Start at `0.1.0` for a pre-1.0 project (semver convention: anything `0.x` signals "API may change").

### Wiring it into a Python project (optional)

If the project is a Python package and you want `import pkg; pkg.__version__` to work while keeping
`VERSION` as the source of truth, read it at runtime instead of duplicating the string:

```python
# pkg/__init__.py
from pathlib import Path
__version__ = (Path(__file__).resolve().parent.parent / "VERSION").read_text().strip()
```

Only suggest this if the user wants programmatic access — for many repos the plain file is enough.

## Semver reminder

The bump logic expects plain semver `MAJOR.MINOR.PATCH`:

- **major** — incompatible/breaking change or removal
- **minor** — new backward-compatible functionality
- **patch** — backward-compatible bug fix

Pre-release/build metadata (`1.2.0rc1`, `1.2.0+build5`) is detected but **not** auto-bumped — the
script returns an error and asks for a manual target, because incrementing a pre-release is
project-specific.
