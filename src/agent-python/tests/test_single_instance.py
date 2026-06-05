"""Le verrou single-instance : la 1re acquisition réussit, la 2e (même nom) échoue."""
import sys

import pytest

if sys.platform != "win32":
    pytest.skip("single_instance is Win32-only", allow_module_level=True)

from agent import single_instance


def test_first_acquire_succeeds_second_fails():
    # Nom unique au test pour ne pas entrer en conflit avec un agent réel qui tournerait.
    name = "Protocol0-Detector-test-lock"
    assert single_instance.acquire(name) is True
    # 2e acquisition du même mutex nommé (même process, handle distinct) : Windows renvoie
    # ERROR_ALREADY_EXISTS -> on doit détecter "déjà pris".
    assert single_instance.acquire(name) is False
