class Timer:
    """No-op stand-in for the Live main-loop timer (tests drive ticks manually)."""

    def __init__(self, callback=None, interval=1, repeat=False):
        self._callback = callback
        self._interval = interval
        self._repeat = repeat

    def start(self):
        pass

    def stop(self):
        pass
