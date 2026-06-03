# Agent + SPA Vue 3 + API `/api`

Suite directe du Jalon 2 (`docs/specs/in-progress/2026-06-01-windows-installer-jalon-2-launcher.md`).
Le Jalon 2 a livré la page « launcher » inline servie par le detector (port 9010, 3 états,
redirect vers `<script_url>/shortcuts`). Cette spec **remplace cette page et le redirect** par un
vrai front Vue 3, et déplace l'édition des raccourcis hors d'Ableton.

## Problème

L'UI web de config est servie par le script **dans Ableton** (page `/shortcuts`, string `_PAGE`
inline) : elle **meurt avec Ableton**, n'offre que l'ajout (pas d'édition/suppression, pas de
détection de conflit, pas de recherche). Éditer ses raccourcis impose donc de lancer Ableton.

## But

- Un **front Vue 3** (build statique) servi par le process de fond, pour éditer les raccourcis
  **sans Ableton** : home soignée, keymapper complet, page de doc d'API.
- Le process de fond grossit bien au-delà de la « détection » → renommé **`detector` → `agent`**.
- Ableton n'est requis que pour *déclencher* les actions, plus pour *éditer*.

## Décisions actées

| Sujet | Décision |
|-------|----------|
| Renommage | `src/detector/` → **`src/agent/`** (package `detector/` → `agent/`). `agent` = terme launchd macOS pour un process per-user au logon ; cross-platform, sans connotation de tier distant. |
| Dossier front | **`src/frontend/`** (Vite + Vue 3 + TS). Source committée, `dist/` gitignoré, buildé en CI. |
| Embarquement | SPA bundlée dans l'exe via PyInstaller `datas=[('..\\..\\frontend\\dist','frontend')]` + résolveur `sys._MEIPASS` (même pattern que `VERSION`) + catch-all SPA → `index.html`. |
| Découpage serveur | **L'agent sert tout** : home + keymapper + api-docs + **`/api`** (CRUD raccourcis). Le script garde son API d'actions interne (`/device/load`…), appelée par l'agent au keypress. |
| Préfixe API | **`/api`** (pas de versioning — API non publique). |
| Catalogue d'actions | **Statique, embarqué dans l'agent** (miroir de l'allowlist `load_device`), pour que le sélecteur marche Ableton fermé. |
| Page api-docs | Page **écrite à la main, stylée au design system** (l'agent est stdlib `http.server`, pas de FastAPI/OpenAPI). Documente uniquement l'API de l'agent. |
| Reload | **Aucune plomberie** : le listener de l'agent recharge `shortcuts.json` par mtime, le script lit en live. |

Étude OSS à l'appui : Navidrome (`ui/`, build gitignoré, `//go:embed`), Syncthing (`gui/`, build
en CI), Transmission (`web/`, sert des statiques), odrive3.6_web_gui (PyInstaller `datas=` +
`sys._MEIPASS` + catch-all SPA — l'analogue Python exact).

## Invariants à préserver

1. **Canonicalisation des combos byte-identique** : listener agent (lit `vk`), capture SPA (lit
   `e.code`), chaîne stockée. Ordre `ctrl, alt, shift, win` + touche, minuscules, joints `+`.
   Namespace `a-z`, `0-9` (haut + numpad), `f1-f12`.
2. **Schéma `shortcuts.json` inchangé** : `{ "version": 1, "bindings": [{combo, action, params}] }`.
3. **Écriture atomique** (`tmp` + `os.replace`).
4. **Port 9010 fixe** (raccourci `.url` câblé dessus).

## Architecture cible

```
navigateur (http://127.0.0.1:9010/)
  SPA Vue 3 (router history-mode)
    /            home (intro + carte CTA → keymapper)
    /shortcuts   keymapper
    /api-docs    référence d'API
        │ assets + XHR /api/*, /status
        ▼
agent (ex-detector) — exe PyInstaller, port 9010, toujours vivant
   GET /status                    → diagnostic 3 états (préservé, redirect supprimé)
   GET /api/health                → {ok, version}
   GET /api/shortcuts             → liste
   GET|POST /api/shortcuts/add    → upsert par combo (atomique)
   GET|POST /api/shortcuts/delete → suppression par combo (NOUVEAU)
   GET /api/actions               → catalogue statique
   GET /*  (catch-all)            → frontend/dist/index.html
   listener pynput — inchangé, recharge par mtime
        │ keypress → GET <script_url>/device/load?name=…
        ▼
script (dans Ableton) — port dynamique, meurt avec Ableton
   /health, /, routes d'actions (INCHANGÉ)
   [SUPPRIMÉ] /shortcuts, /shortcuts/list, /shortcuts/add, /actions
```

## Phases

### A — Renommage `src/detector/` → `src/agent/`
Mécanique, sans changement de comportement, isolé. `git mv` du dossier + package + `.spec`.
MAJ : `pyproject.toml` (name/packages/scripts), `protocol0-agent.spec` (entry + name), imports
`from detector` → `from agent`, `scripts/windows/build_*_exe.ps1` + `build_installer.ps1`,
`installer/protocol0.iss` (chemin/nom exe ; **garder le NOM de tâche `Protocol0`**), `Makefile`,
`.gitignore`. Grep : `detector`, `protocol0-detector`, `from detector`, `import detector`.

### B — Front `src/frontend/`
Vite + Vue 3 + TS. Router **history mode**. `design-system.css` copié au prebuild (source unique
= `src/website/`). Composants : `HomeView` (CTA), `AppHeader` (keymapper / api docs / docs externe),
`KeymapperView` (suit le sous-plan keymapper : `useComboCapture` portant `keyName/buildCombo/
isModifier`, recherche, conflit, auto-save, delete-by-combo), `ApiDocsView`, `Kbd`, `StatusPill`.
`vite build` → `src/frontend/dist/`.

### C — Agent sert SPA + `/api`
Sous-package `agent/web/` : `server.py` (bind 9010 + lifecycle, porté de `launcher.py`), `api.py`
(`/api/*`), `static_files.py` (résolveur `_MEIPASS` + service + catch-all), `status.py` (3 états,
**redirect supprimé**). `agent/shortcut_store.py` (port de `ShortcutConfigService` + `delete`).
`agent/action_catalog.py` (statique). `.spec` : ajouter `('..\\..\\frontend\\dist','frontend')`.

### D — Build & CI
`build_installer.ps1` étape 0 : `cd src/frontend; npm ci; npm run build`. `release.yml` :
`actions/setup-node@v4`. `.gitignore` : `dist/`, `node_modules/`, copie design-system. `Makefile` :
`agent`, `frontend`.

### E — Nettoyage du script
Supprimer `shortcut_routes.py` (+ son import dans `routes/__init__.py`), `ActionCatalog.py`, et
`ShortcutConfigService.py` + `Binding.py` **s'ils sont inutilisés ailleurs** (grep avant). Le
script ne garde que `/health`, `/`, ses routes d'actions.

## Dépend de

- Jalon 2 mergé (launcher 9010, `/status` 3 états, `runtime.json`, raccourci `.url`).

## Vérification

- **Ableton fermé** : `:9010/` → home (thème sombre, fonts), CTA → `/shortcuts` (deep-link survit
  au refresh). `/api/actions` + `/api/shortcuts` → JSON. Enregistrer `ctrl+alt+e`,
  `ctrl+shift+f5`, `alt+l` → chaîne écrite **byte-identique** à ce que le listener matche.
  Conflit → warning + Remplacer. Delete retire le binding. StatusPill = `no_ableton`, édition OK.
- **Ableton ouvert + script actif** : StatusPill = `ready` (pas de redirect). Presser un combo au
  premier plan → action déclenchée (listener rechargé par mtime). Routes script `/shortcuts*` → 404.
- **Exe gelé** : installé via l'installeur, `:9010/` sert la SPA depuis `_MEIPASS/frontend` ;
  home + keymapper + api-docs OK ; keypress déclenche l'action.
