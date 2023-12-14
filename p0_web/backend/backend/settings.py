import json
from os.path import dirname, join

from pydantic import BaseModel
from pydantic_settings import BaseSettings

PROJECT_DIRECTORY = dirname(dirname(__file__))
SETS_DIRECTORY = "/sets"
SETTINGS_FILE = join(PROJECT_DIRECTORY, "settings.json")


class DirectorySettings(BaseModel):
    tracks_directory: str = ""


class Settings(BaseSettings):
    port: int = 8000
    directories: DirectorySettings = DirectorySettings()


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings.dict(), file)


def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            settings_data = json.load(file)
            return Settings(**settings_data)

    except (FileNotFoundError, json.JSONDecodeError):
        return Settings()
