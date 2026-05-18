import os
from os.path import dirname

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    class Config:
        env_file = os.path.join(dirname(dirname(dirname(__file__))), ".env")

    user_home: str
    ableton_name: str = Field(alias="abletonName")
    ableton_version: str = Field(alias="abletonVersion")

    @property
    def log_file_path(self) -> str:
        return f"{self.user_home}\\AppData\\Roaming\\Ableton\\Live {self.ableton_version}\\Preferences\\Log.txt"

    project_directory: str = dirname(dirname(__file__))

    @property
    def ableton_exe(self) -> str:
        return f"C:\\ProgramData\\Ableton\\{self.ableton_name}\\Program\\Ableton {self.ableton_name}.exe"

    @property
    def ableton_process_name(self) -> str:
        return f"Ableton {self.ableton_name}.exe"

    @property
    def splice_executable(self) -> str:
        return f"{self.user_home}\\AppData\\Local\\splice\\Splice.exe"

    @property
    def preferences_directory(self) -> str:
        return (
            f"{self.user_home}\\AppData\\Roaming\\Ableton\\Live {self.ableton_version}\\Preferences"
        )

    ableton_set_directory: str

    @property
    def ableton_test_set_path(self) -> str:
        return f"{self.ableton_set_directory}\\other\\test.als"

    @property
    def icons_directory(self) -> str:
        return f"{self.user_home}\\OneDrive\\Images\\icons"

    log_window_title: str = "Protocol0 logs"

    p0_backend_port: int
    p0_script_port: int

    @property
    def p0_script_url(self) -> str:
        return f"http://127.0.0.1:{self.p0_script_port}"
