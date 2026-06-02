#!/usr/bin/env python3
"""Detect, read, and bump the project version across common formats.

Usage:
    detect_version.py detect            # print JSON: {file, format, version} or {file: null}
    detect_version.py bump <level>      # level: major|minor|patch -> writes new version, prints JSON

Supported sources, in priority order:
    1. pyproject.toml      [project].version  (PEP 621) or [tool.poetry].version
    2. package.json        "version"
    3. Cargo.toml          [package].version
    4. VERSION             whole-file plain text (e.g. "1.2.3")
    5. <pkg>/__init__.py   __version__ = "x.y.z"  (only if already present)

Exit codes: 0 ok, 2 no version source found, 3 usage/parse error.
"""
import json
import re
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _toml_get(path: Path, *key_paths):
    """Return (value, dotted-key) for the first key path that exists, else (None, None)."""
    if tomllib is None:
        return None, None
    try:
        data = tomllib.loads(_read(path))
    except Exception:
        return None, None
    for kp in key_paths:
        cur = data
        ok = True
        for part in kp.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and isinstance(cur, str):
            return cur, kp
    return None, None


def detect():
    root = Path.cwd()

    py = root / "pyproject.toml"
    if py.exists():
        v, kp = _toml_get(py, "project.version", "tool.poetry.version")
        if v:
            return {"file": "pyproject.toml", "format": "toml", "key": kp, "version": v}

    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(_read(pkg))
            if isinstance(data.get("version"), str):
                return {"file": "package.json", "format": "json", "key": "version",
                        "version": data["version"]}
        except Exception:
            pass

    cargo = root / "Cargo.toml"
    if cargo.exists():
        v, kp = _toml_get(cargo, "package.version")
        if v:
            return {"file": "Cargo.toml", "format": "toml", "key": kp, "version": v}

    vf = root / "VERSION"
    if vf.exists():
        txt = _read(vf).strip()
        if txt:
            return {"file": "VERSION", "format": "plain", "key": None, "version": txt}

    # __version__ in any top-level package __init__.py (only if already present)
    for init in sorted(root.glob("*/__init__.py")) + sorted(root.glob("src/*/__init__.py")):
        m = re.search(r"""__version__\s*=\s*["']([^"']+)["']""", _read(init))
        if m:
            return {"file": str(init.relative_to(root)).replace("\\", "/"),
                    "format": "python", "key": "__version__", "version": m.group(1)}

    return {"file": None}


def _bump_semver(version: str, level: str) -> str:
    m = SEMVER_RE.match(version)
    if not m:
        raise ValueError(f"version '{version}' is not plain semver (x.y.z) — bump manually")
    major, minor, patch = (int(m.group(i)) for i in (1, 2, 3))
    if level == "major":
        major, minor, patch = major + 1, 0, 0
    elif level == "minor":
        minor, patch = minor + 1, 0
    elif level == "patch":
        patch += 1
    else:
        raise ValueError(f"unknown level '{level}' (use major|minor|patch)")
    return f"{major}.{minor}.{patch}"


def _write(info: dict, old: str, new: str):
    path = Path.cwd() / info["file"]
    text = _read(path)
    fmt = info["format"]
    if fmt == "plain":
        path.write_text(new + "\n", encoding="utf-8")
        return
    if fmt == "json":
        # Replace only the version string value, preserve formatting.
        new_text = re.sub(r'("version"\s*:\s*")' + re.escape(old) + r'(")',
                          r"\g<1>" + new + r"\g<2>", text, count=1)
        path.write_text(new_text, encoding="utf-8")
        return
    if fmt in ("toml", "python"):
        # Replace the first exact occurrence of the old version string.
        new_text = text.replace(f'"{old}"', f'"{new}"', 1)
        if new_text == text:
            new_text = text.replace(f"'{old}'", f"'{new}'", 1)
        if new_text == text:
            raise ValueError(f"could not locate version string '{old}' in {info['file']}")
        path.write_text(new_text, encoding="utf-8")
        return
    raise ValueError(f"unsupported format '{fmt}'")


def main(argv):
    if len(argv) < 2 or argv[1] not in ("detect", "bump"):
        print(__doc__, file=sys.stderr)
        return 3

    if argv[1] == "detect":
        info = detect()
        print(json.dumps(info))
        return 0 if info.get("file") else 2

    # bump
    if len(argv) < 3:
        print("bump requires a level: major|minor|patch", file=sys.stderr)
        return 3
    info = detect()
    if not info.get("file"):
        print(json.dumps({"file": None}))
        return 2
    old = info["version"]
    try:
        new = _bump_semver(old, argv[2])
        _write(info, old, new)
    except ValueError as e:
        print(json.dumps({"error": str(e), "file": info["file"], "version": old}))
        return 3
    print(json.dumps({"file": info["file"], "old": old, "new": new}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
