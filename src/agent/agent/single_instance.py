"""Verrou single-instance via named mutex Win32.

Deux agents en parallèle = deux hooks clavier WH_KEYBOARD_LL, donc chaque frappe
est traitée deux fois (raccourci déclenché en double). Ça arrive notamment à l'install :
le [Run] postinstall lance l'agent (--open), et un raccourci Startup au logon peut chevaucher
un lancement manuel via le raccourci Menu Démarrer.

Un named mutex est le verrou idiomatique Windows : l'OS le relâche à la mort du process
(pas d'orphelin après crash, contrairement à un lockfile), et c'est plus fiable que de se
fier au bind du port web (qui part en retry s'il échoue).

ctypes/Win32, cohérent avec foreground.py.
"""
import ctypes

_ERROR_ALREADY_EXISTS = 183

# Le handle DOIT rester vivant toute la vie du process : si le GC le collecte, le mutex
# est relâché et une 2e instance pourrait l'acquérir. On le garde en module-level.
_handle = None


def acquire(name: str = "Protocol0-Detector") -> bool:
    """Tente de prendre le verrou. True si on est la 1re instance, False si une autre tourne.

    Le nom du mutex reste "Protocol0-Detector" (identité interne stable) même après le renommage
    detector -> agent : l'installeur tue l'ancien exe avant d'installer le nouveau, donc deux
    versions ne coexistent jamais, et le renommer n'apporterait rien.
    """
    global _handle
    kernel32 = ctypes.windll.kernel32
    _handle = kernel32.CreateMutexW(None, False, name)
    return kernel32.GetLastError() != _ERROR_ALREADY_EXISTS
