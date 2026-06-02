"""Shared, dependency-free helpers for the cross-platform dev tooling.

stdlib-only on purpose: these run *before* any poetry env exists (at bootstrap
time) and in CI, so they cannot import third-party packages.
"""
import subprocess
import sys
from pathlib import Path

# Repo root = parent of this scripts/ directory.
REPO_ROOT = Path(__file__).resolve().parent.parent

MIN_VERSION = (3, 11)


def _candidates():
    """Interpreter commands to probe, best-first, per platform.

    On Windows the `py` launcher is the reliable way to target a specific
    version; elsewhere we try the versioned `python3.x` names then fall back.
    """
    if sys.platform == "win32":
        return [["py", "-3.11"], ["py", "-3"], ["python"], ["python3"]]
    return [
        ["python3.11"], ["python3.12"], ["python3.13"], ["python3.14"],
        ["python3"], ["python"],
    ]


def find_python311():
    """Absolute path to an interpreter >= 3.11, or raise with guidance.

    The probed command may be multi-token (e.g. `py -3.11`); we resolve it to a
    concrete `sys.executable` path so `poetry env use` is unambiguous.
    """
    probed = []
    for cmd in _candidates():
        probed.append(" ".join(cmd))
        ver = _probe_version_cmd(cmd)
        if ver and ver >= MIN_VERSION:
            return _resolve_abs_cmd(cmd)
    raise SystemExit(
        "No Python >= %d.%d found (probed: %s).\n"
        "Install Python 3.11+ (on Windows the `py` launcher should then resolve it)."
        % (MIN_VERSION[0], MIN_VERSION[1], ", ".join(probed))
    )


def _probe_version_cmd(cmd):
    try:
        out = subprocess.run(
            cmd + ["-c", "import sys;print('%d.%d' % sys.version_info[:2])"],
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    try:
        major, minor = (int(p) for p in out.stdout.strip().split("."))
    except ValueError:
        return None
    return (major, minor)


def _resolve_abs_cmd(cmd):
    out = subprocess.run(
        cmd + ["-c", "import sys;print(sys.executable)"],
        capture_output=True, text=True, timeout=15,
    )
    return out.stdout.strip()


def ableton_remote_scripts_dir():
    """The Ableton 'MIDI Remote Scripts' directory for the current OS.

    Hardcodes 'Live 12 Suite' to match the project's supported edition (same
    assumption the installer's auto-detect starts from).
    """
    if sys.platform == "win32":
        return Path(r"C:\ProgramData\Ableton\Live 12 Suite"
                    r"\Resources\MIDI Remote Scripts")
    if sys.platform == "darwin":
        return Path("/Applications/Ableton Live 12 Suite.app"
                    "/Contents/App-Resources/MIDI Remote Scripts")
    raise SystemExit(
        "Unsupported platform %r: the remote-script install targets Windows or "
        "macOS Ableton only." % sys.platform
    )
