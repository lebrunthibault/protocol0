"""Serveur web de l'agent : sert la SPA Vue 3 (build statique) + l'API /api + /status.

Remplace l'ancien launcher.py (page inline + redirect). Démarré sur un thread daemon
depuis agent.main, port fixe 9010.
"""
from agent.web.server import start, stop

__all__ = ["start", "stop"]
