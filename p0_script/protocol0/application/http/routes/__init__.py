# L'import de chaque module ici déclenche l'enregistrement des routes via
# le décorateur @route au moment où HttpServer.start() importe ce package.
from protocol0.application.http.routes import device_routes  # noqa: F401
from protocol0.application.http.routes import track_routes  # noqa: F401
