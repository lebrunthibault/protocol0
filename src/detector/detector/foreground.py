"""Détecte si Ableton est la fenêtre au premier plan.

Reproduit le `#IfWinActive ahk_exe Ableton Live 12 Suite.exe` du mappings.ahk :
le raccourci ne se déclenche que quand Ableton a le focus. Évite de voler des
touches aux autres apps et règle la cohabitation avec le frontend de config.

Spécifique Windows (ctypes/Win32). Isolé ici pour le futur portage macOS
(équivalent : NSWorkspace.frontmostApplication).
"""
import ctypes
from ctypes import wintypes

_ABLETON_EXE_SUBSTRING = "ableton live"

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def _foreground_process_name() -> str:
    hwnd = _user32.GetForegroundWindow()
    if not hwnd:
        return ""
    pid = wintypes.DWORD()
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ""
    handle = _kernel32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(260)
        size = wintypes.DWORD(len(buf))
        # QueryFullProcessImageNameW(handle, 0, buf, &size)
        if not _kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return ""
        return buf.value
    finally:
        _kernel32.CloseHandle(handle)


def ableton_is_foreground() -> bool:
    return _ABLETON_EXE_SUBSTRING in _foreground_process_name().lower()
