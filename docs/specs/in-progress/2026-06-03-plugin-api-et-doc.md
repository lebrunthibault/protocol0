# API de plugins déclarative + documentation

Le remote script a déjà un embryon de système de plugins
(`src/script/protocol0/application/plugin/`) mais il est **minimal et
sous-documenté** :

- `PluginInterface` n'expose que `name`, `should_start()`, `start()`, `stop()`.
  Un plugin qui veut réagir à des events doit appeler **manuellement**
  `DomainEventBus.subscribe(...)` dans `start()` puis `un_subscribe(...)` dans
  `stop()` (cf. `LiveSetPlugin`) — verbeux et facile à oublier (fuite de
  listeners).
- Un plugin n'a **pas de point de déclaration explicite** pour exposer une
  action : les actions vivent dans `application/http/routes/` via `@route`, et
  rien dans l'interface plugin ne dit « voici les routes que j'ajoute ».
  (Contexte : le `ActionCatalog`/allow-list `/actions` du script a été
  **supprimé** au commit `fac73a57` — l'agent SPA détient désormais la GUI
  keymapper ; le script ne garde que `/api/health`, `/docs`, et ses routes
  d'action sous `/api`. Une action de plugin est donc simplement une **route
  HTTP** (`@api_route`), visible dans la Swagger UI `/docs` / `/openapi.json`
  via `get_routes()` et appelée par l'agent au keypress. Cf. spec
  `2026-06-04-script-rest-api-and-swagger.md`.)
- Le seul plugin existant (`LiveSetPlugin`) est **entièrement hardcodé** au set
  perso de l'auteur (BASS/SYNTH/PIANO/VOCALS) — il n'illustre pas une création
  de plugin générique.
- La doc promet l'extensibilité sans la livrer : `README.md` dit *« you can add
  new actions by creating a plugin (doc to come) »*, et `CONSTITUTION.md` parle
  d'actions « discoverable » mais aucune page n'explique comment écrire un plugin.

But : s'inspirer de l'[API plugin de beets](https://beets.readthedocs.io/en/stable/dev/plugins/index.html)
pour rendre l'écriture d'un plugin **déclarative** (hooks d'events +
enregistrement d'actions), puis **documenter** l'extensibilité dans
`CONSTITUTION.md`, `README.md` (→ `docs/plugins.md`) et le site
(`src/website/docs/`).

## Inspiration beets

| Capacité beets | Équivalent Protocol0 |
|---|---|
| `BeetsPlugin` base class | `PluginInterface` enrichie |
| `register_listener(event, fn)` | `register_listeners()` → câblé sur le `DomainEventBus` existant |
| `commands()` (sous-commandes CLI) | `register_actions()` → routes `@api_route` exposées dans `/docs` (Swagger) |
| `config['plugin']` | **Hors lot** — délégué au spec `2026-06-02-script-settings-json.md` |

On garde la contrainte **stdlib-only** (Ableton, cf. `CONSTITUTION.md §2`) : pas
de nouvelle dépendance, le mécanisme reste de l'introspection + le
`DomainEventBus`/`Router` déjà en place.

## Décisions

1. `PluginInterface` gagne deux hooks **optionnels** déclaratifs :
   - `register_listeners() -> Dict[Type, Callable]` : map *type d'event →
     handler*. Abonnés automatiquement après `start()`, **désabonnés
     automatiquement** au `stop()` par le loader (le plugin n'appelle plus jamais
     `subscribe`/`un_subscribe` à la main).
   - `register_actions() -> List[Callable]` : liste de fonctions **décorées
     `@route`**. Elles s'enregistrent dans le `Router` à l'import du module
     (comportement `@route` existant) et apparaissent donc sur l'index `/`. Le
     hook sert de **point de déclaration explicite** (clarté + log au démarrage) ;
     le loader ne re-enregistre rien (pas de catalogue à alimenter).
2. `start()` / `stop()` deviennent **optionnels** (défaut `pass` au lieu de
   `raise NotImplementedError`) : un plugin purement déclaratif n'écrit que
   `register_listeners` / `register_actions`.
3. **Option d'enregistrement des actions retenue : A** (décorateur `@route` sur
   les méthodes/fonctions renvoyées). Plus simple que d'extraire un
   `Router.register`, et compatible avec l'ordre d'init actuel
   (`PluginLoader.load_and_start` s'exécute **avant** `HttpServer.start`, mais le
   registre `_ROUTES` est global donc l'ordre n'impacte pas le dispatch).
4. Pas de dépendance à un catalogue (il n'existe plus côté script) : une action
   de plugin est une route HTTP, découvrable dans la Swagger UI `/docs` /
   `/openapi.json` comme les routes core. (NB : l'index HTML `/` a été remplacé
   par la doc OpenAPI — cf. spec `2026-06-04-script-rest-api-and-swagger.md` ;
   les `@route` deviennent `@api_route`.)
5. Un **plugin d'exemple générique** (`plugins/example/ExamplePlugin.py`) sert de
   template documenté, **désactivé par défaut** (`should_start()` → `False`) pour
   ne pas polluer l'usage réel.
6. `LiveSetPlugin` est **migré** vers `register_listeners()` (suppression du
   boilerplate `subscribe`/`un_subscribe`), à comportement constant.

## Architecture cible

```
PluginLoader.load_and_start(plugins_package)
   │ import_package → découvre PluginInterface.__subclasses__()
   ▼
 pour chaque plugin (should_start() == True) :
   plugin.start()                              # init optionnelle
   for evt, fn in plugin.register_listeners(): # NOUVEAU
       DomainEventBus.subscribe(evt, fn)       #   loader mémorise (evt, fn)
   plugin.register_actions()                   # NOUVEAU (déclaratif + log ;
                                               #   routes déjà câblées par @route)
   ...
 à l'arrêt (ScriptDisconnectedEvent) → _stop_all :
   for evt, fn in listeners du plugin: un_subscribe(evt, fn)   # cleanup auto
   plugin.stop()
```

## Contraintes vérifiées dans le code

- `PluginLoader.load_and_start` tourne **avant** `HttpServer.start(container)`
  (`Protocol0._initialize`) → l'enregistrement des routes plugin via `@route`
  (registre global `_ROUTES`) reste visible au dispatch. OK.
- `DomainEventBus.subscribe` warn sur doublon → le loader ne doit abonner qu'une
  fois par (event, handler).
- Ne jamais bloquer le thread Live (principe `CONSTITUTION.md §2`) : les actions
  passent par le pont HTTP→Live existant, inchangé.

## M1 — API plugin déclarative (code)

**But** : un plugin déclare listeners + actions ; le loader câble et nettoie.

**Fichiers**
- `application/plugin/PluginInterface.py` — ajouter `register_listeners`,
  `register_actions` (défauts vides) ; `start`/`stop` → `pass`.
- `application/plugin/PluginLoader.py` — après `start()`, abonner les listeners
  (et les mémoriser pour le cleanup), logger les actions déclarées ; `_stop_all`
  désabonne les listeners puis appelle `stop()`.

## M2 — Plugin d'exemple minimal (code)

**Nouveau fichier** : `plugins/example/ExamplePlugin.py` (+`__init__.py`).
Template court (~30-40 lignes), générique (aucun set précis), **désactivé par
défaut** :
- un listener sur un event toujours dispo (`SongStartedEvent`) qui logge un
  message ;
- une action générique `@route` (ex. `/example/hello`) qui affiche un message via
  `StatusBar`.

## M3 — Documentation

1. `docs/plugins.md` (nouveau) — guide de référence : ce qu'est un plugin, où ils
   vivent, découverte, cycle de vie, `register_listeners` (+ table des events
   utiles), `register_actions` (apparition au catalogue + raccourcis), le plugin
   exemple, contraintes (stdlib-only, thread Live). Renvoie au spec
   `settings.json` pour la config.
2. `README.md` — remplacer le placeholder *« plugin (doc to come) »* par un lien
   `[creating a plugin](docs/plugins.md)`.
3. `CONSTITUTION.md §2` — sous-section durable *« Plugins extend the catalog »*
   (intention *what/why*, pas de code), reliée à *« Actions form a discoverable
   catalog »*. Rester générique.
4. `src/website/docs/plugins.html` (nouveau, calqué sur `http-api.html`) + entrée
   sidebar `Creating plugins` sur les 5 pages docs + correction des liens
   prev/next.

## Risques

1. **Fuite de listeners si le cleanup oublie un handler.** Mitigation : le loader
   est l'unique propriétaire du couple (event, handler) ; `_stop_all` itère
   exactement ce qu'il a abonné.
2. **Doublon d'abonnement** (warn `DomainEventBus`). Mitigation : abonner une
   seule fois, à la charge du loader.
3. **Action plugin cassant le chargement du script.** Mitigation : le
   `try/except` par plugin de `load_and_start` isole déjà un plugin défaillant.

## Hors périmètre

- Config par plugin → spec `2026-06-02-script-settings-json.md`.
- Métadonnées riches (version, deps, auteur) : on garde `name` + docstring.
- Système de plugins tiers/packaging externe (les plugins vivent dans l'arbre).
