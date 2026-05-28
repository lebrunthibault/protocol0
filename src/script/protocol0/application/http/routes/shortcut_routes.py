"""Routes du gestionnaire de raccourcis (catalogue + config des bindings).

M2 : GET /actions — catalogue des actions assignables (dérivé des @route, cf.
ActionCatalog). Les routes du frontend (GET /shortcuts, /shortcuts/list,
/shortcuts/add) arrivent en M3 et s'appuieront sur ShortcutConfigService.
"""
from typing import Any, Dict, List

from protocol0.application.http.ActionCatalog import get_catalog
from protocol0.application.http.Router import route


@route("GET", "/actions")
def actions() -> List[Dict[str, Any]]:
    """List the actions assignable to a keyboard shortcut, with their params."""
    return get_catalog()
