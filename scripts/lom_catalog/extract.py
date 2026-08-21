"""Extracts a machine-readable inventory of the Live 12 LOM from the wiki reference.

Source: the scraped `Live.*.runtime.md` files (one per Live module, regular
Markdown: `### class X(Base)` / `#### Properties` bullets / `##### method`
headings with the Boost.Python signature on the first body line).

Output: docs/lom/lom-inventory.json — stable ordering, so regenerating from the
same source is byte-identical (--check relies on this). The inventory is the
raw material the action catalog is curated from (see catalog-map.json and
coverage.py); it is committed so the repo stays self-sufficient without the wiki.

Settability of properties is inferred from the Ableton docstrings ("Get/Set...",
"Const access...") plus a manual override table — the Live 12 docstrings carry
that signal directly, which beats cross-checking the Live 11 M4L XML.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

DEFAULT_SOURCE = Path(r"D:\dev\doc\wiki\raw\midi-remote-scripts\reference\live12")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "docs" / "lom" / "lom-inventory.json"

# listener triplets are mechanical per property: pure noise for a catalog
_LISTENER_RE = re.compile(r"^(add_|remove_).+_listener$|_has_listener$")

# method names that are queries, not actions (the catalog exposes actions;
# getters feed state endpoints instead)
_QUERY_PREFIXES = ("get_", "is_", "has_", "can_", "find_", "available_")
_QUERY_NAMES = {"View", "beat_to_sample_time", "sample_to_beat_time"}

# docstring patterns signalling a writable property
_SETTABLE_HINTS = ("get/set", "set the", "set access", "read, write", "enable/disable", "get and set", "get, set")

# manual overrides where the docstring wording hides the settability
_SETTABLE_OVERRIDES = {
    "Track.arm": True,
    "Track.color": True,
    "Track.color_index": True,
    "Track.current_monitoring_state": True,
    "Track.fold_state": True,
    "Track.implicit_arm": True,
    "Track.input_routing_channel": True,
    "Track.input_routing_type": True,
    "Track.is_showing_chains": True,
    "Track.mute": True,
    "Track.name": True,
    "Track.output_routing_channel": True,
    "Track.output_routing_type": True,
    "Track.playing_slot_index": False,
    "Track.solo": True,
    "Clip.color": True,
    "Clip.color_index": True,
    "Clip.name": True,
    "Scene.color": True,
    "Scene.color_index": True,
    "Scene.name": True,
    "Scene.tempo": True,
    "DeviceParameter.value": True,
    "Device.is_enabled": False,  # enabled via its on/off DeviceParameter
}

# The scrape does not include the nested View classes (no "### class View" in any
# file), yet selection and view focus are core catalog surface. Hand-maintained
# supplement, same shape as parsed entries.
_VIEW_SUPPLEMENT = {
    "Song.View": {
        "properties": [
            {"name": "detail_clip", "description": "Get/Set the clip shown in Detail/Clip view."},
            {"name": "draw_mode", "description": "Get/Set whether the draw mode is active."},
            {"name": "follow_song", "description": "Get/Set whether the arrangement follows playback."},
            {"name": "highlighted_clip_slot", "description": "Get/Set the highlighted clip slot."},
            {"name": "selected_chain", "description": "Get/Set the selected chain."},
            {"name": "selected_parameter", "description": "Const access to the selected parameter."},
            {"name": "selected_scene", "description": "Get/Set the selected scene."},
            {"name": "selected_track", "description": "Get/Set the selected track."},
        ],
        "methods": [
            {
                "name": "select_device",
                "params": [{"name": "device", "type": "Device", "optional": False}],
                "returns": "None",
                "description": "Select the given device and shows its track view.",
            }
        ],
    },
    "Track.View": {
        "properties": [
            {"name": "device_insert_mode", "description": "Get/Set where new devices are inserted."},
            {"name": "is_collapsed", "description": "Get/Set whether the track is collapsed in arrangement."},
            {"name": "selected_device", "description": "Const access to the selected device of the track."},
        ],
        "methods": [
            {
                "name": "select_instrument",
                "params": [],
                "returns": "bool",
                "description": "Selects the track instrument and shows its device chain.",
            }
        ],
    },
    "Clip.View": {
        "properties": [
            {"name": "grid_quantization", "description": "Get/Set the grid quantization of the clip view."},
            {"name": "grid_is_triplet", "description": "Get/Set whether the grid is triplet."},
        ],
        "methods": [
            {
                "name": "show_loop",
                "params": [],
                "returns": "None",
                "description": "Scrolls the clip view to the loop.",
            }
        ],
    },
    "Application.View": {
        "properties": [
            {"name": "browse_mode", "description": "Const access to whether hotswap is active."},
            {"name": "focused_document_view", "description": "Const access to the focused view name."},
        ],
        "methods": [
            {
                "name": "focus_view",
                "params": [{"name": "view", "type": "str", "optional": False}],
                "returns": "None",
                "description": "Focuses the given view.",
            },
            {
                "name": "hide_view",
                "params": [{"name": "view", "type": "str", "optional": False}],
                "returns": "None",
                "description": "Hides the given view.",
            },
            {
                "name": "is_view_visible",
                "params": [{"name": "view", "type": "str", "optional": False}],
                "returns": "bool",
                "description": "Returns whether the given view is visible.",
            },
            {
                "name": "scroll_view",
                "params": [
                    {"name": "direction", "type": "NavDirection", "optional": False},
                    {"name": "view", "type": "str", "optional": False},
                    {"name": "modifier_pressed", "type": "bool", "optional": False},
                ],
                "returns": "None",
                "description": "Scrolls the given view in the given direction.",
            },
            {
                "name": "show_view",
                "params": [{"name": "view", "type": "str", "optional": False}],
                "returns": "None",
                "description": "Shows the given view.",
            },
            {
                "name": "toggle_browse",
                "params": [],
                "returns": "None",
                "description": "Toggles hotswap mode for the selected device.",
            },
        ],
    },
}

_CLASS_RE = re.compile(r"^### class (\w+)\((\w+)\)")
_SECTION_RE = re.compile(r"^#### (\w+)")
_PROPERTY_RE = re.compile(r"^- (\w+)(?: - (.*))?$")
_METHOD_RE = re.compile(r"^##### (\w+)\(")
_SIGNATURE_RE = re.compile(r"^(\w+)\(\s*(.*?)\)\s*->\s*(\w+)\s*:?\s*(.*)$")
_PARAM_RE = re.compile(r"\((\w+)\)(\w+)(?:=([^,\]\)]+))?")


def parse_module(path: Path) -> dict:
    """Parses one Live.<Module>.runtime.md into {class_key: {properties, methods}}."""
    module = path.name.replace("Live.", "").replace(".runtime.md", "")
    lines = html.unescape(path.read_text(encoding="utf-8")).splitlines()

    classes: dict = {}
    current_class = None
    current_section = None
    pending_method = None

    for line in lines:
        class_match = _CLASS_RE.match(line)
        if class_match:
            name, base = class_match.groups()
            pending_method = None
            current_section = None
            if base == "enum":
                current_class = None  # enum classes inherit the whole int surface: junk
                continue
            key = module if name == module else "%s.%s" % (module, name)
            current_class = classes.setdefault(key, {"properties": [], "methods": []})
            continue

        if line.startswith("## "):  # leaving the Classes section (e.g. module Functions)
            current_class = None
            continue

        if current_class is None:
            continue

        section_match = _SECTION_RE.match(line)
        if section_match:
            current_section = section_match.group(1)
            pending_method = None
            continue

        if current_section == "Properties":
            prop = _PROPERTY_RE.match(line)
            if prop and not prop.group(1).startswith("_") and prop.group(1) != "canonical_parent":
                current_class["properties"].append(
                    {"name": prop.group(1), "description": (prop.group(2) or "").strip()}
                )
        elif current_section == "Methods":
            method_match = _METHOD_RE.match(line)
            if method_match:
                name = method_match.group(1)
                is_noise = (
                    name.startswith("__") or _LISTENER_RE.search(name) or name in _QUERY_NAMES
                )
                pending_method = None if is_noise else name
                continue
            if pending_method and line.strip() and not line.startswith("```"):
                signature = _SIGNATURE_RE.match(line.strip())
                if signature and signature.group(1) == pending_method:
                    current_class["methods"].append(_parse_method(signature))
                pending_method = None

    return classes


def _parse_method(signature_match: "re.Match") -> dict:
    name, args, returns, description = signature_match.groups()
    optional_from = args.index("[") if "[" in args else len(args)
    params = []
    for param in _PARAM_RE.finditer(args):
        type_name, param_name, default = param.groups()
        if param_name == "arg1":  # self
            continue
        params.append(
            {
                "name": param_name,
                "type": type_name,
                "optional": param.start() >= optional_from or default is not None,
            }
        )
    return {
        "name": name,
        "params": params,
        "returns": returns,
        "description": description.strip(),
    }


def _finalize(classes: dict) -> dict:
    """Stamps actionability/settability and sorts everything for stable output."""
    for class_key, content in classes.items():
        base = class_key.split(".")[-1]
        for prop in content["properties"]:
            override = _SETTABLE_OVERRIDES.get("%s.%s" % (base, prop["name"]))
            if override is not None:
                prop["settable"] = override
            else:
                description = prop["description"].lower()
                prop["settable"] = any(hint in description for hint in _SETTABLE_HINTS)
        for method in content["methods"]:
            method["actionable"] = not method["name"].startswith(_QUERY_PREFIXES)
        content["properties"].sort(key=lambda p: p["name"])
        content["methods"].sort(key=lambda m: m["name"])
    return dict(sorted(classes.items()))


def extract(source: Path) -> dict:
    classes: dict = {}
    for path in sorted(source.glob("Live.*.runtime.md")):
        classes.update(parse_module(path))
    classes.update({key: json.loads(json.dumps(value)) for key, value in _VIEW_SUPPLEMENT.items()})
    return {"source": source.name, "classes": _finalize(classes)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="re-extract and fail (exit 1) if the committed inventory differs",
    )
    args = parser.parse_args()

    inventory = extract(args.source)
    rendered = json.dumps(inventory, indent=2, sort_keys=False) + "\n"

    if args.check:
        committed = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if committed != rendered:
            print("lom-inventory.json is out of date — run: python scripts/lom_catalog/extract.py")
            return 1
        print("lom-inventory.json is up to date")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8", newline="\n")
    classes = inventory["classes"]
    methods = sum(len(c["methods"]) for c in classes.values())
    properties = sum(len(c["properties"]) for c in classes.values())
    print(
        "%s: %d classes, %d properties, %d methods"
        % (args.output, len(classes), properties, methods)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
