from typing import Iterator, Any


class EmptyModule(object):
    def __init__(self, name="", is_false=True):
        # type: (str, bool) -> None
        self.name = name
        self.is_false = is_false

    def __ne__(self, other):
        # type: (object) -> bool
        return False

    def __eq__(self, other):
        # type: (object) -> bool
        return False

    def __nonzero__(self):
        # type: () -> bool
        """allows Live environment check"""
        return not self.is_false

    def __ge__(self, other):
        # type: (Any) -> bool
        """allows Live environment check"""
        return False

    def __call__(self, *a, **k):
        # type: (Any, Any) -> EmptyModule
        return self

    def __getattr__(self, name):
        # type: (Any) -> EmptyModule
        return self

    def __hash__(self):
        # type: () -> int
        return 0

    def __iter__(self):
        # type: () -> Iterator
        """Handles push2 scales"""
        return iter([("", "")])