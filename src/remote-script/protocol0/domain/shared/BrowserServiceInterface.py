from protocol0.shared.sequence.Sequence import Sequence


class BrowserServiceInterface(object):
    def load_device(self, name: str) -> Sequence:
        raise NotImplementedError

    def load_from_user_library(self, name: str) -> Sequence:
        raise NotImplementedError
