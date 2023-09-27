import glob
import os
from typing import List

from p0_backend.settings import Settings
from p0_backend.lib.window.find_window import get_windows_list

settings = Settings()


def get_ableton_windows() -> List[str]:
    set_infos = filter(lambda i: i["app_name"] == settings.ableton_process_name, get_windows_list())

    return [i["name"] for i in set_infos]


def get_last_launched_track_set(excluded_keywords=("default", "master")) -> str:
    """Last launched track"""
    set_filenames = glob.glob(f"{settings.ableton_set_directory}\\tracks\\**\\*.als") + glob.glob(
        f"{settings.ableton_set_directory}\\ideas\\**\\*.als"
    )

    track_set_filenames = filter(
        lambda name: not any(excluded in name.lower() for excluded in excluded_keywords),
        set_filenames,
    )

    return max(track_set_filenames, key=os.path.getatime)


def get_set_from_title(title: str) -> str:
    file_paths = []

    filename = f"{title}.als"
    from loguru import logger
    logger.success(title)
    logger.success(filename)

    for root, _, files in os.walk(settings.ableton_set_directory):
        for file in files:
            if file == filename:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

    assert (
        len(file_paths) <= 1
    ), f"Duplicate sets found : '{filename}' in {settings.ableton_set_directory}"
    from loguru import logger
    logger.success(file_paths)
    assert len(file_paths) == 1, f"Couldn't find '{filename}' in {settings.ableton_set_directory}"

    return file_paths[0]
