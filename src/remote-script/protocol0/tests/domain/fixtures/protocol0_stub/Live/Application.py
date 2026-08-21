from Live._meta import LomObject


class Application(LomObject):
    class View(LomObject):
        class NavDirection:
            up = 0
            down = 1
            left = 2
            right = 3
