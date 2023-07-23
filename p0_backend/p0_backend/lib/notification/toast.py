from win10toast import ToastNotifier

toast = ToastNotifier()


def show_notification(title: str, duration: int = 3):
    toast.show_toast(
        title,
        " ",
        duration=duration,
        threaded=True,
    )
