import os
import site

venv_path = os.path.join( os.path.dirname(os.path.abspath(__file__)), ".venv\\Lib\\site-packages")
site.addsitedir(venv_path)

from protocol0.application.main import create_midi_duplicator_instance as create_instance  # noqa
