"""Coverage gates of the action catalog.

Reads docs/lom/lom-inventory.json + catalog-map.json and the ableton-mcp
checklist from scripts/lom_catalog/coverage.py, and enforces:
- every checklist command is exposed or explicitly waived;
- every op id used in the map exists in the inventory (typo guard);
- every action referenced by the map is a registered route (and stays one).
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DOCS_LOM = REPO_ROOT / "docs" / "lom"


def _lom_coverage():
    """Late import: the scripts dir goes at the END of sys.path (never shadow
    an installed package with a script named like one, e.g. coverage)."""
    sys.path.append(str(REPO_ROOT / "scripts" / "lom_catalog"))
    import coverage as lom_coverage

    return lom_coverage


def _load():
    inventory = json.loads((DOCS_LOM / "lom-inventory.json").read_text(encoding="utf-8"))
    catalog_map = json.loads((DOCS_LOM / "catalog-map.json").read_text(encoding="utf-8"))
    return inventory, catalog_map["ops"]


def test_ableton_mcp_checklist_fully_covered():
    _, ops = _load()
    exposed = {op_id for op_id, op in ops.items() if op["status"] == "exposed"}

    uncovered = [
        name
        for name, item in _lom_coverage().CHECKLIST.items()
        if "waived" not in item and not set(item["ops"]) <= exposed
    ]
    assert uncovered == [], "ableton-mcp commands not covered: %s" % uncovered


def test_catalog_map_op_ids_exist_in_the_inventory():
    inventory, ops = _load()
    known = set()
    for class_key, content in inventory["classes"].items():
        for member in content["properties"] + content["methods"]:
            known.add("%s.%s" % (class_key, member["name"]))

    unknown = sorted(set(ops) - known)
    assert unknown == [], "unknown op ids in catalog-map.json (typo?): %s" % unknown


def test_every_mapped_action_is_a_registered_route(p0):
    from protocol0.application.http.Router import get_routes

    registered = {
        path.replace("/api/action/", "")
        for (method, path) in get_routes()
        if path.startswith("/api/action/")
    }

    _, ops = _load()
    mapped_actions = set()
    for op in ops.values():
        for action_name in op.get("action", "").split(","):
            if action_name.strip():
                mapped_actions.add(action_name.strip())

    missing = sorted(mapped_actions - registered)
    assert missing == [], "catalog-map references unregistered actions: %s" % missing
