"""Lance l'agent + le frontend Vue + la landing website en arriere-plan (target `make up`).

Pourquoi : en dev on jonglait avec deux/trois terminaux (`make agent`, `make frontend`,
`make website`). `make up` demarre les trois d'un coup en process detaches, redirige leurs
sorties vers %APPDATA%\\Protocol0\\logs\\*.log, et memorise les PID dans
%APPDATA%\\Protocol0\\dev-up.json pour que `make down` (scripts/down.py) puisse tout couper.

Apres avoir lance les trois, `make up` affiche les URLs effectives (les ports ne sont pas
fixes : un autre projet peut tenir 5173/8000, donc vite/live-server prennent le premier port
libre) puis REND LA MAIN : les services tournent en background (detaches). On n'enchaine pas
sur le tail -- l'utilisateur lance `make logs` quand il veut suivre Ableton + agent, et
`make down` pour tout couper. Les logs des trois services sont dans %APPDATA%\\Protocol0\\logs\\
(agent.log, frontend.log, website.log).

On tue d'abord les agents qui trainent (cf. kill_agent.py / docs/debug-double-shortcut.md)
pour garantir un seul agent. L'agent lance est le binaire Rust (src/agent), build a la
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

_DEFAULT_FRONTEND_PORT = 5173


def _frontend_port() -> int:
    """Port du dev server vite, lu dans l'environnement (FRONTEND_PORT), defaut 5173 (le defaut
    Vue). Le Makefile charge le .env de la racine (`-include .env` + `export`) avant d'appeler ce
    script, donc on lit juste os.environ ici -- pas de parsing de fichier cote Python. .env est
    gitignore : chaque dev fixe son port s'il a un conflit (autre projet Vue tenant deja 5173).
    Voir .env.example. Une valeur non numerique retombe sur le defaut."""
    value = os.environ.get("FRONTEND_PORT", "")
    return int(value) if value.isdigit() else _DEFAULT_FRONTEND_PORT

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
    return _REPO / "src" / "agent" / "target" / "release" / "Protocol0.exe"


def _build_rust_agent() -> bool:
    """`cargo build --release` du crate src/agent. True si l'exe est pret, False sinon.

    cargo ecrit sa progression sur stderr ; on juge le succes sur le returncode (pas sur la
    presence de stderr). On herite stdout/stderr du terminal pour que l'utilisateur voie la
    compilation (premier run ~20s, incremental quasi instantane)."""
    print("Building Rust agent (cargo build --release)...", flush=True)
    try:
        rc = subprocess.run(
            ["cargo", "build", "--release"],
            cwd=str(_REPO / "src" / "agent"),
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


def _spawn(log_name: str, args, cwd: Path) -> int:
    """Lance `args` detache, stdout+stderr -> logs/<log_name>.log. Retourne le PID."""
    # Mode "w" : on repart d'un log vierge a chaque `make up` (sinon on relit le run
    # precedent et on se croit sur le mauvais port).
    log_path = _state_dir() / "logs" / ("%s.log" % log_name)
    log = open(log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        args,
        cwd=str(cwd),
        stdout=log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=_DETACHED,
        # shell=True : npx/live-server sont des .cmd sous Windows, introuvables sans le shell.
        # L'exe agent (chemin absolu) marche aussi via le shell.
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

    # L'agent lance par `make up` est le binaire Rust (src/agent), comme `make agent` et
    # comme l'installeur. On le build AVANT de le spawn : sinon l'exe peut etre absent (premier
    # run) ou perime. Build bloquant (cargo est rapide en incremental) ; si le build echoue, on
    # s'arrete plutot que de lancer un vieux binaire.
    if not _build_rust_agent():
        return 1

    # Frontend : on choisit NOUS-MEMES le port (5173 s'il est libre, sinon 5174, 5175...) puis on
    # Frontend : port lu dans l'env (FRONTEND_PORT, defaut 5173 ; le Makefile charge .env. Cf.
    # _frontend_port / .env.example).
    # On le passe a vite en --strictPort -> vite prend CE port ou echoue clairement, jamais un
    # co-bind silencieux. Si 5173 est deja pris par un autre projet Vue, le dev met FRONTEND_PORT=5174
    # (ou autre) dans son .env. On connait le port AVANT de lancer vite -> banner direct, sans
    # parser le log.
    front_port = _frontend_port()
    frontend_cmd = ["npm", "run", "dev", "--", "--port", str(front_port), "--strictPort"]
    front_url = "http://localhost:%d" % front_port

    # Website : un autre projet peut occuper 8080. live-server prend le premier port libre ; on lit
    # l'URL effective dans son log pour l'afficher (cf. _effective_url). `make up PORT=3000` force
    # quand meme le website sur un port precis.
    # Chemin ABSOLU obligatoire : _kill_stale_web identifie nos serveurs au chemin du repo dans
    # leur cmdline. Avec un chemin relatif, le live-server precedent n'est jamais reape, squatte
    # 8080, et chaque nouveau run derive sur un port aleatoire.
    port = os.environ.get("PORT")
    website_cmd = ["npx", "--yes", "live-server", str(_REPO / "src" / "website"), "--no-browser"]
    if port:
        website_cmd.append("--port=%s" % port)
    # NB: le sink stdout du service agent est "agent-stdout" (pas "agent.log") pour ne PAS
    # entrer en collision avec le vrai log de l'agent Rust, qui ecrit lui-meme dans
    # %APPDATA%\Protocol0\logs\agent.log.<date> via tracing-appender. Le stdout de l'exe est de
    # toute facon vide (tout passe par le fichier date) ; on le garde juste au cas ou (panic au
    # tout demarrage avant l'init du logger). `make logs` lit le fichier date, pas celui-ci.
    services = [
        # (label, command, cwd, log_name)
        ("agent", [str(_rust_agent_exe())], _REPO / "src" / "agent", "agent-stdout"),
        ("frontend", frontend_cmd, _REPO / "src" / "frontend", "frontend"),
        ("website", website_cmd, _REPO, "website"),
    ]

    pids = {}
    print("Starting dev stack in background:")
    for label, args, cwd, log_name in services:
        pid = _spawn(log_name, args, cwd)
        pids[label] = pid
        print("  %-9s PID %d  -> logs/%s.log" % (label, pid, log_name))

    _state_file().write_text(json.dumps(pids), encoding="utf-8")

    # Le port frontend est deja connu (lu dans .env, defaut 5173 ; force a vite en --strictPort),
    # donc rien a attendre cote vite. Seul le website peut deriver (live-server choisit son port) :
    # on poll son log pour l'URL effective. npx met ~5s a lancer live-server, d'ou la marge ; le
    # poll s'arrete des que l'URL est ecrite. Non bloquant -- au-dela, "(starting)".
    site_re = r"Serving .* at https?://[^:]+:(\d+)"
    site_url = _poll_site_url(site_re, timeout_s=15.0)

    # front_url est exact (port choisi par nous, vite force dessus en --strictPort) -> on l'affiche
    # tel quel, jamais "(starting...)". Le frontend (live-reload) est ce que l'utilisateur ouvre
    # pour voir ses changes ; l'agent :9010 sert le dist/ builde (fige).
    banner = "\n".join([
        "",
        "Dev stack up:",
        "  frontend: %s  (live-reload — open this to see your changes)" % front_url,
        "  agent:    http://127.0.0.1:9010  (serves the built dist/)",
        "  website:  %s" % (site_url or "(starting... see logs/website.log)"),
        "  (make down to stop everything)",
        "",
    ])
    print(banner, flush=True)

    # On REND la main ici : les 3 services tournent en background (detaches). On n'enchaine
    # PAS sur le tail -- l'utilisateur fait `make logs` quand il veut suivre Ableton + agent,
    # et `make down` pour tout couper. (make up doit retourner, pas bloquer.)
    return 0


def _poll_site_url(site_re: str, timeout_s: float):
    """Poll le log du website jusqu'a `timeout_s` pour y lire son URL effective (live-server peut
    deriver de :8080), en affichant un petit spinner anime (in-place) pour ne pas paraitre fige.
    Retourne l'URL ou None si pas prete a temps (le banner affiche alors un fallback). Non
    bloquant au-dela de timeout_s. Le spinner s'efface avant le banner.

    Le frontend n'est PAS poll ici : son port est deja connu (lu dans .env, force a vite en
    --strictPort), donc rien a attendre de ce cote."""
    frames = "|/-\\"
    site_url = None
    interval = 0.2
    steps = max(1, int(timeout_s / interval))
    spinner_on = sys.stdout.isatty()  # pas de spinner si la sortie est redirigee (vers un fichier)
    for i in range(steps):
        site_url = _effective_url("website", site_re)
        if site_url:
            break
        if spinner_on:
            # \r ramene en debut de ligne ; on reecrit par-dessus a chaque frame.
            sys.stdout.write("\r  %s waiting for website... " % frames[i % len(frames)])
            sys.stdout.flush()
        time.sleep(interval)
    if spinner_on:
        sys.stdout.write("\r" + " " * 36 + "\r")  # efface la ligne du spinner
        sys.stdout.flush()
    return site_url


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _effective_url(name: str, pattern: str):
    """Lit le port reel dans logs/<name>.log (vite/live-server l'annoncent). None tant que la
    ligne n'est pas encore ecrite (la boucle d'appel re-essaie).

    On STRIP d'abord les codes couleur ANSI : vite colore sa ligne "Local:" et insere des
    sequences (\x1b[22m, \x1b[1m...) entre "Local" et ":", et juste avant le port. Sans ce strip,
    le pattern (qui attend "Local:" contigu et le port colle au "://...:") ne matche jamais et on
    reste bloque sur "(starting...)" alors que vite tourne. live-server n'emet pas de couleurs,
    donc ca ne change rien pour lui."""
    log_path = _state_dir() / "logs" / ("%s.log" % name)
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    text = _ANSI_RE.sub("", text)
    matches = re.findall(pattern, text)
    return ("http://localhost:%s" % matches[-1]) if matches else None


if __name__ == "__main__":
    sys.exit(main())
