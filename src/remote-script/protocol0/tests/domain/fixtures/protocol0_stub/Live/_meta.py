from unittest.mock import Mock


class LenientMeta(type):
    """Unknown class attributes resolve to a Mock.

    Production annotations reference attributes we don't model (e.g.
    Live.Song.Song.view evaluated at def time); LOM object classes are lenient
    so those resolve, while enum classes stay strict so a missing member fails
    loudly instead of comparing a Mock.
    """

    def __getattr__(cls, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return Mock()


class LomObject(metaclass=LenientMeta):
    pass
