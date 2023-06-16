class LoopableInterface(object):
    @property
    def looping(self) -> bool:
        raise NotImplementedError

    @looping.setter
    def looping(self, loop: bool) -> None:
        raise NotImplementedError

    @property
    def start(self) -> float:
        raise NotImplementedError

    @start.setter
    def start(self, start: float) -> None:
        raise NotImplementedError

    @property
    def end(self) -> float:
        raise NotImplementedError

    @end.setter
    def end(self, end: float) -> None:
        raise NotImplementedError

    @property
    def length(self) -> float:
        raise NotImplementedError

    @length.setter
    def length(self, length: float) -> None:
        raise NotImplementedError
