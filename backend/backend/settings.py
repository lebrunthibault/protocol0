import os
from os.path import dirname
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = os.path.join(dirname(dirname(dirname(__file__))), ".env")

    user_home: str

    @property
    def log_file_path(self) -> str:
        ableton_root = Path(self.user_home) / "AppData" / "Roaming" / "Ableton"
        candidates = [
            p / "Preferences" / "Log.txt"
            for p in ableton_root.glob("Live *")
            if (p / "Preferences" / "Log.txt").exists()
        ]
        if not candidates:
            raise FileNotFoundError(f"No Ableton Log.txt found under {ableton_root}")
        return str(max(candidates, key=lambda p: p.stat().st_mtime))

    project_directory: str = dirname(dirname(__file__))

    p0_backend_port: int
    p0_script_port: int

    @property
    def p0_script_url(self) -> str:
        return f"http://127.0.0.1:{self.p0_script_port}"
