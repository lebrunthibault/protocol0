from functools import partial
from unittest.mock import Mock

from protocol0.domain.shared.utils.func import nop


class SlotManager:
    def disconnect(self):
        pass

    def register_slot(self, *a, **k):
        pass


class Subject:
    def __call__(self, *a, **k):
        return self

    def __getattr__(self, name):
        return self


def subject_slot(*_, **__):
    @instance_decorator
    def decorator(self, method):
        return partial(method, self)

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
