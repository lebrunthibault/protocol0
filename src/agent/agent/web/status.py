"""Diagnostic de la connexion Ableton : 3 états calculés par l'agent.

Porté de l'ancien launcher.py. Le redirect navigateur (-> script_url + /shortcuts) est
SUPPRIMÉ : l'agent possède désormais le GUI. La SPA consomme cet état pour son StatusPill.

  - no_ableton      : process Ableton absent.
  - script_inactive : Ableton lancé mais le serveur du script injoignable (pas activé / figé).
  - ready           : script joignable -> son URL est renvoyée (pour info ; l'édition n'en
                      dépend pas, seul le déclenchement d'actions l'utilise via le listener).
"""
import requests

from agent import process_check, runtime_state


def compute() -> dict:
    if not process_check.ableton_is_running():
        return {"state": "no_ableton"}
    rt = runtime_state.read()
    if rt and _ping(rt["script_url"]):
        return {"state": "ready", "script_url": rt["script_url"]}
    return {"state": "script_inactive"}


def _ping(script_url: str) -> bool:
    try:
        r = requests.get(script_url + "/health", timeout=1)
        return r.status_code == 200
    except requests.RequestException:
        return False
