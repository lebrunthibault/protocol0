import json
import logging
import types
from typing import Optional, Any, List, Dict

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.string import smart_string
from protocol0.shared.Config import Config
from protocol0.shared.logging.LogLevelEnum import LogLevelEnum
from protocol0.shared.logging.LoggerServiceInterface import LoggerServiceInterface


class LoggerService(LoggerServiceInterface):
    def log(self, message: Any, debug: bool = True, level: Optional[LogLevelEnum] = None) -> None:
        """a log function and not method allowing us to call this even with no access to the ControlSurface object"""
        if isinstance(message, types.GeneratorType):
            message = list(message)

        if isinstance(message, List) or isinstance(message, Dict):
            try:
                # use str to json encode classes
                message = json.dumps(message, indent=4, default=str)
            except (TypeError, UnicodeEncodeError) as e:
                from protocol0.shared.logging.Logger import Logger

                Logger.warning(e)

        level = level or LogLevelEnum.INFO
        if level.value < Config.LOG_LEVEL.value:
            return
        message = f"{level.name.lower()}: {smart_string(message)}"

        if not isinstance(debug, bool):
            raise Protocol0Error("logger: parameter mismatch")
        if debug:
            from protocol0.domain.shared.utils.debug import get_frame_info

            frame_info = get_frame_info(4)
            if frame_info:
                message = "%s (%s:%s in %s)" % (
                    message,
                    frame_info.filename,
                    frame_info.line,
                    frame_info.method_name,
                )

        logging.info(f"P0 - {message}")

        # for line in message.splitlines():
        #     logging.info(f"P0 - {line}")
