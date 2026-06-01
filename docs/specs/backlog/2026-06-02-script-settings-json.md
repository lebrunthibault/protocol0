# Config du remote script via settings.json (%APPDATA%)

En prod (install par exe, Jalon 1), le remote script n'a **pas** de `.env` à lire :
les ports/URLs étaient lus via `protocol0.shared.env.get("P0_..._PORT")`, qui
renvoyait `None` et **crashait le chargement du script** dans Ableton
(`TypeError: can only concatenate str (not "NoneType") to str`).

Correctif appliqué au Jalon 1 (provisoire) : valeurs **en dur** dans le code :
- `HttpServer.py` → `_PORT = 9000`
- `BackendClient.py` → `_BASE_URL = "http://127.0.0.1:9001"`

Cette spec vise à rendre ces valeurs **configurables** proprement, sans `.env`.

## But

Lire la config du script depuis un fichier **`%APPDATA%\Protocol0\settings.json`**
(même dossier que `shortcuts.json`), avec des **défauts câblés** quand le fichier
ou une clé est absent — pour ne jamais re-crasher au chargement.

Schéma proposé :
```json
{
  "version": 1,
  "script_port": 9000,
  "backend_url": "http://127.0.0.1:9001"
}
```

## Périmètre

- Un petit lecteur stdlib (remplace/réutilise `protocol0/shared/env.py`, devenu
  mort code après le passage en dur) : lit `settings.json`, tolérant (défauts si
  absent/corrompu, jamais d'exception au chargement — même esprit que
  `detector/config.py` et `ShortcutConfigService`).
- Remplacer les deux valeurs en dur :
  - `HttpServer.py:_PORT` → `settings.script_port` (défaut 9000)
  - `BackendClient.py:_BASE_URL` → `settings.backend_url` (défaut `http://127.0.0.1:9001`)
- Cohérence avec le **detector**, qui lit déjà son port via `P0_SCRIPT_PORT`
  (défaut 9000, cf. `src/detector/detector/settings.py`). Idéalement, les deux
  composants partagent la même source de vérité pour le port du script — à
  arbitrer : le detector pourrait aussi lire `settings.json`, ou garder l'env var.

## Hors périmètre

- UI d'édition de `settings.json` (édition manuelle suffit au début).
- Distribution d'un `settings.json` par défaut par l'installeur (les défauts
  câblés couvrent le cas « fichier absent »).

## Notes

- `BackendClient` n'est de toute façon pas exercé tant que le backend est en pause
  (constitution §5) ; mais son **import** doit réussir, d'où le besoin d'un défaut
  qui ne crashe pas.
- Penser à supprimer les `TODO` laissés dans `HttpServer.py` et `BackendClient.py`
  qui pointent vers cette spec.
