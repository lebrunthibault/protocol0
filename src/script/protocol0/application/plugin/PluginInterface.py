from typing import ClassVar


class PluginInterface(object):
    name: ClassVar[str] = ""

    def should_start(self) -> bool:
        return True

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError
