import ctypes
import os


def go_to_desktop(n: int):
    virtual_desktop_accessor = ctypes.WinDLL(
        f"{os.path.dirname(__file__)}/VirtualDesktopAccessor.dll"
    )
    virtual_desktop_accessor.GoToDesktopNumber(n)
