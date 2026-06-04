"""Entry point of the Protocol0 launcher (protocol0-launcher.exe).

This tiny exe is what the user double-clicks (desktop / Start Menu shortcut). It is NOT
the resident agent: the agent already runs as a scheduled task at logon and serves the
web page on the fixed port ``settings.WEB_PORT`` (9010). The launcher merely opens that
page in the default browser, then exits immediately.

Why a dedicated exe rather than an Internet shortcut (.url):
- A .url necessarily takes the default browser's icon (+ the shortcut-overlay arrow)
  -> "ugly", not a real app.
- An exe carries its own icon (the "P" badge, see installer/assets/protocol0.ico,
  embedded by protocol0-launcher.spec) and has NO shortcut overlay when dropped directly
  on the desktop.

Built without a console (PyInstaller --windowed): no black-window flash.
webbrowser is stdlib -> no new hidden import / antivirus profile unchanged.
"""
import webbrowser

from agent.settings import WEB_PORT

# Open straight on the keymapper (/shortcuts) rather than the landing page (/): the
# shortcut is the thing the user came to manage. The SPA serves /shortcuts via the
# history-mode catch-all, so a deep-link survives the cold open.
LAUNCHER_URL = "http://127.0.0.1:%d/shortcuts" % WEB_PORT


def main() -> None:
    # new=2: open in a new tab of the default browser.
    webbrowser.open(LAUNCHER_URL, new=2)


if __name__ == "__main__":
    main()
