from os.path import dirname

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = 8001
    project_directory: str = dirname(dirname(__file__))
    ableton_set_directory: str = "/sets"
