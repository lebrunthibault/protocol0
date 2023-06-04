import time
from os.path import basename

import psutil
from loguru import logger
from psutil import NoSuchProcess

from p0_backend.api.settings import Settings


def kill_old_processes():
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
            any("p0_backend" in arg for arg in cmd_line)
        ):
            logger.info(
                f"deleting process {pid} {script_name} after {time.time() - 3 - create_time:.2f}s"
            )

            p.kill()


kill_old_processes()
