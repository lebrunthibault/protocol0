from os.path import dirname

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    user_home: str
    ableton_version: str = Field(alias="abletonVersion")

    @property
    def ableton_major_version(self) -> str:
        return self.ableton_version.split(".")[0]

    @property
    def log_file_path(self) -> str:
        return f"{self.user_home}\\AppData\\Roaming\\Ableton\\Live {self.ableton_version}\\Preferences\\Log.txt"

    project_directory: str = dirname(dirname(__file__))

    @property
    def ableton_exe(self) -> str:
        return f"C:\\ProgramData\\Ableton\\Live {self.ableton_major_version} Suite\\Program\\Ableton Live {self.ableton_major_version} Suite.exe"

    @property
    def ableton_process_name(self) -> str:
        return f"Ableton Live {self.ableton_major_version} Suite.exe"

    splice_executable: str = "C:\\Users\\thiba\\AppData\\Local\\splice\\Splice.exe"

    @property
    def preferences_directory(self) -> str:
        return (
            f"{self.user_home}\\AppData\\Roaming\\Ableton\\Live {self.ableton_version}\\Preferences"
        )

    ableton_set_directory: str

    @property
    def ableton_test_set_path(self) -> str:
        return f"{self.ableton_set_directory}\\test.als"

    icons_directory: str = "C:\\Users\\thiba\\OneDrive\\Images\\icons"

    http_api_url: str = "http://127.0.0.1:8000"

    log_window_title: str = "Protocol0 logs"

    # Midi port names are relative to the Protocol0 script and not this midi backend
    p0_output_port_name: str = "P0_OUT"
    p0_input_port_name: str = "P0_IN_HTTP"
    # p0_backend_loopback_name: str = "P0_BACKEND_LOOPBACK"
