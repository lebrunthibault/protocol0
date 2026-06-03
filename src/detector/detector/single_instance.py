"""Verrou single-instance via named mutex Win32.

Deux detectors en parallèle = deux hooks clavier WH_KEYBOARD_LL, donc chaque frappe
est traitée deux fois (raccourci déclenché en double). Ça arrive notamment à l'install :
le [Run] de l'installeur lance le detector pendant que la tâche planifiée le lance aussi.

Un named mutex est le verrou idiomatique Windows : l'OS le relâche à la mort du process
(pas d'orphelin après crash, contrairement à un lockfile), et c'est plus fiable que de se
fier au bind du port launcher (qui part en retry s'il échoue).

ctypes/Win32, cohérent avec foreground.py.
"""
import ctypes

_ERROR_ALREADY_EXISTS = 183

# Le handle DOIT rester vivant toute la vie du process : si le GC le collecte, le mutex
# est relâché et une 2e instance pourrait l'acquérir. On le garde en module-level.
_handle = None


def acquire(name: str = "Protocol0-Detector") -> bool:
    """Tente de prendre le verrou. True si on est la 1re instance, False si une autre tourne."""
    global _handle
    kernel32 = ctypes.windll.kernel32
    _handle = kernel32.CreateMutexW(None, False, name)
    return kernel32.GetLastError() != _ERROR_ALREADY_EXISTS
