"""One-command local dev setup, cross-platform (Windows + macOS).

Sets up the remote script's poetry env (lint/test tooling — flake8, vulture,
pytest; the script itself is stdlib-only) and deploys the remote script into
Ableton. The agent is Rust (`make agent` builds it with cargo) and needs no
poetry. After this, `make agent` is all you need.

Prerequisites the dev installs once (this script checks, it does not install them):
  - make, poetry, and a Python >= 3.11.

stdlib-only — see _pyfind for why.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import install_remote_script
from _pyfind import REPO_ROOT, find_python311

# The remote script gets a poetry env for its dev tooling (lint/test). The agent
# is Rust now (built with cargo), so it needs no poetry env of its own.
POETRY_PROJECTS = ["src/remote-script"]


def _require_poetry():
    if shutil.which("poetry") is None:
        raise SystemExit(
            "poetry not found on PATH.\n"
            "Install it once (isolated env recommended): pipx install poetry\n"
            "  (or see https://python-poetry.org/docs/#installation)"
        )


def _run(cmd, cwd):
    print("+ (%s) %s" % (cwd, " ".join(cmd)))
    subprocess.run(cmd, cwd=cwd, check=True)


def main():
    _require_poetry()
    python = find_python311()
    print("Using Python: %s" % python)

    for rel in POETRY_PROJECTS:
        project = REPO_ROOT / rel
        _run(["poetry", "env", "use", python], cwd=project)
        _run(["poetry", "install"], cwd=project)

    install_remote_script.main()
    print("Bootstrap complete - run 'make agent' to start.")


if __name__ == "__main__":
    sys.exit(main())
