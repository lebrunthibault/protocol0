from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class BrowserItemNotFoundError(Protocol0Error):
    def __init__(self, name: str) -> None:
        super(BrowserItemNotFoundError, self).__init__(
            "Cannot find browser item in the live library: %s\n" % name
        )
        self.name = name
