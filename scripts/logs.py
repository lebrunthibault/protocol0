"""Tail combine les logs Ableton et ceux de l'agent dans un seul terminal (target `make logs`).

Pourquoi : en dev on veut une seule fenetre qui montre ce que fait le remote script (cote
Ableton, via Log.txt) ET ce que fait l'agent (raccourcis clavier, appels HTTP au script,
serveur web). Avant, ca vivait dans le backend extrait (loguru + rx). Ici on le reecrit en
stdlib pure, comme les autres scripts/*.py du dispatcher.

Deux sources, interleavees ligne a ligne :
  1. [ableton] : %APPDATA%\\Ableton\\Live */Preferences/Log.txt. On ne garde que les lignes
     P0/Protocol0 (le Log.txt est tres bavard), on retire le prefixe "Protocol 0 - " et on
     colore en vert (rouge si erreur).
  2. [agent]   : %APPDATA%\\Protocol0\\logs\\agent.log.<date> -- l'agent Rust ecrit via
     tracing-appender en rotation par jour (on prend le plus recent, cf. _agent_log_path). On
     retire le prefixe "2026-...Z INFO Protocol0::<module>: " (redondant) et on colore en magenta.

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
# Prefixe a retirer en tete de ligne agent. Deux formats supportes :
#   - Rust (tracing, agent actuel) : "2026-06-05T10:02:02.411246Z  INFO Protocol0::web: msg"
#     (ISO-8601 avec T/Z, microsecondes, 2 espaces, niveau, "Protocol0::<module>: ").
#   - Python stdlib (ancien agent) : "2026-06-02 01:54:10,066 INFO agent: msg".
_AGENT_PREFIX_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?Z?\s+\w+\s+[\w:.]+: "
)
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


def _ableton_log_path():
    """Le Log.txt P0 le plus recent sous %APPDATA%\\Ableton\\Live *. None si introuvable.

    On prend le Log.txt modifie le plus recemment, point. C'est le Live actuellement lance
    (celui qui ecrit en ce moment), qu'il soit stable ou beta : l'utilisateur peut tourner sur
    un build beta (ex. "Live 12.4.5b3") plus recent que toute version stable installee. Filtrer
    les beta nous faisait retomber sur une vieille stable qui n'ecrit plus rien.
    """
    root = Path(os.environ.get("APPDATA", "")) / "Ableton"
    candidates = [
        p / "Preferences" / "Log.txt"
        for p in root.glob("Live *")
        if (p / "Preferences" / "Log.txt").exists()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _agent_log_path():
    """Le fichier de log de l'agent le plus recent.

    L'agent Rust ecrit via tracing-appender en rotation par jour : le nom reel est
    `agent.log.YYYY-MM-DD` (PAS `agent.log` tout court, qui peut exister mais vide -- p.ex. le
    sink stdout du service sous `make up`). On prend donc le `agent.log*` non vide le plus
    recemment modifie. None si aucun (l'agent n'a pas encore tourne) -> _follow attend sa
    creation, mais comme le nom contient la date, on resout au lancement de `make logs`.
    """
    logs_dir = Path(os.environ.get("APPDATA", "")) / "Protocol0" / "logs"
    candidates = [p for p in logs_dir.glob("agent.log*") if p.is_file() and p.stat().st_size > 0]
    if not candidates:
        # Rien encore : on renvoie le nom du fichier date du jour pour que _follow l'attende.
        return logs_dir / ("agent.log.%s" % time.strftime("%Y-%m-%d"))
    return max(candidates, key=lambda p: p.stat().st_mtime)


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
