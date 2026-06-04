# Support macOS — installeur shell (iso Windows)

Jumeau macOS du Jalon 1 Windows
(`docs/specs/done/2026-06-01-windows-installer-jalon-1.md`). On vise un **script
shell simple** (`install.sh`), **pas** de `.pkg`, **pas** de signature de code.

Principe directeur : **rester iso Windows**. Le remote script va dans le dossier
**système** (le bundle de l'app Ableton, équivalent de `ProgramData`), pas la User
Library — choix délibéré pour coller au comportement Windows.

Le foreground macOS et le mapping clavier pynput ne sont **pas testables sans Mac**
(l'auteur n'en a pas ; un ami testera) → approche best-effort + **mode debug verbeux**
+ protocole de test.

## Décisions

- **Périmètre** : complet — detector + remote script + LaunchAgent + scripts shell.
- **Remote script** : dans le **bundle app**
  `/Applications/Ableton Live X.app/Contents/App-Resources/MIDI Remote Scripts/`
  (iso Windows ; **sudo requis**). Auto-détection du Live le plus récent dans
  `/Applications`, override possible.
- **Autostart** : LaunchAgent `~/Library/LaunchAgents/com.protocol0.detector.plist`
  (per-user, `RunAtLoad`, `KeepAlive` = restart-on-crash). Session GUI requise.
- **Foreground macOS** : subprocess léger (`lsappinfo` ; fallback `osascript`),
  **sans PyObjC**. Ne se déclenche qu'à un match de combo, pas à chaque touche.
- **Incertitude** : best-effort + **flag debug** `P0_DETECTOR_DEBUG=1` (logge l'app au
  premier plan + touches pynput brutes) + protocole de test.
- **appdata macOS** : `~/Library/Application Support/Protocol0` (config + `logs/`),
  pendant de `%APPDATA%\Protocol0`.
- **Naming** : `protocol0` partout. Binaire `protocol0-detector`, label
  `com.protocol0.detector`.

## Composants distribués

1. **Detector** → binaire PyInstaller `protocol0-detector` (pas `.exe`), lancé par un
   LaunchAgent au login, `KeepAlive` pour le restart. Logs rotatifs dans
   `~/Library/Application Support/Protocol0/logs/detector.log`.
2. **Remote script** → copie pure de `build/stage/Protocol_0/` dans le bundle app
   Ableton (sudo). Stdlib-only, comme sur Windows.

## Portage du code (portable vs Windows-spécifique)

**Helper de chemin `appdata_dir()`** — dupliqué à l'identique dans les deux paquets
séparés (contrat de couplage existant, cf. `ShortcutConfigService.py:25`) :
```python
def appdata_dir() -> str:
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"),
                            "Library", "Application Support", "Protocol0")
    return os.path.join(os.environ["APPDATA"], "Protocol0")  # win32
```
Call sites : `detector/config.py:22-23`, `detector/main.py:19-22` (+ docstring `:26`),
`ShortcutConfigService.py:24-26`.

**`foreground.py`** — dispatch par plateforme, chemin Win32 (lignes 10-44) gardé intact ;
backend darwin via `lsappinfo front` + `lsappinfo info -only name <ASN>`, le substring
`"ableton live"` matche « Ableton Live 12 Suite ». Fallback `osascript … frontmost`.

**`listener.py:42-66`** — `_key_name()` : fallback sur `key.char` (a-z/0-9) quand `vk`
absent (macOS). Format de combo (minuscules, ordre `ctrl,alt,shift,win`, `+`) préservé →
`shortcuts.json` portable. `Key.cmd*` mappe déjà sur `"win"` (Cmd = token `win`,
intentionnel).

**`main.py:54-56`** — gate `sys.platform` autorise `("win32", "darwin")`.

**`settings.py`** — flag `P0_DETECTOR_DEBUG` (pattern de `P0_SCRIPT_PORT`).

**`debug.py:20-23`** — remplacer les `"\\"` en dur par `os.sep`.

**Inchangé (portable)** : `version.py` (les deux), `script_client.py`, `HttpServer.py`,
`shortcut_routes.py`, `env.py`, `Config.py`.

## Mode debug (diagnostic à distance)

`P0_DETECTOR_DEBUG=1` → niveau DEBUG ; logge dans `listener._handle_main_key` chaque
touche brute (`vk`/`char`/`name`) + la combo construite ; logge dans
`ableton_is_foreground()` le nom d'app détecté au premier plan. L'ami lance le binaire à
la main avec ce flag si un raccourci ne marche pas.

## Scripts & artefacts (miroir des `.ps1`/`.iss`)

**Créer** :
- `scripts/build_detector_binary.sh` (miroir `build_detector_exe.ps1`)
- `scripts/stage_remote_script.sh` (miroir exact, VERSION incluse)
- `scripts/install.sh` (auto-détect bundle Live le plus récent + override ; sudo pour le
  bundle ; copie binaire + `chmod +x` + `xattr -dr com.apple.quarantine` ; rend le plist
  + `launchctl bootstrap` ; `sudo rm -rf` puis `cp -R` du Protocol_0 ; instructions TCC)
- `scripts/uninstall.sh` (`launchctl bootout` + rm plist/binaire/Protocol_0 ; **préserve
  `shortcuts.json`**)
- `installer/com.protocol0.detector.plist.template` (Label, ProgramArguments,
  RunAtLoad, KeepAlive, ProcessType Interactive, StandardOut/ErrPath →
  `~/Library/Logs/Protocol0`)
- `src/detector/protocol0-detector-mac.spec` (séparé ; `datas` slashes avant ;
  `hiddenimports=['pynput.keyboard._darwin','pynput.mouse._darwin']` ; pas de PyObjC)

## Permission Accessibility / Input Monitoring (gotcha)

pynput sur macOS exige Accessibility (+ probablement Input Monitoring) accordé au binaire
dans Réglages Système → Confidentialité. `install.sh` ne peut pas l'accorder : imprimer
les instructions, faire `xattr -dr com.apple.quarantine`, et après accord
`launchctl kickstart -k gui/$(id -u)/com.protocol0.detector`. **Plus gros risque UX mac.**

## Vérification — protocole de test (l'ami)

1. Build : `build_detector_binary.sh` → `dist/protocol0-detector` ; `stage_remote_script.sh`
   → `build/stage/Protocol_0/{__init__.py,protocol0/,VERSION}`.
2. Install : `install.sh` (sudo ; tester défaut auto-détecté + override). Vérifier binaire,
   plist, `Protocol_0/` dans le bundle.
3. Permission : accorder Accessibility + Input Monitoring ;
   `launchctl kickstart -k gui/$(id -u)/com.protocol0.detector`.
4. Agent : `launchctl print …` tourne ; `detector.log` → « keyboard listener started » + version.
5. Ableton : redémarrer Live ; Control Surface → « Protocol 0 ».
6. Port : `:9000` répond.
7. Fonctionnel : combo + Ableton focus → action + log `combo … -> …` ; autre app focus →
   `ignored (Ableton not foreground)`. Si KO → relancer avec `P0_DETECTOR_DEBUG=1`.
8. Autostart : logout/login → agent relancé.
9. Crash-restart : `kill <pid>` → KeepAlive relance.
10. Uninstall : `uninstall.sh` → tout retiré, **`shortcuts.json` préservé**.

## Risques

- **Foreground non testable sans Mac** — format `lsappinfo`/`osascript` non vérifié ;
  best-effort + mode debug. Risque principal.
- **TCC Accessibility / Input Monitoring** — binaire non signé, accord manuel, réinitialisable
  par le quarantine ; `install.sh` aide mais ne peut pas auto-accorder.
- **pynput `vk`/`char` sur macOS non vérifié** — fallback char non testé sous modificateurs.
- **Bundle app + sudo + update de Live** — écrire dans le bundle exige sudo et **casse à
  chaque mise à jour de Live** (dossier recréé) → réinstall nécessaire. Contrepartie assumée
  du choix iso-Windows (vs User Library).
- **Stdlib-only** — le remote script doit le rester ; `appdata_dir()` n'utilise que `os`/`sys`.
- **Cmd→`win`** — token `win` = Cmd sur mac ; portable, documenté.
