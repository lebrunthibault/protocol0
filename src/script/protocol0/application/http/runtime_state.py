"""Fichier d'état runtime publié par le script à %APPDATA%\\Protocol0\\runtime.json.

Le script choisit son port d'écoute dynamiquement (cf. HttpServer : 9000, sinon un
port libre). Le detector — qui vit hors d'Ableton et survit à ses redémarrages — n'a
aucun moyen de deviner ce port. On le publie donc ici : le script écrit l'URL effective
au démarrage du serveur et supprime le fichier à l'arrêt (disconnect). L'absence du
fichier vaut "script pas actif" pour les lecteurs (detector, launcher).

Tourne dans le Python embarqué d'Ableton : stdlib uniquement (json, os).
"""
import json
import os


def runtime_path() -> str:
    return os.path.join(os.environ["APPDATA"], "Protocol0", "runtime.json")


def write(script_url: str, pid: int, version: str) -> None:
    """Publie l'URL effective du serveur. Écriture atomique : on dump dans un .tmp
    puis os.replace (atomique sur Windows, même dossier) -> un lecteur ne voit jamais
    un fichier à moitié écrit, seulement l'ancien complet ou le nouveau complet."""
    path = runtime_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    payload = {"script_url": script_url, "pid": pid, "version": version}
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def clear() -> None:
    """Supprime le fichier (appelé à l'arrêt du serveur). Idempotent."""
    try:
        os.remove(runtime_path())
    except OSError:
        pass
