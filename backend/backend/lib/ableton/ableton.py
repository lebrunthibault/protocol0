import win32gui  # noqa

from backend.lib.window.find_window import SearchTypeEnum
from backend.lib.window.window import focus_window
from backend.settings import Settings

settings = Settings()


def focus_ableton() -> None:
    focus_window(
        settings.ableton_process_name, search_type=SearchTypeEnum.PROGRAM_NAME
    )  # type: ignore
