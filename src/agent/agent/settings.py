"""Runtime settings of the agent.

The agent ships as a standalone exe (PyInstaller), with no .env alongside.

The script port is no longer hardwired: the script picks it dynamically and publishes its
effective URL in runtime.json (see runtime_state). So we discover the URL at runtime.
P0_SCRIPT_PORT remains a manual escape hatch: if set, it forces the URL and bypasses
runtime.json (advanced / dev cases).
"""
import os
from typing import Optional

# Fixed port of the web server served by the agent (home + keymapper + /api + /status).
# Hardwired: the launcher (agent/launcher_entry.py, packaged as protocol0-launcher.exe) opens
# http://127.0.0.1:9010/ and imports this constant -> single source of truth for the port, no
# dynamic fallback on the launcher side. The URL must also stay bookmarkable.
WEB_PORT = 9010
# Back-compat alias (the old name was LAUNCHER_PORT).
LAUNCHER_PORT = WEB_PORT


class Settings:
    def __init__(self) -> None:
        self._override_port: Optional[int] = (
            int(os.environ["P0_SCRIPT_PORT"]) if "P0_SCRIPT_PORT" in os.environ else None
        )

    @property
    def override_url(self) -> Optional[str]:
        """URL forced via P0_SCRIPT_PORT, or None for dynamic discovery."""
        if self._override_port is None:
            return None
        return "http://127.0.0.1:%d" % self._override_port
