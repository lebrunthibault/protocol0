import time
from os.path import basename

import psutil
from loguru import logger
from psutil import NoSuchProcess

from p0_backend.api.settings import Settings


def _kill_old_processes():
    for p in psutil.process_iter():
        if p.name() != "python.exe":
            continue

        try:
            pid = p.pid
            cmd_line = p.cmdline()
            create_time = p.create_time()
        except NoSuchProcess:
            continue

        script_name = basename(cmd_line[1])

        if create_time >= time.time() - 10:
            continue

        if (
            basename(Settings().project_directory) in cmd_line[0]
            or basename(Settings().project_directory) in cmd_line[1]
            or script_name == "start_midi_server.py"
        ):
            logger.info(
                f"deleting process {pid} {script_name} after {time.time() - 3 - create_time:.2f}s"
            )
            p.kill()


if __name__ == "__main__":
    _kill_old_processes()
