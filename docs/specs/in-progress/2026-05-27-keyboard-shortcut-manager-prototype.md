# Prototype — Keyboard Shortcut Manager (détecteur local dédié)

## État d'avancement (reprise) — 2026-05-28

Branche : `keyboard-shortcut-manager-prototype`. Dernier commit : `74dce210`
(« Pivot keyboard detection out-of-process: dedicated local detector (M1) »).

- **Spike détection in-script : NO-GO** (voir « Verdict du spike M0 » plus bas).
  Code du spike créé puis **supprimé** dans la branche (aucune trace dans l'historique).
  Constitution mise à jour en conséquence (§3.1, §3.2, §4, §5, §5.1, §6).
- **M1 : FAIT & VALIDÉ end-to-end dans Live.** Détecteur `src/detector/` opérationnel :
  `ctrl+alt+e` → EQ Eight, `ctrl+alt+u` → Utility, foreground-only. Lancé en dev par
  `cd src/detector ; poetry run detector` (logs au terminal, Ctrl+C pour arrêter).
  Config de test posée : `%APPDATA%\Protocol0\shortcuts.json`.
- **Prochaine étape : M2** (catalogue `GET /actions` dérivé des `@route` +
  `ShortcutConfigService` côté script), puis **M3** (frontend HTML/JS inline servi
  par le script), puis **M4** (packaging Scheduled Task, différé).
- **Point d'attention M3** : la capture navigateur doit produire la **même chaîne
  canonique** que le détecteur. Côté détecteur, le nom de touche vient du **`vk`**
  (position physique) ; côté navigateur, utiliser **`e.code`** (idem) — pas `e.key`.

## Contexte

`constitution.md` fixe la vision : remplacer le gestionnaire de raccourcis natif
d'Ableton par un système **programmable, configurable et indépendant du set**.
Aujourd'hui la chaîne ne marche que par son extrémité droite — les actions existent
déjà via HTTP (`GET /device/load?name=…` sur `:9000`), déclenchées par AutoHotkey
(`mappings.ahk`). Manquent : la **détection** des raccourcis (sans AHK) et leur
**configuration** via une UI.

Action end-to-end visée (§6) : **charger un device par son nom** via un raccourci
configuré dans le frontend.

## Verdict du spike M0 (2026-05-28) : détection in-script = NO-GO

Le plan initial (détection clavier **dans le script**, §3.1 d'origine) a été testé par
un spike (`src/script/protocol0/plugins/keyboard/`, voir historique git de cette
branche). **Invalidé**, pour trois raisons indépendantes — chacune suffisante :

1. **Pas de `ctypes`.** Le Python embarqué d'Ableton (build statique `win_64_static`)
   n'a ni le package `ctypes`, ni `_ctypes.pyd`, ni **aucune** extension C, ni
   `python311.dll`. `import ctypes` → `ModuleNotFoundError`. pynput ET ctypes brut en
   dépendent. (Logs Live : `pynput unavailable ()` → `No module named 'ctypes'`.)
2. **Charger un `.pyd` crashe Live.** Une extension C standard se lie à
   `python311.dll`, absente de ce build → droper `_ctypes.pyd` ne restaure rien, ça
   crashe l'hôte. Aucun projet connu (ClyphX, AbletonOSC, Push) n'a jamais chargé du
   natif in-process.
3. **Pas de message loop.** Même avec ctypes, un hook `WH_KEYBOARD_LL` exige que le
   thread installateur pompe les messages Windows ; le thread du remote script est
   tick-driven et n'en a pas.

→ Constitution mise à jour (§3.1, §4, §5) : la détection passe **hors-process**, dans
un **détecteur local dédié**. Le code du spike (`plugins/keyboard/`) sera retiré.

## Décisions (révisées)

1. **Détecteur local dédié** (`src/detector/`), process autonome sous **Python
   système** (où `ctypes`/`pynput` marchent), **distinct du backend**. Le backend est
   un futur **service cloud** (ML, paywall — constitution §5) ; la détection est
   intrinsèquement locale → ne peut pas y vivre. Service séparé aussi pour le
   découplage (un crash n'affecte pas l'autre).
2. **Détection : pynput.** Cross-platform (propice au futur portage macOS), pure-Python
   sous Windows. Le détecteur tourne sous vrai Python → pynput s'installe et s'importe
   normalement (contrairement à l'env Ableton).
3. **Portée : foreground-only.** Ne déclenche que si Ableton est la fenêtre au premier
   plan (check OS local). Reproduit le `#IfWinActive ahk_exe Ableton…` actuel.
4. **Bridge HTTP inchangé.** Sur combo → le détecteur résout le binding et appelle
   l'API existante du script (`GET :9000/device/load?name=…`). La couture
   capture/exécution reste celle d'aujourd'hui (c'est ce qui rend le pivot bon marché).
5. **Config** : un seul JSON à `%APPDATA%\Protocol0\shortcuts.json`, hors arbre source
   (§3.3, §5), lu par le détecteur **et** écrit par le frontend du script.
6. **Frontend** : HTML/JS minimal inline (zéro build, `fetch` vanilla), servi par le
   script sur une route GET. Reste in-script (servir une UI web ne demande pas de
   natif — §3.2 tient toujours).
7. **Packaging** : Scheduled Task au logon, calqué sur `install_p0_backend_task.ps1`.

## Architecture cible (proto, local-only)

```
[touche]                          ┌──────────── machine locale ────────────┐
   │                              │                                         │
   ▼                              │   src/detector/  (Python système)       │
détecteur (pynput, foreground)    │     pynput Listener + GetForegroundWindow│
   │  combo → lookup config       │     lit %APPDATA%\Protocol0\shortcuts.json│
   ▼                              │                                         │
GET :9000/device/load?name=…  ───────►  remote script (Ableton)            │
                                  │     - frontend config (route GET)       │
   frontend config (navigateur) ─────►  - exécution load_device (LOM)       │
        écrit shortcuts.json      └─────────────────────────────────────────┘
   (backend cloud :9001 — hors de ce chemin, §5)
```

## Contraintes vérifiées dans le code (à respecter)

- **Router GET-only** (`application/http/Router.py`) : `do_GET` seul, query params
  coercés par annotations (int/bool/str), pas de POST/body. `str` → text/html ;
  dict/list → JSON ; `None` → fire-and-forget via `submit`.
- **Routes enregistrées** en important `application/http/routes/__init__.py` (import
  tardif dans `HttpServer.start`). Tout nouveau module de routes s'y ajoute.
- **Conventions repo** : le backend lit `.env` racine via `pydantic-settings`
  (`backend/settings.py`) ; client HTTP via `requests` (`p0_script_api_client.py`) ;
  packaging Scheduled Task (`scripts/install_p0_backend_task.ps1`). Le détecteur
  calque ces patterns mais reste un package autonome.

---

## M1 — Détecteur : squelette + bridge HTTP (remplace l'ancien M0)

**But** : un process `src/detector/` qui démarre, charge la config, écoute le clavier
via pynput, filtre foreground (Ableton), et sur combo appelle `:9000/device/load`.
Premier end-to-end **sans frontend** (config éditée à la main).

**Nouveaux fichiers**
- `src/detector/pyproject.toml` — package autonome ; deps `pynput`, `requests`,
  `pydantic-settings` (+ `pywin32` ou ctypes stdlib pour le foreground check).
- `src/detector/detector/__init__.py`
- `src/detector/detector/settings.py` — lit `.env` racine (`P0_SCRIPT_PORT`), calqué
  sur `backend/settings.py`.
- `src/detector/detector/config.py` — lecture `%APPDATA%\Protocol0\shortcuts.json`
  (tolérant : `[]` si absent/corrompu) + normalisation combo.
- `src/detector/detector/foreground.py` — `ableton_is_foreground()` (Win32 local) ;
  isolé pour le futur portage Mac.
- `src/detector/detector/listener.py` — pynput Listener, build combo canonique, lookup,
  appel `requests.get(:9000/device/load?name=…)`.
- `src/detector/detector/main.py` — entrée (`poetry run detector`).

**Format de combo (canonique, partagé détecteur ↔ frontend ↔ config)** : chaîne
minuscule, modificateurs dans l'ordre fixe `ctrl`,`alt`,`shift`,`win`, puis la touche,
joints par `+`. Ex. `ctrl+alt+e`. Namespace proto : `a–z`, `0–9`, `f1–f12`.

**Vérif M1** : avec `ctrl+alt+e → load_device(name="EQ Eight")` dans le JSON,
`poetry run detector` puis presser la combo **dans Ableton** → EQ Eight chargé (idem
`GET /device/load?name=EQ Eight`). Presser la combo **hors** Ableton → rien (foreground).

**État M1 (code écrit + vérifié hors-Ableton ; end-to-end à confirmer dans Live)**
- `src/detector/` créé : `settings.py` (lit `.env` racine, `extra="ignore"`),
  `config.py` (lecture `shortcuts.json` + reload mtime), `foreground.py` (Win32),
  `listener.py` (pynput + combo canonique + lookup), `script_client.py` (requests →
  `/device/load`), `main.py` (`poetry run detector`).
- `poetry install` OK ; imports OK ; **logique testée** (parse config, tolérance
  fichier absent, normalisation combo `ctrl+alt+e`/`ctrl+shift+k`, mapping touches
  a-z/0-9/f1-f12) ; **foreground check testé en vrai** (renvoie False hors Ableton) ;
  détecteur **démarre proprement** (charge config, listener started) ; flake8 clean.
- Config de test posée : `%APPDATA%\Protocol0\shortcuts.json` (ctrl+alt+e → EQ Eight,
  ctrl+alt+u → Utility).
- **VALIDÉ end-to-end dans Live (2026-05-28)** : `ctrl+alt+e` → EQ Eight chargé,
  `ctrl+alt+u` → Utility ; hors focus Ableton → `ignored (not foreground)`. Logs :
  `combo ctrl+alt+e -> load_device {'name': 'EQ Eight'}`.
- **Bugs corrigés pendant la validation** :
  - `_key_name` mappait par `char` → cassé par les modificateurs (Ctrl+E → control
    char `\x05`, Ctrl+Alt+E → AltGr `€` en AZERTY). Corrigé : mapping par **`vk`**
    (position physique, stable quel que soit modificateur/layout). vk A-Z=65-90,
    0-9=48-57, pavé num=96-105 ; f1-f12 via `Key.name`.
  - `Ctrl+C` n'arrêtait pas le détecteur (`listener.join()` avalait l'interruption)
    → remplacé par une attente interruptible (`time.sleep` loop) dans `main.py`.

## M2 — `ShortcutConfigService` côté script + catalogue d'actions

**But** : exposer côté script ce dont le frontend a besoin. Le détecteur, lui, lit
directement le JSON (M1) — pas besoin du script pour ça.

- **Catalogue** : route `GET /actions` dérivée des `@route` existants via `get_routes()`
  (§3.4 « discoverable » ; `index_routes.py` les introspecte déjà). Allow-list (au
  début `load_device` seule). Par entrée : `name`, `label` (1re ligne `getdoc`),
  `params` (`signature`), `path`+`method`.
- **Config côté script** : `ShortcutConfigService` stdlib (load/save/upsert sur
  `%APPDATA%\Protocol0\shortcuts.json`, enveloppe versionnée). Sert les routes du
  frontend (M3).

**Nouveaux** : `application/http/ActionCatalog.py`,
`application/http/routes/shortcut_routes.py`, `domain/shortcut/{Binding,ShortcutConfigService}.py`.
**Touché** : `application/http/routes/__init__.py` (import `shortcut_routes`).

**Schéma binding** :
```json
{ "version": 1, "bindings": [
  { "combo": "ctrl+alt+e", "action": "load_device", "params": { "name": "EQ Eight" } }
] }
```

## M3 — Frontend HTML/JS minimal inline (route GET, servi par le script)

**Routes** (dans `shortcut_routes.py`) :
- `GET /shortcuts` → page HTML (calquée `index_routes.index()`).
- `GET /actions` (M2) → catalogue JSON.
- `GET /shortcuts/list` → bindings courants JSON.
- `GET /shortcuts/add?combo=…&action=…&params=<json-urlencodé>` → `Binding`,
  `upsert`/`save`. Params = blob JSON url-encodé (`json.loads` côté handler) → route
  générique sans POST. Mutation-sur-GET acceptée (localhost). POST = suivi différé.

**Capture combo → format → détecteur**
- JS `keydown` + `e.preventDefault()` + `e.stopPropagation()` ; lit
  `ctrl/alt/shift/metaKey` + **`e.code`** (position physique, pas `e.key`) → même
  chaîne canonique que le détecteur produit.
- Convergence par position physique ; namespace `a–z`,`0–9`,`f1–f12`.
- **Gotcha Win** : Windows intercepte `Win+X` avant le navigateur → best-effort ;
  privilégier `Ctrl+Alt+X`, documenter.

**Recharge config détecteur** : le détecteur surveille le mtime de `shortcuts.json` (ou
relit à chaque combo non trouvé) → pas besoin que le frontend notifie le détecteur. À
trancher en M3 (le plus simple : relire le fichier périodiquement / sur changement mtime).

## M4 — Packaging détecteur (Scheduled Task) — DIFFÉRÉ

**But** : `scripts/install_p0_detector_task.ps1` calqué sur
`install_p0_backend_task.ps1` — start au logon, restart sur crash, fenêtre cachée.

**Hors dev.** En développement, le détecteur tourne en `poetry run detector` dans un
terminal (logs en direct, Ctrl+C, relance instantanée). Le packaging Scheduled Task
est explicitement séparé du dev (constitution §5.1) et différé.

**Docker exclu.** Le détecteur capture le clavier de la session Windows hôte
(pynput/SetWindowsHookEx) et lit le window manager (GetForegroundWindow) ; un
conteneur WSL2 est isolé de l'hôte → inaccessible. C'est de l'intégration OS hôte,
toujours en process natif (constitution §5.1).

## Risques

1. **pynput sous Python système** — devrait marcher (vrai env) ; à confirmer M1.
2. **Foreground check spécifique OS** — Win32 ; isolé (`foreground.py`) pour Mac.
3. **Touche Win best-effort** — privilégier `Ctrl+Alt+X`.
4. **Mutation-sur-GET** (save) — localhost-only ; blob JSON ; POST en suivi.
5. **Cohérence config** — détecteur relit `shortcuts.json` sur changement (mtime).
6. **Deux artefacts locaux à installer** (script + détecteur) au lieu d'un — assumé
   suite au NO-GO (constitution §4/§5).

## Hors scope (prototype)

Catalogue complet (seul `load_device`), packaging binaire final, suppression totale
d'AHK, POST/body dans le Router, support macOS, backend cloud (§5).

## Nettoyage du spike

Retirer `src/script/protocol0/plugins/keyboard/` (3 fichiers) et la dépendance `pynput`
ajoutée au loader (`script_templates/Protocol_0/pyproject.toml` + copie déployée) : le
hook in-script est abandonné. Conserver le verdict ci-dessus comme trace.
