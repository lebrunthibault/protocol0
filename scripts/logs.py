"""Tail combine les logs Ableton et ceux de l'agent dans un seul terminal (target `make logs`).

Pourquoi : en dev on veut une seule fenetre qui montre ce que fait le remote script (cote
Ableton, via Log.txt) ET ce que fait l'agent (raccourcis clavier, appels HTTP au script,
serveur web). Avant, ca vivait dans le backend extrait (loguru + rx). Ici on le reecrit en
stdlib pure, comme les autres scripts/*.py du dispatcher.

Deux sources, interleavees ligne a ligne :
  1. [ableton] : %APPDATA%\\Ableton\\Live */Preferences/Log.txt. On ne garde que les lignes
     P0/Protocol0 (le Log.txt est tres bavard), on retire le prefixe "Protocol 0 - " et on
     colore en vert (rouge si erreur).
  2. [agent]   : %APPDATA%\\Protocol0\\logs\\agent.log (cf. agent/main.py:_log_dir). On retire
     le prefixe stdlib "2026-... INFO agent: " (redondant) et on colore en magenta.

Chaque fichier est suivi dans un thread daemon ; les lignes existantes ne sont PAS rejouees
(on seek a la fin), on n'affiche que ce qui arrive apres le lancement. Stdlib uniquement,
Windows-only (chemins APPDATA + Ableton). Ctrl-C pour quitter.
"""
import os
import re
import sys
import threading
import time
from pathlib import Path

# Couleurs ANSI. Windows 10/11 Terminal les interprete nativement ; on active le mode VT
# au demarrage (_enable_vt) pour le cas conhost classique.
_RESET = "\033[0m"
_COLORS = {
    "green": "\033[32m",
    "red": "\033[31m",
    "magenta": "\033[35m",
    "yellow": "\033[33m",
    "grey": "\033[90m",
}

# Lignes du remote script dans Log.txt : "Protocol 0 - <message>" (ex. "Protocol 0 - HTTP GET /").
_SCRIPT_PREFIX_RE = re.compile(r"^.*?Protocol 0 - ")
# Toute ligne Log.txt mentionnant P0/Protocol0 nous interesse (le reste est du bruit Live).
_SCRIPT_KEEP_RE = re.compile(r"Protocol ?0|P0 -")
# Prefixe stdlib de l'agent : "2026-06-02 01:54:10,066 INFO agent: ".
_AGENT_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \w+ [\w.]+: ")
# Heuristique d'erreur (colore en rouge).
_ERROR_RE = re.compile(
    r"error|traceback|exception|RemoteScriptError", re.IGNORECASE
)

_print_lock = threading.Lock()


def _enable_vt() -> None:
    """Active l'interpretation des sequences ANSI sous conhost (no-op si deja gere)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        # -11 = STD_OUTPUT_HANDLE ; 0x0004 = ENABLE_VIRTUAL_TERMINAL_PROCESSING.
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def _emit(prefix: str, color: str, text: str) -> None:
    c = _COLORS.get(color, "")
    stamp = time.strftime("%H:%M:%S")
    with _print_lock:
        print("%s%s [%s]%s %s" % (c, stamp, prefix, _RESET, text), flush=True)


# Versions beta de Live : suffixe "b<chiffre>" (ex. "Live 12.4.5b3"). On les exclut de la
# selection du Log.txt -> on tail la version stable installee, pas un build beta parallele.
_BETA_RE = re.compile(r"b\d+$")


def _ableton_log_path():
    """Le Log.txt P0 le plus recent sous %APPDATA%\\Ableton\\Live * (hors beta). None si introuvable."""
    root = Path(os.environ.get("APPDATA", "")) / "Ableton"
    candidates = [
        p / "Preferences" / "Log.txt"
        for p in sorted(root.glob("Live *"))
        if (p / "Preferences" / "Log.txt").exists() and not _BETA_RE.search(p.name)
    ]
    if not candidates:
        return None
    # Plusieurs versions de Live installees -> on prend le Log.txt modifie le plus recemment.
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _agent_log_path():
    return Path(os.environ.get("APPDATA", "")) / "Protocol0" / "logs" / "agent.log"


def _follow(path: Path):
    """Generateur : attend que `path` existe, seek a la fin, puis yield chaque nouvelle ligne."""
    while not path.exists():
        time.sleep(0.5)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        f.seek(0, os.SEEK_END)
        buf = ""
        while True:
            chunk = f.readline()
            if chunk:
                buf += chunk
                if buf.endswith("\n"):
                    yield buf.rstrip("\n")
                    buf = ""
            else:
                time.sleep(0.2)


def _tail_ableton(path: Path) -> None:
    for line in _follow(path):
        if not _SCRIPT_KEEP_RE.search(line):
            continue
        clean = _SCRIPT_PREFIX_RE.sub("", line)
        color = "red" if _ERROR_RE.search(clean) else "green"
        _emit("ableton", color, clean)


def _tail_agent(path: Path) -> None:
    for line in _follow(path):
        clean = _AGENT_PREFIX_RE.sub("", line)
        color = "red" if _ERROR_RE.search(line) else "magenta"
        _emit("agent", color, clean)


def main() -> int:
    if sys.platform != "win32":
        print("make logs: Windows-only (Ableton + APPDATA paths).")
        return 0
    _enable_vt()

    ableton = _ableton_log_path()
    agent = _agent_log_path()

    print("Tailing combined logs (Ctrl-C to quit):")
    if ableton:
        print("  [ableton] %s" % ableton)
    else:
        print("  [ableton] (no Ableton Log.txt found under %%APPDATA%%\\Ableton)")
    print("  [agent]   %s%s" % (agent, "" if agent.exists() else "  (waiting...)"))
    print()

    threads = []
    if ableton:
        threads.append(threading.Thread(target=_tail_ableton, args=(ableton,), daemon=True))
    threads.append(threading.Thread(target=_tail_agent, args=(agent,), daemon=True))
    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nbye.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
