"""Deploy the DEV remote script into Ableton's MIDI Remote Scripts directory.

Cross-platform port of the old `make install_script` (Windows PowerShell). Copies
the Protocol_0 template into Ableton, then rewrites the DEV loader's
__P0_SOURCE_DIR__ placeholder to this checkout's src/script path, so Ableton loads
protocol0/ live from the repo (edits picked up without reinstalling).

stdlib-only — see _pyfind for why.
"""
import shutil
import sys
from pathlib import Path

from _pyfind import (
    REPO_ROOT,
    ableton_remote_scripts_dir,
    ableton_remote_scripts_dirs,
)

PLACEHOLDER = "__P0_SOURCE_DIR__"


def _deploy(template, script_root, scripts_dir):
    """Copy the DEV template into one Live install and wire it to this checkout."""
    dest = scripts_dir / "Protocol_0"
    shutil.copytree(template, dest, dirs_exist_ok=True)

    # Rewrite the DEV loader to point at this checkout (raw-string-safe on both
    # OSes: a Windows path has backslashes, a mac path doesn't — both fine).
    init_py = dest / "__init__.py"
    text = init_py.read_text(encoding="utf-8")
    init_py.write_text(text.replace(PLACEHOLDER, str(script_root)),
                       encoding="utf-8")
    return dest


def main():
    script_root = REPO_ROOT / "src" / "script"
    template = script_root / "script_templates" / "Protocol_0"
    if not template.is_dir():
        raise SystemExit("Remote-script template not found: %s" % template)

    # Deploy into *every* detected Live install (stable + Beta) so all of them
    # load live from this checkout. Fall back to the single default dir on a
    # fresh box where no Live is installed yet.
    targets = ableton_remote_scripts_dirs() or [ableton_remote_scripts_dir()]
    for scripts_dir in targets:
        dest = _deploy(template, script_root, scripts_dir)
        print("Protocol 0 installed -> %s" % dest)


if __name__ == "__main__":
    sys.exit(main())
