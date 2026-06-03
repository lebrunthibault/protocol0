# Script HTTP : vraie API REST sous `/api` + doc Swagger sous `/docs`

## Problème

Le serveur HTTP du **remote script** (dans Ableton, `127.0.0.1:9000`,
`src/script/protocol0/application/http/`) ne ressemble pas à une vraie API REST :

- `GET /` sert une **page HTML** (l'index `index_routes.index()` qui liste les
  routes dans un `<table>`) — un serveur d'API ne devrait pas servir du HTML à la
  racine.
- Les routes d'action vivent **à la racine** (`/device/load`, `/track/select`,
  `/song/toggle_follow`, `/clip/key_detected`, `/set/get_state`) — pas de
  namespace qui les distingue d'une éventuelle surface humaine.
- Les **mutations passent par `GET`** (`/device/load?name=…` charge un device).
  C'est l'anti-pattern que toutes les API de référence interdisent.
- Aucune **doc machine-lisible** : la seule « doc » est la page HTML d'index.

But : faire du script une **vraie API REST JSON** — `/api/*` pour les actions,
`/docs` pour une **vraie Swagger UI**, `/api/health` conservé comme sonde +
porteur de version. Pas de HTML servi par l'API hors `/docs`.

> Note : `/shortcuts` **n'est pas** servi par le script (retiré au commit
> `fac73a57`) — il vit dans l'**agent** (`:9010/api/shortcuts`). Ce que
> `:9000/` sert aujourd'hui, c'est la page d'index HTML. Ce spec ne touche **que
> le script** (`:9000`) ; l'agent (`:9010`) a déjà un split `/api/*` + SPA propre
> et reste hors scope.

## Contrainte structurante

Le script tourne **dans l'interpréteur d'Ableton : stdlib-only** (cf.
`CONSTITUTION.md §2`). Pas de FastAPI/Flask. Tout — routage, OpenAPI, Swagger UI —
doit se faire à la main avec `http.server` + introspection, comme le
`Router.py`/`index_routes.py` actuels.

## Recherche OSS (références citées)

Étude menée via la skill `oss-best-practices` contre 5 API de contrôle localhost
comparables :

| Projet | Prefix | Versioning URL | OpenAPI/Swagger | Mutation via GET ? | HTML à la racine API ? |
|---|---|---|---|---|---|
| **beets** (peer le plus proche) | aucun | non | non (prose) | non (PATCH/DELETE) | SPA `/`, JSON ailleurs |
| **Syncthing** | `/rest/` | non | non (prose) | non (POST même pour « scan ») | JSON pur, UI sur `/` |
| **Transmission** | `/transmission/rpc` | in-band semver | non (prose) | POST-only JSON-RPC | JSON pur, UI séparée |
| **Jupyter Server** | `/api/` | dans `info.version` du spec | **oui — `api.yaml` statique** | non | JSON-only |
| **Home Assistant** | `/api/` | non (URL) | non (prose) | non (POST) | JSON-only |

**Convergence :** API préfixée + UI humaine sur un chemin séparé ; **jamais de
mutation via GET** (unanime) ; **pas de version dans l'URL** (aucun des 5) ; la
racine de l'API renvoie du JSON, pas du HTML. `/api` est le prefix idiomatique
majoritaire (Jupyter + Home Assistant).

**Divergence :** seul Jupyter sert de l'OpenAPI — et il prouve qu'un serveur
stdlib-only **peut** servir du Swagger : un `api.yaml` statique embarqué + lien
viewer externe, zéro machinerie serveur.

Sources : [beets web](https://github.com/beetbox/beets/blob/master/beetsplug/web/__init__.py)
· [Syncthing REST](https://docs.syncthing.net/dev/rest.html)
· [Syncthing CSRF](https://github.com/syncthing/syncthing/blob/main/lib/api/api_csrf.go)
· [Transmission rpc-spec](https://github.com/transmission/transmission/blob/main/docs/rpc-spec.md)
· [Jupyter api.yaml](https://github.com/jupyter-server/jupyter_server/blob/main/jupyter_server/services/api/api.yaml)
· [Jupyter REST docs](https://jupyter-server.readthedocs.io/en/latest/developers/rest-api.html)
· [Home Assistant REST](https://developers.home-assistant.io/docs/api/rest/)

## Décisions (validées)

1. **Prefix `/api`, sans version.** `/api/device/load`, `/api/track/select`, etc.
   Pas de `/v1` dans l'URL (aucune référence ne le fait pour du localhost
   mono-consommateur ; évolution additive). `GET /api/health` conservé comme
   sonde **et** porteur de version (`{ok, version}`) — c'est le « version value »
   à la Jupyter/Syncthing.
2. **Mutations en `POST`, jamais en `GET`.** On suit la règle unanime des
   références. `GET` réservé aux lectures pures (`/api/set/state`,
   `/api/health`). **Conséquence assumée** : un Stream Deck « open URL » (GET
   seul) ne peut plus déclencher une action directement → voir « Stream Deck »
   ci-dessous.
3. **`GET /openapi.json` généré dynamiquement depuis `get_routes()`.** Le
   `Router` introspecte déjà method/path/params/docstring (cf.
   `index_routes._row`). On réutilise cette introspection pour produire un
   document **OpenAPI 3.1** à la volée → les routes de **plugins** (`@route` via
   `register_actions()`, cf. spec `2026-06-03-plugin-api-et-doc.md`) apparaissent
   **automatiquement**, sans YAML à maintenir. Une coche au-dessus de Jupyter
   (qui hand-write son `api.yaml`).
4. **Swagger UI vendorée à `/docs`.** On embarque le dist statique Swagger UI
   dans le package du script (`application/http/swagger_ui/`), servi par une route
   `GET /docs` qui pointe sur `/openapi.json`. Marche **offline**, pas de
   dépendance CDN, `/docs` self-contained.
5. **`GET /` ne sert plus de HTML.** Remplacé par un **redirect 302 vers
   `/docs`** (surface humaine = Swagger). L'API ne sert du HTML qu'à `/docs` (+
   les assets statiques Swagger). L'ancienne page d'index `index()` est
   supprimée.
6. **Stream Deck : POST partout, on assume.** L'exemple « open URL » est **retiré**
   de la doc. Un Stream Deck devra passer par un POST (relais/plugin/agent) ; on
   documente la migration GET→POST. Garde l'API pure.

## Surface cible

```
GET  /                      → 302 redirect vers /docs
GET  /docs                  → Swagger UI (HTML, vendorée), lit /openapi.json
GET  /openapi.json          → OpenAPI 3.1 généré depuis get_routes()
GET  /api/health            → {ok, version}      (sonde + version)
GET  /api/set/state         → état sérialisé du set (lecture pure)
POST /api/device/load       → charge un device (body ou query: name)
POST /api/track/select      → sélectionne une track (name)
POST /api/song/toggle_follow→ stop follow playhead
POST /api/clip/key_detected → notifie une key détectée (pitch)
POST /api/example/hello     → plugin d'exemple
```

Classement lecture/mutation (relevé dans le code actuel) :
- **lecture (GET)** : `set/get_state` (renvoie un dict, idempotent).
- **mutations (POST)** : `device/load`, `track/select`, `song/toggle_follow`,
  `clip/key_detected`, `example/hello` (effets de bord sur Live).

## Impact / consommateurs à migrer

Toutes ces routes sont appelées en GET aujourd'hui — **breaking change** :

| Consommateur | Fichier | Changement |
|---|---|---|
| Agent (keypress → action) | `src/agent/agent/script_client.py` | `_get(base,"/device/load")` → `POST base+"/api/device/load"` |
| Extension JS (spike SDK) | `src/js-extension/src/extension.ts` | `/device/load`, `/track/select`, `/health` → `/api/...` + POST |
| Doc site | `src/website/docs/http-api.html` | base URL, `/api/*`, GET→POST, **retirer l'exemple Stream Deck open-URL**, retirer le renvoi vers l'index HTML `/` (→ `/docs`) |
| Doc repo | `docs/plugins.md`, `CONSTITUTION.md` | « découvrable sur l'index `/` » → « découvrable dans `/docs` / `/openapi.json` » |
| Vue ApiDocsView | `src/frontend/src/views/ApiDocsView.vue` | vérifier qu'elle ne hardcode pas les chemins du script |
| Spec plugin en cours | `docs/specs/in-progress/2026-06-03-plugin-api-et-doc.md` | mettre à jour la promesse « visible sur l'index `/` » → Swagger/openapi |
| `index_routes.py` | script | supprimer `index()` (HTML) ; `health()` → `/api/health` ; ajouter `/`, `/docs`, `/openapi.json` |

## Plan d'implémentation

### M1 — Router : prefix `/api`, dispatch POST, helpers méthode

**Fichiers** : `application/http/Router.py`, `application/http/HttpServer.py`

- `Router` : ajouter `do_POST` au `HttpRequestHandler` (lire le body, parser le
  JSON ou les query params — calquer `agent/web/api._parse_input`). Le dispatch
  matche `(method, path)` comme aujourd'hui (le registre `_ROUTES` est déjà clé
  `(method, path)`).
- Décider du portage du prefix `/api` : option simple = les `@route` déclarent le
  chemin **complet** (`/api/device/load`). Option DRY = `@route` garde le chemin
  court et le Router préfixe `/api` au matching. **Retenu : chemin court +
  préfixe au matching** (les routes core et plugins n'ont pas à répéter `/api`,
  et `/health`/`/docs`/`/` restent hors prefix). Documenter ce choix dans
  `Router.py`.
- Coercition des params : réutiliser `_coerce` pour les query GET ; pour POST,
  lire le body JSON.

### M2 — Génération OpenAPI + Swagger UI

**Nouveaux fichiers** : `application/http/openapi.py`,
`application/http/swagger_ui/` (dist vendorée), routes dans `index_routes.py`.

- `openapi.py` : `build_spec()` itère `get_routes()`, mappe chaque
  `(method, path, fn)` vers un Path Item OpenAPI 3.1 — `summary` =
  `inspect.getdoc(fn)`, `parameters` (query pour GET) / `requestBody` (JSON pour
  POST) dérivés de `inspect.signature`. Réutilise la logique de
  `index_routes._param_label`. `info.version = __version__`.
- `index_routes.py` :
  - supprimer `index()` (HTML) et ses helpers `_row`/`_param_label` (déplacer la
    logique utile dans `openapi.py`).
  - `GET /` → `302 Location: /docs`.
  - `GET /openapi.json` → `json.dumps(build_spec())`, `application/json`.
  - `GET /docs` → sert `swagger_ui/index.html` (vendoré), configuré sur
    `/openapi.json`.
  - `GET /api/health` (déplacer `/health`).
- `HttpRequestHandler` doit savoir servir des **assets statiques** (le dist
  Swagger : `swagger-ui.css`, `swagger-ui-bundle.js`, …) avec le bon
  `Content-Type` — petit resolver type `agent/web/static_files`.

### M3 — Migrer les routes d'action sous POST + `/api`

**Fichiers** : `application/http/routes/*.py`

- Annoter `device/load`, `track/select`, `song/toggle_follow`,
  `clip/key_detected` en `@route("POST", …)`. `set/get_state` reste `GET`.
- (Plugin) `example/hello` → POST (cf. spec plugin).

### M4 — Migrer les consommateurs

- `src/agent/agent/script_client.py` : `POST {base}/api/device/load` (body JSON
  `{name}`), gérer le nouveau prefix. Adapter `_get` → `_post`.
- `src/js-extension/src/extension.ts` : `/api/*` + POST + `/api/health`.
- Vérifier `src/frontend/src/views/ApiDocsView.vue` (pas de chemin script
  hardcodé cassé).

### M5 — Documentation

- `src/website/docs/http-api.html` : base URL inchangée (`:9000`), routes `/api/*`,
  GET→POST, **retirer l'exemple Stream Deck open-URL** (ou le remplacer par un
  exemple `curl -X POST`), remplacer le renvoi vers `/` par `/docs`.
- `docs/plugins.md`, `CONSTITUTION.md` : « découvrable sur `/` » → « découvrable
  dans `/docs` (Swagger) / `/openapi.json` ».
- `docs/specs/in-progress/2026-06-03-plugin-api-et-doc.md` : aligner la promesse
  d'index.

### M6 — Tests

- Adapter `src/agent/tests/test_web_api.py` / `test_static_files.py` si touchés
  (ils visent l'agent — vérifier qu'ils ne testent pas le script).
- Ajouter un test script : `GET /openapi.json` renvoie un doc valide listant les
  routes ; `GET /` redirige vers `/docs` ; `POST /api/track/select` dispatche ;
  `GET /api/device/load` (ancienne forme) renvoie 404/405.

## Stream Deck (conséquence de POST)

L'exemple « bouton open-URL » du Stream Deck **disparaît** : `GET` ne mute plus.
Un Stream Deck qui veut déclencher une action devra émettre un **POST** (plugin
Stream Deck « HTTP Request », relais, ou via l'agent). On le documente comme
migration. C'est le coût assumé de la pureté REST (cf. décision 6).

## Risques

1. **Breaking change pour l'agent.** Si on déploie le script avant l'agent, les
   keypress échouent (404 sur l'ancienne route GET). → Migrer
   `script_client.py` **dans le même lot** et bumper ensemble.
2. **Poids du dist Swagger UI committé.** Vendorer ajoute quelques fichiers
   JS/CSS au repo. → Garder uniquement les assets nécessaires (`swagger-ui.css`,
   `swagger-ui-bundle.js`, `index.html` minimal), pas tout le package npm.
3. **OpenAPI 3.1 généré incomplet** (types params approximatifs). → Acceptable :
   l'introspection donne déjà nom/type/required/docstring ; on n'a pas besoin de
   schémas riches pour une API d'actions.
4. **Le spec plugin en cours** suppose la découverte sur `/` — coordonner les
   deux specs (celui-ci reformule cette promesse vers `/docs`).

## Hors périmètre

- L'agent (`:9010`) — déjà propre (`/api/*` + SPA), pas touché ; aligner
  `/status` → `/api/status` reste une note future, pas ce lot.
- Durcissement CSRF/Origin : la décision POST rend le sujet moins pressant (plus
  de GET-mutation) ; un check Origin reste possible plus tard mais hors scope.
- Auth / API key : localhost-only, hors scope (comme aujourd'hui).
