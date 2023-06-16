from functools import wraps, partial
from unittest.mock import Mock, MagicMock

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

# Subject = MagicMock()

class Subject2:

    def __init__(self, func):
        self.func = func
        self.subject = "toto"


    def __call__(self, *a, **k):
        print((self, a, k))
        return self.func(self, *a, **k)
        # return self

def subject_slot2(*_, **__):
    def decorator(func):
        @wraps(func)
        def decorated(self, *a, **k):
            print("return")
            print(self)
            print(a)
            print(k)
            return func(self, *a, **k)

        return Subject2(func)
        # return Mock(side_effect=partial(decorated)

    return decorator

def subject_slot(*_, **__):
    @instance_decorator
    def decorator(self, method):
        return partial(method, self)

    return decorator


def instance_decorator(decorator):
    u"""
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
            self._data_name = u'%s_%d_decorated_instance' % (func.__name__, id(self))
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
