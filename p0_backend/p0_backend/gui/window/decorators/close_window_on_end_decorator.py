from p0_backend.gui.window.decorators.window_decorator import WindowDecorator


class CloseWindowOnEndDecorator(WindowDecorator):
    def display(self):
        self.window.display()
        self.sg_window.close()
