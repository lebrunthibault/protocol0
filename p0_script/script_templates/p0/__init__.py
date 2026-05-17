import os
import site
import sys

_here = os.path.dirname(os.path.abspath(__file__))

site.addsitedir(os.path.join(_here, ".venv", "Lib", "site-packages"))

# P0_SOURCE_DIR is rewritten by `make install_script` to point at the
# checked-out p0_script repo, so changes to protocol0/ are picked up
# without reinstalling.
P0_SOURCE_DIR = r"__P0_SOURCE_DIR__"
if os.path.isdir(P0_SOURCE_DIR):
    sys.path.insert(0, P0_SOURCE_DIR)

from protocol0.application.main import create_instance  # noqa
