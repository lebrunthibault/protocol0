import os
import sys

# protocol0 has no third-party runtime deps — it runs on stdlib-only
# Python 3.11, so there is no .venv/site-packages to add to the path.

# P0_SOURCE_DIR is rewritten by `make install_script` to point at the
# checked-out script repo, so changes to protocol0/ are picked up
# without reinstalling.
P0_SOURCE_DIR = r"__P0_SOURCE_DIR__"
if os.path.isdir(P0_SOURCE_DIR):
    sys.path.insert(0, P0_SOURCE_DIR)

from protocol0.application.main import create_instance  # noqa
