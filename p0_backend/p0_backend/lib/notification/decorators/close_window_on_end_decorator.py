from p0_backend.lib.notification.decorators.window_decorator import WindowDecorator


class CloseWindowOnEndDecorator(WindowDecorator):
    def display(self):
        self.window.display()
        self.sg_window.close()
