import os
from os.path import dirname

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        # __file__ -> <repo>/src/detector/detector/settings.py; the monorepo-root
        # .env is 4 dirnames up (settings.py -> detector -> detector -> src -> <repo>).
        # Same depth/convention as backend/settings.py.
        env_file = os.path.join(dirname(dirname(dirname(dirname(__file__)))), ".env")
        # The shared root .env also carries P0_BACKEND_PORT (for the backend); the
        # detector only needs the script port, so ignore unrelated keys.
        extra = "ignore"

    p0_script_port: int

    @property
    def p0_script_url(self) -> str:
        return f"http://127.0.0.1:{self.p0_script_port}"
