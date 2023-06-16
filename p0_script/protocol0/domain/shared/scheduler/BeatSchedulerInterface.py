from typing import Callable


class BeatSchedulerInterface(object):
    def wait_beats(self, beats: float, callback: Callable, execute_on_song_stop: bool) -> None:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError
