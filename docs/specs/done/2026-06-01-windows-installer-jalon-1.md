# Installeur Windows — Jalon 1 : install + autostart

Jusqu'ici, faire tourner Protocol0 sur une machine exige Python + Poetry, un
`make install_script` (qui fait un `poetry install` dans le dossier Ableton et
réécrit `__init__.py` en mode dev), et le lancement manuel du detector via
`poetry run detector` dans un terminal. C'est un workflow de développeur, pas
distribuable.

Ce jalon livre un **installeur `.exe` Windows** (Inno Setup, inspiré de
[SyncthingWindowsSetup](https://github.com/Bill-Stewart/SyncthingWindowsSetup))
qui, sur une machine vierge **sans Python ni Poetry**, installe les deux
composants actifs et fait démarrer le detector automatiquement au logon.

Windows uniquement (pas de Mac).

## Composants distribués

1. **Detector** (écoute clavier) → un **`.exe` autonome PyInstaller**
   (`protocol0-detector.exe`), lancé en **tâche planifiée au logon**, fenêtre
   cachée, auto-restart sur crash. Pas de service Windows : la capture clavier
   et le check de fenêtre au premier plan exigent la session interactive.
2. **Remote Script** (control surface Ableton) → **copie pure** du dossier
   `Protocol_0` dans `MIDI Remote Scripts`. Le script est **stdlib-only**
   (commit `2d965072`), donc la copie est triviale : pas de `poetry install`,
   pas de `_vendor/`, pas de réécriture dev en prod.

## Hors périmètre (Jalon 2)

Icône systray et « check for updates » — cf.
`docs/specs/todo/2026-06-01-windows-installer-jalon-2-systray-updates.md`.

## Décisions

- **Naming** : `protocol0` / « Protocol 0 » partout (jamais `p0`). Exe
  `protocol0-detector.exe`, tâche `protocol0-detector`.
- **Détection Ableton** : auto-détect
  `%ProgramData%\Ableton\Live*\Resources\MIDI Remote Scripts`, **version la plus
  récente** choisie ; override manuel possible dans le wizard.
- **Config prod** : port `9000` en dur (override `P0_SCRIPT_PORT` possible),
  **pas de `.env`** distribué. Seule config utilisateur :
  `%APPDATA%\Protocol0\shortcuts.json`, préservée à la désinstallation.
- **Logs detector** : fichier rotatif `%APPDATA%\Protocol0\logs\detector.log`.

## Architecture

```
[Installeur Inno Setup (.exe)]
  ├─ copie  protocol0-detector.exe       → C:\Program Files\Protocol0\
  ├─ copie  Protocol_0\ (protocol0/ + __init__.py prod)
  │                                      → <Ableton>\MIDI Remote Scripts\Protocol_0\
  ├─ [Run]  install_protocol0_detector_task.ps1  (crée la tâche au logon)
  └─ [Uninstall] uninstall_…_task.ps1 + suppression fichiers (sauf shortcuts.json)

Au logon :
[Scheduled Task protocol0-detector] → protocol0-detector.exe (caché, auto-restart)
  ├─ lit  %APPDATA%\Protocol0\shortcuts.json
  ├─ logge %APPDATA%\Protocol0\logs\detector.log
  └─ HTTP :9000 → remote script (dans Ableton)
```

## Build

`scripts/build_installer.ps1` orchestre :
1. `build_detector_exe.ps1` → `src/detector/dist/protocol0-detector.exe`
   (PyInstaller, spec `src/detector/protocol0-detector.spec`).
2. `stage_remote_script.ps1` → `build/stage/Protocol_0/` (copie de
   `src/script/protocol0/` + `__init__.prod.py`).
3. `ISCC.exe installer\protocol0.iss` → `dist-installer/Protocol0-Setup-*.exe`.

Le build requiert Poetry + PyInstaller + Inno Setup sur la **machine de build**
seulement, jamais sur la cible.

## Vérification

1. **Build** : les 3 artefacts ci-dessus sont produits.
2. **Smoke test exe** : `protocol0-detector.exe` lancé seul → `detector.log`
   montre « keyboard listener started » ; combo ignoré si Ableton non focus.
   Valide le fix hidden-import pynput.
3. **Install** : le wizard pré-remplit le chemin MIDI Remote Scripts (Live le
   plus récent) ; `Protocol_0\protocol0\` copié, exe dans `Program Files\Protocol0`.
4. **Autostart** : `Get-ScheduledTask protocol0-detector` enregistrée ; après
   logoff/logon, `Get-Process protocol0-detector` présent, aucun flash console.
5. **Fonctionnel** : control surface « Protocol 0 » activé dans Ableton ; combo
   lié (Ableton focus) → log `… -> load_device …`, appel :9000 OK.
6. **Auto-restart** : `Stop-Process protocol0-detector -Force` → revient ~1 min.
7. **Uninstall** : tâche + `Program Files\Protocol0` + `Protocol_0` supprimés ;
   `%APPDATA%\Protocol0\shortcuts.json` préservé.

## Pièges rencontrés (et résolus) pendant l'implémentation

Trois bugs ont été trouvés en testant dans le vrai Python d'Ableton, tous liés à
l'absence de `.env` en prod :

1. **Loader prod : `ModuleNotFoundError: No module named 'protocol0'`.** Ableton
   charge `Protocol_0/__init__.py` mais n'ajoute pas son dossier au `sys.path`.
   Fix : le loader prod fait `sys.path.insert(0, dirname(__file__))` avant l'import
   (cf. `script_templates/Protocol_0/__init__.prod.py`).
2. **Script : `TypeError` au chargement sur les ports.** `HttpServer._PORT` et
   `BackendClient._BASE_URL` lisaient `P0_SCRIPT_PORT` / `P0_BACKEND_PORT` depuis le
   `.env` racine (absent en prod) → `env_get` renvoyait `None` → crash. Fix
   provisoire : valeurs **en dur** (`9000`, `http://127.0.0.1:9001`). Rendre
   configurable : `docs/specs/backlog/2026-06-02-script-settings-json.md`.
3. **Installeur : fichiers verrouillés.** La tâche planifiée relançait l'exe pendant
   l'install. Fix : `PrepareToInstall()` dans le `.iss` fait `schtasks /End` puis
   `taskkill` avant la copie ; l'uninstall task script tue aussi le process.

Notes :
- **`__pycache__` périmé** : un `.pyc` d'une ancienne install dev pouvait masquer le
  nouveau `__init__.py`. Fix : `[InstallDelete]` vide le dossier cible avant copie ;
  `stage_remote_script.ps1` purge les `__pycache__`.
- **2 process `protocol0-detector.exe`** = normal (bootloader PyInstaller onefile :
  parent + enfant), une seule instance logique.

## Risques

- **PyInstaller rate le backend pynput** → `ImportError` à froid. Fix :
  `hiddenimports` explicites dans le `.spec` ; smoke-test (étape 2) avant build
  de l'installeur.
- **SmartScreen / exe non signé** + alerte AV (un keylogger). Documenter
  « Informations complémentaires → Exécuter quand même » ; `upx=False`.
  Signature de code = ultérieur.
- **Le script cesse d'être stdlib-only** → la copie pure casserait ; garde-fou :
  le script DOIT rester stdlib-only (cf. `2d965072`).
- **Auto-détect rate une install non standard** → la page d'override pré-remplie
  est le filet.
