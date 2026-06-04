"""The ``@action`` decorator — the single way a plugin exposes an action.

A plugin method decorated with ``@action`` becomes an HTTP action: the loader
(``PluginLoader``) generates a ``POST /api/action/<plugin>/<method>`` route for it
at startup. The plugin never touches ``@api_route`` — it only declares *what* to
expose; Protocol0 wires the route.

The decorator takes **no argument**:

- the **method name** is the action name;
- the method's **typed parameters** (``str``/``int``/``float``/``bool``) drive both
  the JSON body schema in ``/openapi.json`` and the typed inputs in the keymapper UI.

Everything is read from ``inspect.signature`` so the signature stays the single
source of truth shared with ``openapi.py``. Stdlib-only (Ableton).
"""
import inspect

# Attribute the decorator stamps on the underlying function. Read back off the
# bound method's ``__func__`` at discovery time.
_ACTION_ATTR = "_action_meta"


class ActionMeta(object):
    def __init__(self, name):
        # type: (str) -> None
        self.name = name


def action(fn):
    """Mark a plugin method as an exposed action (name = method name).

    Returns the function unchanged (no wrapper) so ``inspect.signature`` on the
    bound method still shows only the typed parameters — exactly what the router
    and the OpenAPI generator introspect.
    """
    setattr(fn, _ACTION_ATTR, ActionMeta(fn.__name__))
    return fn


def iter_actions(instance):
    """Yield ``(name, bound_method)`` for every ``@action`` method of a plugin instance.

    ``getmembers(..., ismethod)`` returns **bound** methods (``self`` already
    applied); the marker is read off ``member.__func__`` where ``@action`` set it.
    """
    actions = []
    for _, member in inspect.getmembers(instance, predicate=inspect.ismethod):
        meta = getattr(member.__func__, _ACTION_ATTR, None)
        if meta is not None:
            actions.append((meta.name, member))
    return actions
