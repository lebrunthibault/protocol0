"""Lance l'agent + le frontend Vue + la landing website en arriere-plan (target `make up`).

Pourquoi : en dev on jonglait avec deux/trois terminaux (`make agent`, `make frontend`,
`make website`). `make up` demarre les trois d'un coup en process detaches, redirige leurs
sorties vers %APPDATA%\\Protocol0\\logs\\*.log, et memorise les PID dans
%APPDATA%\\Protocol0\\dev-up.json pour que `make down` (scripts/down.py) puisse tout couper.

Apres avoir lance les trois, `make up` affiche les URLs effectives (les ports ne sont pas
fixes : un autre projet peut tenir 5173/8000, donc vite/live-server prennent le premier port
libre) puis enchaine direct sur le tail combine Ableton + agent (la logique de `make logs`).
Resultat : une seule commande, un seul terminal. Ctrl-C arrete le tail ; les services restent
en background (`make down` les coupe). Les logs frontend/website sont aussi dans le meme
dossier (frontend.log, website.log) si besoin.

On tue d'abord les agents qui trainent (cf. kill_agent.py / docs/debug-double-shortcut.md)
pour garantir un seul agent. L'agent lance est le binaire Rust (src/agent-rust), build a la
volee avant le spawn -- meme binaire que `make agent` et l'installeur. Stdlib uniquement,
Windows-only (chemins APPDATA, npx, cargo).
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import kill_agent

# CREATE_NO_WINDOW : aucune fenetre console (sinon shell=True ouvre un cmd.exe visible par
# service). La sortie est deja redirigee vers un fichier, donc rien a afficher.
# CREATE_NEW_PROCESS_GROUP : on peut cibler proprement l'arbre au moment du down.
_DETACHED = 0x08000000 | 0x00000200

_REPO = Path(__file__).resolve().parent.parent


def _state_dir() -> Path:
    d = Path(os.environ["APPDATA"]) / "Protocol0"
    (d / "logs").mkdir(parents=True, exist_ok=True)
    return d


def _state_file() -> Path:
    return _state_dir() / "dev-up.json"


_CREATE_NO_WINDOW = 0x08000000


def _kill_stale_web() -> None:
    """Tue le vite/live-server de CE repo qui traine (lancement manuel `make frontend`/
    `make website`, ou un `make up` precedent mal coupe). Sans ca, vite/live-server voient
    leur port occupe et basculent sur un port aleatoire -> on croit etre sur :5173/:8000
    alors que non.

    On exige a la fois (1) la signature vite/live-server ET (2) le chemin du repo dans la
    cmdline, pour ne JAMAIS tuer un serveur vite d'un IDE (WebStorm/PyCharm) ou d'un autre
    projet ouvert en parallele."""
    repo = str(_REPO).lower()
    for pid, _name, cmd in kill_agent._processes():
        low = cmd.lower()
        is_web = "vite" in low or "live-server" in low
        if is_web and repo in low:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True, text=True, timeout=10,
                creationflags=_CREATE_NO_WINDOW,
            )


def _rust_agent_exe() -> Path:
    """Chemin du binaire Rust produit par cargo (le meme que `make agent` lance)."""
    return _REPO / "src" / "agent-rust" / "target" / "release" / "Protocol0.exe"


def _build_rust_agent() -> bool:
    """`cargo build --release` du crate src/agent-rust. True si l'exe est pret, False sinon.

    cargo ecrit sa progression sur stderr ; on juge le succes sur le returncode (pas sur la
    presence de stderr). On herite stdout/stderr du terminal pour que l'utilisateur voie la
    compilation (premier run ~20s, incremental quasi instantane)."""
    print("Building Rust agent (cargo build --release)...", flush=True)
    try:
        rc = subprocess.run(
            ["cargo", "build", "--release"],
            cwd=str(_REPO / "src" / "agent-rust"),
            shell=True,  # cargo est sur le PATH via un .cmd shim sous Windows
        ).returncode
    except OSError as e:
        print("  cargo introuvable (%s). Installe Rust (rustup) + VS C++ Build Tools." % e)
        return False
    if rc != 0:
        print("  cargo build a echoue (exit %d)." % rc)
        return False
    if not _rust_agent_exe().exists():
        print("  build OK mais %s introuvable." % _rust_agent_exe())
        return False
    return True


def _spawn(name: str, args, cwd: Path) -> int:
    """Lance `args` detache, stdout+stderr -> logs/<name>.log. Retourne le PID."""
    # Mode "w" : on repart d'un log vierge a chaque `make up` (sinon on relit le run
    # precedent et on se croit sur le mauvais port).
    log_path = _state_dir() / "logs" / ("%s.log" % name)
    log = open(log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        args,
        cwd=str(cwd),
        stdout=log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=_DETACHED,
        # shell=True : npx/poetry sont des .cmd sous Windows, introuvables sans le shell.
        shell=True,
    )
    return proc.pid


def main() -> int:
    if sys.platform != "win32":
        print("make up: Windows-only (APPDATA, poetry, npx).")
        return 0

    # Idempotent : on nettoie d'abord tout ce qui pourrait trainer (agent en double, et
    # frontend/website d'un lancement precedent) pour repartir sur les ports nominaux.
    kill_agent.main()
    _kill_stale_web()

    # L'agent lance par `make up` est le binaire Rust (src/agent-rust), comme `make agent` et
    # comme l'installeur. On le build AVANT de le spawn : sinon l'exe peut etre absent (premier
    # run) ou perime. Build bloquant (cargo est rapide en incremental) ; si le build echoue, on
    # s'arrete plutot que de lancer un vieux binaire.
    if not _build_rust_agent():
        return 1

    # Pas de port fixe : un autre projet peut occuper 5173/8000. vite et live-server prennent
    # le premier port libre ; on lit l'URL effective dans leur log pour l'afficher (cf.
    # _effective_url). `make up PORT=3000` force quand meme le website sur un port precis.
    port = os.environ.get("PORT")
    website_cmd = ["npx", "--yes", "live-server", "src/website", "--no-browser"]
    if port:
        website_cmd.append("--port=%s" % port)
    services = [
        # (label, command, cwd)
        ("agent", [str(_rust_agent_exe())], _REPO / "src" / "agent-rust"),
        ("frontend", ["npm", "run", "dev"], _REPO / "src" / "frontend"),
        ("website", website_cmd, _REPO),
    ]

    pids = {}
    print("Starting dev stack in background:")
    for label, args, cwd in services:
        pid = _spawn(label, args, cwd)
        pids[label] = pid
        print("  %-9s PID %d  -> logs/%s.log" % (label, pid, label))

    _state_file().write_text(json.dumps(pids), encoding="utf-8")

    # On ne fixe pas les ports (un autre projet peut tenir 5173/8000) -> vite et live-server
    # choisissent le premier port libre. On poll leur log jusqu'a y lire le port EFFECTIF
    # (vite peut bufferiser sa ligne "Local:" qq secondes via npm->cmd sans TTY).
    front_re = r"Local:\s*https?://[^:]+:(\d+)"
    site_re = r"Serving .* at https?://[^:]+:(\d+)"
    front_url = site_url = None
    for _ in range(30):  # ~15s max (30 * 0.5s)
        front_url = front_url or _effective_url("frontend", front_re)
        site_url = site_url or _effective_url("website", site_re)
        if front_url and site_url:
            break
        time.sleep(0.5)

    banner = "\n".join([
        "",
        "Dev stack up:",
        "  frontend: %s" % (front_url or "(starting... see logs/frontend.log)"),
        "  website:  %s" % (site_url or "(starting... see logs/website.log)"),
        "  agent:    http://127.0.0.1:9010",
        "  (make down to stop everything)",
        "",
    ])
    print(banner, flush=True)  # flush: visible avant que le tail (logs.main) prenne la main

    # On enchaine direct sur le tail combine Ableton + agent : un seul terminal, une seule
    # commande. Ctrl-C arrete le tail (les services restent up en background ; `make down`
    # les coupe). C'est `make logs` sans avoir a la taper.
    import logs as _logs  # noqa: E402  (import tardif: meme dossier, deja sur sys.path)
    return _logs.main()


def _effective_url(name: str, pattern: str):
    """Lit le port reel dans logs/<name>.log (vite/live-server l'annoncent). None tant que la
    ligne n'est pas encore ecrite (la boucle d'appel re-essaie)."""
    log_path = _state_dir() / "logs" / ("%s.log" % name)
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    matches = re.findall(pattern, text)
    return ("http://localhost:%s" % matches[-1]) if matches else None


if __name__ == "__main__":
    sys.exit(main())
