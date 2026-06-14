from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


class BrowserItemNotFoundError(Protocol0Warning):
    def __init__(self, name: str) -> None:
        super(BrowserItemNotFoundError, self).__init__(
            "Device not found in the Live library: %s" % name
        )
        self.name = name
