from PySimpleGUI import BLUES

from p0_backend.lib.enum.abstract_enum import AbstractEnum


class ColorEnum(AbstractEnum):
    SUCCESS = "SUCCESS"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    @property
    def hex_value(self) -> str:
        return self.get_value_from_mapping(
            {
                ColorEnum.SUCCESS: "#2d985c",
                ColorEnum.INFO: BLUES[2],
                ColorEnum.WARNING: "#8c982d",
                ColorEnum.ERROR: "#ea5852",
            }
        )
