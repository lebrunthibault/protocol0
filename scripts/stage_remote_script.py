"""Prepare build/stage/Protocol_0/ ready to copy into MIDI Remote Scripts.

Cross-platform port of stage_remote_script.ps1. Pure file copy (the remote script
is stdlib-only, so no poetry install / vendoring). Output consumed by
installer/protocol0.iss:

    build/stage/Protocol_0/
      ├─ __init__.py        (= __init__.prod.py, the prod loader)
      ├─ protocol0/         (the source package, without __pycache__ / tests)
      └─ VERSION

stdlib-only — see _pyfind for why.
"""
import shutil
import sys
from pathlib import Path

from _pyfind import REPO_ROOT


def main():
    script_src = REPO_ROOT / "src" / "script" / "protocol0"
    prod_init = (REPO_ROOT / "src" / "script" / "script_templates"
                 / "Protocol_0" / "__init__.prod.py")
    version_file = REPO_ROOT / "VERSION"
    stage_root = REPO_ROOT / "build" / "stage" / "Protocol_0"

    if not script_src.is_dir():
        raise SystemExit("Source package not found: %s" % script_src)
    if not prod_init.is_file():
        raise SystemExit("Prod loader not found: %s" % prod_init)
    if not version_file.is_file():
        raise SystemExit("VERSION file not found: %s" % version_file)

    # Start from a clean stage dir.
    if stage_root.exists():
        shutil.rmtree(stage_root)
    stage_root.mkdir(parents=True)

    # Copy protocol0/, dropping what must not ship.
    shutil.copytree(
        script_src, stage_root / "protocol0",
        ignore=shutil.ignore_patterns("__pycache__", "tests"),
    )

    # Drop the prod loader as __init__.py.
    shutil.copyfile(prod_init, stage_root / "__init__.py")

    # VERSION at the bundle root: in prod the script has no repo tree nor
    # _MEIPASS, so protocol0/version.py walks up from __file__ and finds this
    # VERSION inside Protocol_0/. Without it the version falls back to "0.0.0".
    shutil.copyfile(version_file, stage_root / "VERSION")

    print("OK -> %s" % stage_root)


if __name__ == "__main__":
    sys.exit(main())
