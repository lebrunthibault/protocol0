"""Deploy the DEV remote script into Ableton's MIDI Remote Scripts directory.

Cross-platform port of the old `make install_script` (Windows PowerShell). Copies
the Protocol_0 template into Ableton, then rewrites the DEV loader's
__P0_SOURCE_DIR__ placeholder to this checkout's src/remote-script path, so Ableton loads
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


# Residue a prod install (installer / Live-updater migration) leaves in Protocol_0/:
# the frozen bundled package and its metadata. A dev deployment must not keep them
# around — the frozen protocol0/ is dead weight and VERSION lies about what runs.
_PROD_RESIDUE = ("protocol0", "__pycache__", "VERSION")


def _deploy(template, script_root, scripts_dir):
    """Copy the DEV template into one Live install and wire it to this checkout."""
    dest = scripts_dir / "Protocol_0"
    shutil.copytree(template, dest, dirs_exist_ok=True)

    # Mirror image of the installer's [InstallDelete] (which wipes dev residue
    # before a prod install): purge prod residue so only the dev loader remains.
    for name in _PROD_RESIDUE:
        residue = dest / name
        if residue.is_dir():
            shutil.rmtree(residue)
        elif residue.exists():
            residue.unlink()

    # Rewrite the DEV loader to point at this checkout (raw-string-safe on both
    # OSes: a Windows path has backslashes, a mac path doesn't — both fine).
    init_py = dest / "__init__.py"
    text = init_py.read_text(encoding="utf-8")
    init_py.write_text(text.replace(PLACEHOLDER, str(script_root)),
                       encoding="utf-8")
    return dest


def _user_library_remote_scripts():
    """Default 'User Library/Remote Scripts' location for the current OS."""
    if sys.platform == "win32":
        base = Path.home() / "Documents"
    else:
        base = Path.home() / "Music"
    return base / "Ableton" / "User Library" / "Remote Scripts"


def _remove_user_library_duplicate():
    """Remove a stray Protocol_0 from the User Library, if any.

    Live also scans 'User Library/Remote Scripts' for control surfaces; a
    Protocol_0 copy there (e.g. left by an old installer) can shadow the dev
    deployment with a frozen bundle — edits then silently never reach Ableton.
    One canonical location only: the per-install MIDI Remote Scripts dirs.
    """
    stray = _user_library_remote_scripts() / "Protocol_0"
    if stray.is_dir():
        shutil.rmtree(stray)
        print("Removed stale duplicate (was shadowing the dev script): %s" % stray)


def main():
    script_root = REPO_ROOT / "src" / "remote-script"
    template = script_root / "script_templates" / "Protocol_0"
    if not template.is_dir():
        raise SystemExit("Remote-script template not found: %s" % template)

    _remove_user_library_duplicate()

    # Deploy into *every* detected Live install (stable + Beta) so all of them
    # load live from this checkout. Fall back to the single default dir on a
    # fresh box where no Live is installed yet.
    targets = ableton_remote_scripts_dirs() or [ableton_remote_scripts_dir()]
    for scripts_dir in targets:
        dest = _deploy(template, script_root, scripts_dir)
        print("Protocol 0 installed -> %s" % dest)


if __name__ == "__main__":
    sys.exit(main())
