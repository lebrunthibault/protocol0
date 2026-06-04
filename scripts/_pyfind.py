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


# Major Ableton Live version Protocol 0 supports. Detection only matches
# "Live <this>*" installs. Bump when moving to a new Live (e.g. "13").
# Keep in sync with installer/protocol0.iss SupportedLiveVersion.
SUPPORTED_LIVE_VERSION = "12"


def _pick_remote_scripts_dir(roots_glob, suffix):
    """The 'MIDI Remote Scripts' dir among supported-version installs, or None.

    roots_glob yields candidate install roots already filtered to the supported
    Live version (e.g. 'Live 12 *' folders or 'Ableton Live 12 *.app' bundles);
    suffix is appended to each to reach the remote scripts folder. Edition-agnostic
    (Intro / Standard / Suite). When both a stable and a Beta build are present, the
    Beta is preferred (mirrors the installer).
    """
    stable = None
    beta = None
    for root in roots_glob:
        candidate = root / suffix
        if not candidate.is_dir():
            continue
        if "beta" in root.name.lower():
            beta = candidate
        else:
            stable = candidate
    return beta or stable


def ableton_remote_scripts_dir():
    """The Ableton 'MIDI Remote Scripts' directory for the current OS.

    Detects the installed supported Live version (SUPPORTED_LIVE_VERSION, any
    edition: Intro / Standard / Suite), mirroring the installer's auto-detect;
    prefers a Beta build when present. Falls back to '<version> Suite' when
    nothing is found, so bootstrap on a fresh box still has a sensible default.
    """
    if sys.platform == "win32":
        ableton_root = Path(r"C:\ProgramData\Ableton")
        found = _pick_remote_scripts_dir(
            ableton_root.glob("Live %s*" % SUPPORTED_LIVE_VERSION),
            Path("Resources") / "MIDI Remote Scripts",
        )
        return found or (ableton_root / ("Live %s Suite" % SUPPORTED_LIVE_VERSION)
                         / "Resources" / "MIDI Remote Scripts")
    if sys.platform == "darwin":
        apps = Path("/Applications")
        found = _pick_remote_scripts_dir(
            apps.glob("Ableton Live %s*.app" % SUPPORTED_LIVE_VERSION),
            Path("Contents") / "App-Resources" / "MIDI Remote Scripts",
        )
        return found or (apps / ("Ableton Live %s Suite.app" % SUPPORTED_LIVE_VERSION)
                         / "Contents" / "App-Resources" / "MIDI Remote Scripts")
    raise SystemExit(
        "Unsupported platform %r: the remote-script install targets Windows or "
        "macOS Ableton only." % sys.platform
    )
