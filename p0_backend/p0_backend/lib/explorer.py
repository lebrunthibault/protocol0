import os
from os.path import basename
from time import sleep

from p0_backend.lib.decorators import retry
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.mouse.mouse import click
from p0_backend.lib.window.window import focus_window


def open_explorer(file_path: str, wait: bool = False) -> int:
    assert os.path.exists(file_path), f"'{file_path}' does not exist"
    file_path = file_path.replace("\\", "/")

    click((0, 500))  # move the cursor from the explorer window position
    folder_name = basename(os.path.split(file_path)[0])

    if not wait:
        os.system(f'start "", "{file_path}"')
        return 0

    try:
        handle = focus_window(folder_name)
        sleep(0.1)
        return handle
    except (AssertionError, Protocol0Error):
        os.system(f"explorer.exe /select, {file_path}")
        handle = retry(10, 0.5)(focus_window)(name=folder_name)
        sleep(0.5)

    return handle
