"""Mini .env reader (stdlib only).

Reads the monorepo-root .env. Works in both layouts:
- dev: this file is at p0_script/protocol0/shared/env.py, root is 3 dirnames up
- deployed: same path, because the deployed script imports from P0_SOURCE_DIR
  (rewritten at install time to point at the repo) — see script_templates/p0/__init__.py.
"""
import os

_CACHE = None


def load_env():
    # type: () -> dict
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    here = os.path.dirname(os.path.abspath(__file__))
    # here -> <repo>/p0_script/protocol0/shared
    # parents: shared -> protocol0 -> p0_script -> <repo>
    root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    path = os.path.join(root, ".env")
    _CACHE = _parse(path) if os.path.isfile(path) else {}
    return _CACHE


def get(key, default=None):
    # type: (str, str) -> str
    return load_env().get(key, os.environ.get(key, default))


def _parse(path):
    # type: (str) -> dict
    out = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out
