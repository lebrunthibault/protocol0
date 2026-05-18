import win32gui  # noqa

from p0_backend.lib.window.find_window import SearchTypeEnum
from p0_backend.lib.window.window import focus_window
from p0_backend.settings import Settings

settings = Settings()


def focus_ableton() -> None:
    focus_window(
        settings.ableton_process_name, search_type=SearchTypeEnum.PROGRAM_NAME
    )  # type: ignore
