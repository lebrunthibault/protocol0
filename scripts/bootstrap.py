"""One-command local dev setup, cross-platform (Windows + macOS).

Sets up both poetry envs (remote script + detector) and deploys the remote script
into Ableton. After this, `make detector` is all you need.

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

# Projects that each get their own poetry env.
POETRY_PROJECTS = ["src/script", "src/detector"]


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
    print("Bootstrap complete - run 'make detector' to start.")


if __name__ == "__main__":
    sys.exit(main())
