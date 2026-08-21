from functools import partial
from unittest.mock import Mock

from protocol0.domain.shared.utils.func import nop


class SlotManager:
    def disconnect(self):
        pass

    def register_slot(self, *a, **k):
        pass


class Subject:
    """Fake base for the LOM fixtures, with a real listener registry.

    add_<name>_listener / remove_<name>_listener / <name>_has_listener are
    synthesized for any name, and setting an attribute fires its listeners —
    so domain code observing a fake reacts to mutations like in Live.
    Unknown attributes still resolve to self (null object), matching the
    historical stub behavior until every fake models its full surface.
    """

    def __getattr__(self, name):
        if name.startswith("__"):
            # never swallow dunder lookups (copy / pickle / inspect protocols)
            raise AttributeError(name)
        if name.startswith("add_") and name.endswith("_listener"):
            return partial(self._add_listener, name[len("add_") : -len("_listener")])
        if name.startswith("remove_") and name.endswith("_listener"):
            return partial(self._remove_listener, name[len("remove_") : -len("_listener")])
        if name.endswith("_has_listener"):
            return partial(self._has_listener, name[: -len("_has_listener")])
        if name.startswith("notify_"):
            return partial(self._notify_listeners, name[len("notify_") :])
        return self

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if self.__dict__.get("_p0_listeners", {}).get(name):
            # Live never re-enters your own modifying code: listeners fire on the
            # next tick, not synchronously (create_clip-style flows subscribe to
            # the resulting event right after mutating and rely on this)
            from protocol0.domain.shared.scheduler.Scheduler import Scheduler

            Scheduler.defer(partial(self._notify_listeners, name))

    def __call__(self, *a, **k):
        return self

    def _listener_registry(self):
        return self.__dict__.setdefault("_p0_listeners", {})

    def _add_listener(self, event, listener):
        listeners = self._listener_registry().setdefault(event, [])
        if listener not in listeners:
            listeners.append(listener)

    def _remove_listener(self, event, listener):
        listeners = self._listener_registry().get(event, [])
        if listener in listeners:
            listeners.remove(listener)

    def _has_listener(self, event, listener):
        return listener in self._listener_registry().get(event, [])

    def _notify_listeners(self, event):
        for listener in list(self._listener_registry().get(event, [])):
            listener()


class SubjectSlot:
    """Callable slot returned by @subject_slot: assigning .subject registers the
    decorated method as a listener on the subject (a fake or a Mock)."""

    def __init__(self, event, listener):
        self._event = event
        self._listener = listener
        self._subject = None

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, subject):
        if self._subject is not None:
            remove = getattr(self._subject, "remove_%s_listener" % self._event, None)
            if callable(remove):
                remove(self._listener)
        self._subject = subject
        if subject is not None:
            add = getattr(subject, "add_%s_listener" % self._event, None)
            if callable(add):
                add(self._listener)

    def __call__(self, *a, **k):
        return self._listener(*a, **k)


def subject_slot(event):
    @instance_decorator
    def decorator(self, method):
        return SubjectSlot(event, partial(method, self))

    return decorator


def instance_decorator(decorator):
    """
    Meta-decorator to define decorators that decorate a method in a
    concrete instance. The decorator method will be passed the
    object instance as first argument and the unbound decorated method
    as second argument. The decorator method will be called lazily the
    first time the method is accessed.

    For an example see @subject_slot in SubjectSlot module.
    """

    class Decorator(object):
        def __init__(self, func=nop, *args, **kws):
            self.__name__ = func.__name__
            self.__doc__ = func.__doc__
            self._data_name = "%s_%d_decorated_instance" % (func.__name__, id(self))
            self._func = func
            self._args = args
            self._kws = kws

        def __get__(self, obj, cls=None):
            if obj is None:
                return
            data_name = self._data_name
            try:
                return obj.__dict__[data_name]
            except KeyError:
                decorated = decorator(obj, self._func, *self._args, **self._kws)
                obj.__dict__[data_name] = decorated
                return decorated

    return Decorator


subject_slot_group = Mock()
