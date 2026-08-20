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

The decorator wraps the method to run it inside a **Live undo step**, so a single
Ctrl-Z in Ableton reverts a whole action. The wrapper is signature-transparent
(see ``_http_signature``), which is what lets the router and the OpenAPI
generator keep introspecting it as if it were the bare method.
"""
import inspect
from functools import partial, wraps

# Attribute the decorator stamps on the underlying function. Read back off the
# bound method's ``__func__`` at discovery time.
_ACTION_ATTR = "_action_meta"


class ActionMeta(object):
    def __init__(self, name):
        # type: (str) -> None
        self.name = name


def _http_signature(fn):
    """The signature the router and the OpenAPI generator must see on the wrapper.

    Two things have to hold at once, and neither comes for free:

    - the **parameters** stay those of ``fn`` (``Router._build_kwargs`` and the
      OpenAPI schema read them). ``@wraps`` alone would not do: it sets
      ``__wrapped__``, but if we drop that, ``inspect.signature`` falls back to
      the wrapper's own ``(*a, **k)``;
    - the **return annotation** is forced to ``None``. ``Router._returns_value``
      reads it to decide whether to wait for a result. An action may legitimately
      declare ``-> Optional[Sequence]`` (it does return one, and we chain it
      below), but over HTTP the contract stays fire-and-forget: waiting would
      block the HTTP thread and then fail to JSON-serialize the Sequence.

    Setting ``__signature__`` covers both — ``inspect.signature`` honours it over
    ``__wrapped__``.
    """
    return inspect.signature(fn).replace(return_annotation=None)


def action(fn):
    """Mark a plugin method as an exposed action (name = method name).

    The action runs inside a Live undo step, so one Ctrl-Z reverts it whole.
    The step is closed through a ``Sequence``: when the action returns one
    (i.e. it finishes later), ``SequenceStep`` chains it and the step is only
    closed once that Sequence completes — same mechanism as ``EncoderAction``.
    """
    from protocol0.shared.Undo import Undo
    from protocol0.shared.sequence.Sequence import Sequence

    @wraps(fn)
    def with_undo_step(*a, **k):
        Undo.begin_undo_step()
        seq = Sequence()
        seq.add(partial(fn, *a, **k))
        seq.add(Undo.end_undo_step)
        seq.done()

    with_undo_step.__signature__ = _http_signature(fn)
    setattr(with_undo_step, _ACTION_ATTR, ActionMeta(fn.__name__))
    return with_undo_step


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
