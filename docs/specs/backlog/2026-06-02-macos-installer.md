# Support macOS — installeur shell (iso Windows)

Jumeau macOS des deux jalons Windows : Jalon 1
(`docs/specs/done/2026-06-01-windows-installer-jalon-1.md`, install + autostart) et
Jalon 2 (`docs/specs/in-progress/2026-06-01-windows-installer-jalon-2-launcher.md`,
launcher web + découverte de port). On vise un **script shell simple** (`install.sh`),
**pas** de `.pkg`, **pas** de signature de code.

Principe directeur : **rester iso Windows**. Le remote script va dans le dossier
**système** (le bundle de l'app Ableton, équivalent de `%ProgramData%`), pas la User
Library — choix délibéré pour coller au comportement Windows.

> **Ableton Live 12 uniquement.** Protocol0 cible Live 12 (Python 3.11 embarqué ; Live 11
> est en 3.7). Le produit est marketé « Ableton 12 only », toutes éditions
> (Intro/Standard/Suite). La détection ne vise **que** Live 12 (`major == 12`) et **échoue
> avec un message clair** si aucun Live 12 n'est trouvé — pas de fallback sur une autre
> version. Voir « Toutes éditions ».

Le foreground macOS et le mapping clavier pynput ne sont **pas testables sans Mac**
(l'auteur n'en a pas ; un ami testera) → approche best-effort + **mode debug verbeux**
+ protocole de test.

## ⚠️ État de l'archi — ce plan a été réécrit après le Jalon 2

Le code a beaucoup bougé depuis la première rédaction (mai 2026). **Lire l'archi
courante avant d'implémenter** ; les changements qui touchent ce portage :

- **`detector` → `agent`** partout (commit `bccb758b`). Paquet `src/agent/agent/`,
  binaire `protocol0-agent`, logs `agent.log`, tâche/label `Protocol0` /
  `com.protocol0.agent`.
- **L'agent sert un serveur web** (`agent/web/` : SPA Vue 3 + `/api` + `/status`) sur
  un **port fixe 9010** (`settings.WEB_PORT`), en plus de capturer le clavier. Le
  launcher (`agent/launcher_entry.py`) ne fait qu'ouvrir cette page. **Ce serveur doit
  tourner aussi sur macOS** (rien de Windows-spécifique dedans : `http.server` stdlib).
- **`requests` n'est PLUS stdlib-only côté agent** : `script_client.py` et
  `web/status.py` en dépendent. PyInstaller l'embarque déjà ; à reconfirmer dans le
  `.spec` mac.
- **Découverte de port dynamique** : le script publie son URL effective dans
  `runtime.json`, l'agent la lit à chaque appel. Plus de `:9000` câblé côté agent.
  Le `:9000` ne subsiste que comme port *préféré* du script (fallback OS sinon).
- **Nouveaux fichiers** côté agent à porter/auditer : `process_check.py` (détecte
  si Ableton **tourne**, pas seulement au premier plan), `single_instance.py`,
  `web/server.py`, `web/status.py`, `launcher_entry.py`.
- **Le `appdata_dir()` helper du plan original N'EXISTE PAS encore** : chaque call
  site fait `os.environ["APPDATA"]` en dur. Le portage doit l'introduire (cf.
  « Portage du code »).

## Décisions

- **Périmètre** : complet — agent (clavier + serveur web) + remote script +
  LaunchAgent + launcher + scripts shell.
- **Remote script** : dans le **bundle app**
  `<Ableton Live 12>.app/Contents/App-Resources/MIDI Remote Scripts/` (chemin confirmé,
  **noter `App-Resources`, pas `Resources`**) ; iso Windows ; **sudo requis** (bundle
  souvent root-owned). Détection ciblée **Live 12** (override possible).
- **Détection du bundle = par BUNDLE ID + version 12, pas par nom** (cf. « Toutes
  éditions »). Le `.app` est renommable et l'édition n'est pas fiable dans le nom → filtrer
  `/Applications` **et** `~/Applications` par `CFBundleIdentifier == com.ableton.live`
  **ET** `CFBundleVersion` majeur `== 12`. **Toutes éditions (Intro/Standard/Suite) de
  Live 12 couvertes par construction** : même bundle id. **Aucun Live 12 → erreur claire
  « Ableton Live 12 required », stop** (pas de fallback sur 10/11).
- **Autostart** : LaunchAgent **per-user** `~/Library/LaunchAgents/live.protocol0.agent.plist`
  (`RunAtLoad=true`, `KeepAlive={SuccessfulExit:false, Crashed:true}` = restart-on-crash
  mais honore un stop propre). Session GUI requise. **Pas de LaunchDaemon root** : un
  keyboard tap n'a pas besoin de root, juste de la session GUI (cf. best practices).
- **launchctl moderne** : `bootstrap gui/$(id -u) <plist>` / `bootout` / `kickstart -k`,
  **jamais** `load`/`unload` (déprécié). Convention validée par skhd + yabai.
- **Foreground macOS = par BUNDLE ID** : `lsappinfo front` → ASN, puis
  `lsappinfo info -only bundleID <asn>` comparé à `com.ableton.live` (fallback `osascript`).
  **Sans PyObjC.** Ne matche **pas** le nom d'affichage (renommable) ni le process `Live`
  (trop générique). Ne se déclenche qu'à un match de combo, pas à chaque touche.
- **Ableton tourne ? (process_check) = par BUNDLE ID** : énumérer les apps lancées et
  matcher `com.ableton.live` (via `lsappinfo` ; pas `pgrep Live` qui est trop large —
  `Contents/MacOS/Live` → `comm` = juste `Live`). Pendant macOS du `tasklist`. Sert au
  `/status` du launcher (distinguer « Ableton fermé » de « control surface pas activée »).
- **Serveur web (port 9010)** : porté tel quel (stdlib `http.server`). Le launcher
  ouvre `http://127.0.0.1:9010/shortcuts` via `webbrowser` (déjà cross-platform).
- **TCC** : le listener est **observe-only** (pas de `suppress`/`intercept` dans
  `listener.py`) → pynput utilise un `CGEventTap` en `kCGEventTapOptionListenOnly` →
  permission requise = **Input Monitoring** (et non Accessibility). Détail décisif,
  cf. section « TCC » plus bas.
- **Incertitude** : best-effort + **flag debug** `P0_AGENT_DEBUG=1` (logge l'app au
  premier plan + touches pynput brutes) + protocole de test.
- **appdata macOS** : `~/Library/Application Support/Protocol0` (config `shortcuts.json`
  + `runtime.json` + `logs/`), pendant de `%APPDATA%\Protocol0`. Logs aussi exposés en
  `~/Library/Logs/Protocol0/` via `StandardOut/ErrPath` du plist (convention mac).
- **Naming** : `protocol0` partout. Binaire `protocol0-agent`, launcher
  `protocol0-launcher`. Label LaunchAgent **`live.protocol0.agent`** (reverse-DNS aligné
  sur le domaine `protocol0.live` ; convention skhd/yabai/karabiner/syncthing).

## Composants distribués

1. **Agent** → binaire PyInstaller `protocol0-agent` (pas `.exe`), lancé par un
   LaunchAgent au login, `KeepAlive` pour le restart. Capture le clavier ET sert le
   serveur web 9010 (SPA + `/api` + `/status`). Logs rotatifs dans
   `~/Library/Application Support/Protocol0/logs/agent.log`.
2. **Launcher** → **`.app` minimal** `Protocol0.app` (PAS de binaire PyInstaller).
   Un wrapper trivial : `Info.plist` + un script `Contents/MacOS/Protocol0` qui fait
   `open "http://127.0.0.1:9010/shortcuts"` puis sort, + une icône `Contents/Resources/
   Protocol0.icns` (le badge « P »). **Décision** (cf. « Décisions tranchées ») : un `.app`
   est l'artefact idiomatique mac à glisser au Dock, porte son icône proprement, ne touche
   pas le clavier → **aucune permission TCC**, et coûte ~10 lignes contre tout un runtime
   Python embarqué pour un seul `open`. Posé dans `/Applications/Protocol0.app`.
3. **Remote script** → copie pure de `build/stage/Protocol_0/` dans le bundle app
   Ableton (sudo). Stdlib-only, comme sur Windows.

## Portage du code (portable vs Windows-spécifique)

**Helper de chemin `appdata_dir()`** — À CRÉER (n'existe pas aujourd'hui). Comme l'agent
et le script vivent dans deux paquets séparés sans dépendance partagée (contrat de
couplage existant), **dupliquer le helper à l'identique des deux côtés** :
```python
def appdata_dir() -> str:
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"),
                            "Library", "Application Support", "Protocol0")
    return os.path.join(os.environ["APPDATA"], "Protocol0")  # win32
```
Call sites à remplacer (chemins en dur `os.environ["APPDATA"]`, à revérifier — le code
bouge) :
- **Agent** : `agent/config.py:23` (`config_path`), `agent/main.py:21`
  (`_log_dir`, + docstring `:27`), `agent/runtime_state.py:14` (`runtime_path`).
- **Script** : `protocol0/application/http/runtime_state.py:16` (`runtime_path`),
  et le `ShortcutConfigService` (lecture `shortcuts.json` côté script).
- **Hors périmètre installeur** mais même contrat : `scripts/logs.py` (Windows-only,
  `make logs`), `src/js-extension/src/extension.ts` (spike). Ne pas les porter ici ;
  juste savoir qu'ils répliquent le même chemin.

**`foreground.py`** — dispatch par plateforme. Le chemin Win32 (ctypes
`GetForegroundWindow` + `QueryFullProcessImageNameW`, lignes 10-47) est gardé intact ;
backend darwin : `lsappinfo front` → ASN, puis `lsappinfo info -only bundleID <asn>`
comparé à `com.ableton.live` (fallback `osascript`). **Match par bundle id, pas par nom
d'affichage** (cf. « Toutes éditions »). La règle partagée Windows `matches_ableton()`
matche un nom d'exe ; côté mac on introduit une règle distincte `is_ableton_bundle_id()`
(la sémantique diffère : nom vs id). Garder les deux derrière une petite indirection par
plateforme plutôt que de forcer une constante commune.

**`process_check.py`** (nouveau, Jalon 2) — `ableton_is_running()`. Backend Windows =
`tasklist /FO CSV` + `matches_ableton()` (préfixe `"ableton live "`, inchangé). Backend
darwin : énumérer les apps lancées et matcher `CFBundleIdentifier == com.ableton.live`
(via `lsappinfo`), **PAS** `pgrep Live` (l'exécutable est `Contents/MacOS/Live` → `comm` =
`Live`, trop générique, et l'édition n'y apparaît jamais). Couvre Intro/Standard/Suite/Lite
par construction (même bundle id). Voir « Toutes éditions » pour le détail et les bêtas.

**`listener.py:42-66`** — `_key_name()` : mappe par `vk`. Sous macOS, `vk` peut être
absent ou différent → **fallback sur `key.char`** (a-z/0-9) à confirmer. Format de combo
(minuscules, ordre `ctrl,alt,shift,win`, `+`) préservé → `shortcuts.json` portable.
`Key.cmd*` mappe déjà sur `"win"` (`listener.py:36-38`) → **Cmd = token `win`**,
intentionnel et documenté.

**`main.py:56`** — gate `sys.platform != "win32"` (« agent is Windows-only ») →
autoriser `("win32", "darwin")`. Tout le reste de `start()` (single_instance, listener,
`web.start()`) est portable.

**`settings.py`** — flag `P0_AGENT_DEBUG` (pattern de `P0_SCRIPT_PORT`, déjà présent).
`WEB_PORT = 9010` inchangé. `P0_SCRIPT_PORT` reste l'escape hatch.

**`web/` (server, status, api, static_files)** — **portable, rien à faire** :
`http.server` stdlib, `requests` pour le ping `/api/health`. Vérifier juste que
`static_files.py` lit bien la SPA via `sys._MEIPASS` (PyInstaller) — ok sur mac.

**Inchangé (portable)** : `version.py`, `script_client.py` (résout l'URL via
`runtime_state` + `requests`), `single_instance.py` (à vérifier : implémentation du
verrou cross-platform ?), `web/*`, `Config.py` côté script.

## Mode debug (diagnostic à distance)

`P0_AGENT_DEBUG=1` → niveau DEBUG ; logge dans `listener._handle_main_key` chaque touche
brute (`vk`/`char`/`name`) + la combo construite ; logge dans `foreground` le nom d'app
détecté au premier plan. L'ami lance le binaire à la main avec ce flag si un raccourci ne
marche pas.

## Scripts & artefacts (miroir des `.ps1`/`.iss`)

**Créer** (côté `scripts/macos/` pour rester rangé en miroir de `scripts/windows/`) :
- `scripts/macos/build_agent_binary.sh` (miroir `build_agent_exe.ps1` : build SPA
  d'abord, puis PyInstaller pour l'**agent seul** + assemblage du **`.app` launcher**
  — pas de PyInstaller pour le launcher). La SPA `src/frontend/dist` doit exister AVANT
  (embarquée via `datas` dans l'agent).
- `scripts/macos/stage_remote_script.sh` (miroir `stage_remote_script.ps1`, VERSION
  incluse, purge `__pycache__`).
- `scripts/macos/install.sh` :
  1. auto-détect du bundle **Live 12** par bundle id (`com.ableton.live`) + `CFBundleVersion`
     majeur `== 12`, sur `/Applications` + `~/Applications`, override possible. **Si aucun
     Live 12 → message « Ableton Live 12 required » et exit non-zéro** (cf. « Toutes
     éditions ») ;
  2. copie le **binaire agent** vers un **chemin d'install STABLE**
     `~/Library/Application Support/Protocol0/bin/` (cf. TCC : un chemin stable préserve
     une partie de la clé TCC) + `chmod +x` + `xattr -dr com.apple.quarantine` +
     **ad-hoc codesign** avec un identifier stable (cf. TCC) ;
  3. copie le **`.app` launcher** dans `/Applications/Protocol0.app`
     (+ `xattr -dr com.apple.quarantine`) ;
  4. substitue le chemin + `$HOME` dans le template de plist, le pose dans
     `~/Library/LaunchAgents/`, puis `launchctl bootstrap gui/$(id -u)` ;
  5. **sudo** uniquement pour le bundle Ableton : `sudo rm -rf` puis `cp -R` du Protocol_0 ;
  6. imprime les instructions TCC + ouvre le volet Input Monitoring (deep-link) ;
  7. **à la fin, propose d'ouvrir Protocol0** (cf. ci-dessous).
- `scripts/macos/uninstall.sh` (`launchctl bootout gui/$(id -u)` + rm plist/binaires/
  Protocol_0 ; **préserve `shortcuts.json`** — il vit hors du payload, donc préservé par
  construction).
- `installer/live.protocol0.agent.plist.template` — clés validées contre skhd/yabai/
  syncthing :
  - `Label` → `live.protocol0.agent`
  - `ProgramArguments` → chemin **absolu** du binaire agent (chemin d'install stable)
  - `RunAtLoad` → `true`
  - `KeepAlive` → `{SuccessfulExit: false, Crashed: true}` (restart sur crash, pas sur
    quit propre — sinon un quit utilisateur se bat avec launchd)
  - `ProcessType` → `Interactive` (sert une UI web locale ; évite le throttling) —
    **pas** de `Nice -20` (skhd/yabai en ont besoin pour la latence WM, pas nous)
  - `StandardOutPath`/`StandardErrorPath` → `~/Library/Logs/Protocol0/agent.{out,err}.log`
    (convention mac ; skhd/yabai écrivent dans `/tmp`, c'est une verrue à ne pas copier)
  - `EnvironmentVariables` → `PATH` (utile si l'agent shell-out vers `lsappinfo`/`pgrep`)
- `src/agent/protocol0-agent-mac.spec` — **agent uniquement** (le launcher est un `.app`,
  pas de `.spec`). Séparé du `.spec` Windows ; `datas` slashes POSIX : `../../VERSION`,
  `../../src/frontend/dist` ; `hiddenimports=['pynput.keyboard._darwin',
  'pynput.mouse._darwin']` ; `requests` déjà tiré ; pas de PyObjC ; pas d'`icon=.ico`.
- **`.app` launcher** (assemblé à la main, pas PyInstaller) :
  `installer/Protocol0.app/Contents/{Info.plist, MacOS/Protocol0, Resources/Protocol0.icns}`.
  `MacOS/Protocol0` = script `#!/bin/sh` → `open "http://127.0.0.1:9010/shortcuts"`.
  `Info.plist` : `CFBundleName=Protocol 0`, `CFBundleIdentifier=live.protocol0.launcher`,
  `CFBundleIconFile=Protocol0`, `LSUIElement` non requis (l'app sort tout de suite).
  Icône `.icns` générée depuis `src/website/favicon.svg` (pendant mac de `generate_icon.py`).

**Cibles Makefile** (miroir éventuel) : la `make installer` Windows existe ; prévoir un
équivalent mac best-effort, ou laisser les `.sh` invoqués à la main par l'ami.

## Ouvrir Protocol0 à la fin de l'install

L'installeur Windows (Inno Setup) a un wizard GUI → l'idiome y serait une case `[Run]`
`postinstall skipifsilent` « Launch Protocol 0 ». **`install.sh` n'a pas de wizard** :
l'équivalent idiomatique shell est un **prompt interactif final**, défaut « oui » :

```sh
printf "Open Protocol 0 now? [Y/n] "; read -r ans
case "$ans" in [Nn]*) ;; *) open -a "/Applications/Protocol0.app" ;; esac
```

Détails :
- `open -a Protocol0.app` (le `.app` ouvre l'URL `:9010/shortcuts`). Comme l'agent vient
  d'être `bootstrap`é, le serveur 9010 répond déjà ; sinon la SPA affiche un état (cf.
  `/status`) plutôt qu'une page morte.
- **Skip si non-interactif** : si `stdin` n'est pas un TTY (`[ -t 0 ]` faux — install via
  CI/pipe), ne pas prompter, juste imprimer l'URL. Pendant shell du `skipifsilent`.
- **Parité Windows** : l'Inno Setup actuel n'a PAS cette étape (il enregistre + démarre la
  tâche, sans proposer d'ouvrir l'UI). À **rétro-ajouter** côté Windows pour rester iso —
  une ligne `[Run]` vers `protocol0-launcher.exe` avec `Flags: postinstall skipifsilent
  nowait` et `Description: "Open Protocol 0"`. (Petit suivi Windows, hors de ce jalon mac
  mais à noter pour ne pas diverger.)

## Décisions tranchées

- **Cycle de vie launchd : TOUT-SHELL.** `install.sh` copie un template de plist,
  substitue le chemin du binaire + `$HOME`, et lance lui-même
  `launchctl bootstrap gui/$(id -u)`. **Pas** de subcommand `--*-service` sur l'agent.
  Raison : le seul vrai gain du subcommand (skhd/yabai) est de résoudre le chemin du
  binaire au runtime, motivé par les préfixes Homebrew variables — driver **absent chez
  nous** (notre installeur place le binaire à un chemin stable qu'on choisit). L'hybride
  n'apporterait que du code launchd **non testable sans Mac** dans le binaire distribué,
  et diverge de Windows (qui pilote `schtasks` depuis le `.ps1`, pas depuis l'exe). Un
  `--restart-service`/status reste possible en **backlog** si un `make`/tap Homebrew le
  justifie un jour.
- **Launcher mac : `.app` MINIMAL** (cf. « Composants distribués » §2). Pas de binaire
  PyInstaller. Idiomatique, porte l'icône proprement, zéro TCC, ~10 lignes.

## Toutes éditions de Live 12 (Intro / Standard / Suite) — contrainte forte

Protocol0 cible **Live 12 uniquement** (Python 3.11) mais **doit** marcher sur toutes ses
**éditions**. Sur Windows, le préfixe d'exe `"ableton live "` + le numéro de version y
suffisent. Sur macOS c'est plus subtil et le **match par nom est fragile** (recherche
sourcée, cf. Sources `ableton-detect`) :

- **Le nom du `.app` est renommable et l'édition n'y est pas fiable.** Par défaut
  `Ableton Live <MAJOR> <Edition>.app` (ex. `Ableton Live 12 Suite.app`), mais Ableton
  documente le renommage pour faire cohabiter plusieurs versions → on ne peut pas s'y fier.
- **L'exécutable est `Contents/MacOS/Live`** quelle que soit l'édition → le process `comm`
  est juste `Live` (trop générique ; aucune trace d'édition ni de version).
- **La clé robuste, identique sur toutes éditions** : `CFBundleIdentifier ==
  com.ableton.live` ; la **version** se lit dans `CFBundleVersion` (on exige le majeur 12).

**Règle unique adoptée — bundle id + version 12 :**
- **Install (détection du bundle)** : énumérer les `.app` de `/Applications` **et**
  `~/Applications` (préfiltre nom `^Ableton ` juste pour éviter de lire tous les plists),
  garder ceux dont `CFBundleIdentifier == com.ableton.live` (via
  `mdls -name kMDItemCFBundleIdentifier <app>` ou
  `/usr/libexec/PlistBuddy -c 'Print CFBundleIdentifier' "<app>/Contents/Info.plist"`)
  **ET** dont `CFBundleVersion` a un majeur `== 12`. S'il en reste plusieurs (ex. 12.0 et
  12.4) → la plus récente par `CFBundleVersion`. **S'il n'en reste aucun → erreur
  « Ableton Live 12 required » + exit non-zéro**, jamais de fallback sur 10/11. Installer
  dans `<app>/Contents/App-Resources/MIDI Remote Scripts/`.
- **Runtime (`process_check` + `foreground`)** : résoudre le bundle id de l'app lancée /
  au premier plan (`lsappinfo`) et comparer à `com.ableton.live`. (Au runtime on ne
  re-vérifie pas la version : si l'install a réussi, c'est un Live 12 ; et un utilisateur
  qui lance un autre Live n'a de toute façon pas le script chargé.)

**Bêtas** : une beta Live 12 s'installe comme app séparée mais **porte le même bundle id**
→ un match par id seul ne l'exclut PAS (et son `CFBundleVersion` est aussi majeur 12, donc
elle passe le filtre). Si on veut l'écarter, ajouter un check sur le token `Beta` dans le
nom du bundle. **Décision MVP** : ne pas sur-filtrer — si la beta 12 est l'install la plus
récente, l'utilisateur la vise probablement ; l'override manuel reste le filet.

**Édition réelle, si jamais besoin** (pas pour le MVP) : `Contents/Resources/
Installation.cfg` → champ `.variant` (`Suite`/`Standard`/`Intro`/`Lite`), pas le nom de
fichier.

## À trancher (avant implémentation)

- **Format exact rapporté par `lsappinfo` / chemins shell** : la recherche confirme le
  bundle id et les chemins, mais le format brut de sortie de `lsappinfo info -only bundleID`
  (guillemets, espacement) n'est pas byte-vérifié sans Mac. Idem la confirmation visuelle
  que `mdls`/`PlistBuddy` lisent bien le bon plist. **À valider par l'ami testeur** ; le
  mode debug `P0_AGENT_DEBUG=1` est là pour ça.

## Best practices OSS — installeur macOS non signé (synthèse, sourcée)

Étudié contre **skhd**, **yabai** (les deux jumeaux les plus proches : daemon clavier
macOS, non signé, LaunchAgent, TCC), **Karabiner-Elements** (référence d'autorité sur la
permission TCC clavier) et **Syncthing**/**Hammerspoon** (daemon + UI web locale,
autostart). Sources en bas de section.

**Convergence (défaut sûr — tout le monde s'accorde) :**
1. **launchctl moderne** : `bootstrap gui/$(id -u) <plist>` / `bootout` / `kickstart -k`,
   jamais `load`/`unload` (skhd, yabai). La machine d'état skhd vaut d'être copiée :
   `print` (probe) → `enable` → `bootstrap` si non chargé, sinon `kickstart`.
2. **LaunchAgent per-user** dans `~/Library/LaunchAgents/`, label reverse-DNS,
   `RunAtLoad=true`, `KeepAlive={SuccessfulExit:false, Crashed:true}`. **Pas de
   LaunchDaemon root** : seul Karabiner en a un, pour son driver HID — nous n'en avons
   pas besoin (un tap clavier ne demande pas root, juste la session GUI).
3. **Logs dans `~/Library/Logs/`** (Syncthing) — pas `/tmp` (verrue skhd/yabai).
4. **Config hors payload** → préservée à l'uninstall par construction (Karabiner,
   Syncthing). Notre `shortcuts.json` l'est déjà.

**Divergence — la vraie décision :** plist auto-généré par subcommand (skhd/yabai, car
chemin Homebrew variable) vs template statique copié (Syncthing). Tranché en « À trancher »
ci-dessus (hybride recommandé).

**Le quarantine, personne ne le documente** : ni Syncthing ni Hammerspoon ne traitent
Gatekeeper pour un binaire non signé. C'est à nous : `xattr -dr com.apple.quarantine`
dans `install.sh` (déjà prévu).

## TCC — permission clavier (le plus gros risque, corrigé après recherche)

**Quelle permission ?** Dépend du mode du `CGEventTap`, et pynput le choisit au runtime
selon `suppress`/`intercept` (`pynput/_util/darwin.py`) :
- `kCGEventTapOptionListenOnly` (observe, ne modifie/avale rien) → **Input Monitoring**
  (`CGPreflightListenEventAccess` / service TCC `ListenEvent`).
- `kCGEventTapOptionDefault` (peut modifier/avaler) → **Accessibility** (`AXIsProcessTrusted`).

Notre `listener.py` est **observe-only** (pas de `suppress=True`, pas d'intercept ; il lit
la combo et laisse passer la touche) → pynput prend **ListenOnly → Input Monitoring**.
Donc **diriger l'utilisateur vers Input Monitoring** d'abord. (pynput appelle aussi
`AXIsProcessTrusted()` pour son propre diagnostic, et logge un message « not trusted » qui
parle d'Accessibility → mentionner Accessibility en secours, sans en faire le défaut.)

**`install.sh` ne peut pas accorder TCC** (aucune API d'octroi scriptable, seulement
`tccutil reset` pour révoquer). Donc :
1. `xattr -dr com.apple.quarantine` sur les binaires (sinon Gatekeeper bloque).
2. **Ad-hoc codesign avec un identifier stable** (`codesign -s - --identifier
   live.protocol0.agent <binaire>`) : ancre la clé TCC sur un identifier constant plutôt
   que sur un cdhash qui change à chaque build PyInstaller — atténue la perte de grant à
   chaque update (cf. ci-dessous).
3. Imprimer les instructions + **deep-link** vers le volet :
   `x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent`
   (Input Monitoring ; `…?Privacy_Accessibility` en secours).
4. Après accord : `launchctl kickstart -k gui/$(id -u)/live.protocol0.agent`.

**Non signé = grant TCC cassé à CHAQUE update** (cdhash churn) — c'est le mode d'échec
n°1 documenté chez skhd (#371, #312) et yabai. Mitigations :
- chemin d'install **stable** (la clé TCC inclut le chemin) ;
- **ad-hoc codesign --identifier stable** (point 2) ;
- **détection runtime** : l'agent sert une UI web → quand le tap ne reçoit aucun event /
  `not trusted`, afficher dans la SPA un bandeau « permission perdue — ré-accorder ici »
  avec le deep-link. Avantage que skhd/yabai (sans UI) n'ont pas — à exploiter via
  `/status` (ajouter un état `permission_missing` ?). **Piste à creuser, hors MVP.**
- documenter la recette de récupération : `tccutil reset ListenEvent live.protocol0.agent`
  (+ `Accessibility`), puis re-toggle.

## Vérification — protocole de test (l'ami)

1. Build : `build_agent_binary.sh` → `dist/protocol0-agent` (binaire) + `Protocol0.app`
   (assemblé) ; `stage_remote_script.sh` →
   `build/stage/Protocol_0/{__init__.py,protocol0/,VERSION}`.
   (La SPA `src/frontend/dist` doit être buildée avant.)
2. Install : `install.sh` (sudo pour le bundle uniquement ; tester défaut auto-détecté +
   override). Vérifier binaire agent (chemin stable + codesign ad-hoc),
   `/Applications/Protocol0.app`, plist `live.protocol0.agent`, `Protocol_0/` dans le bundle.
   **Prompt final** « Open Protocol 0 now? [Y/n] » : « Y » → le `.app` ouvre la SPA ;
   en pipe/non-TTY → pas de prompt, juste l'URL imprimée.
2b. **Live 12, toutes éditions** : la détection trouve le bon `.app` quelle que soit
   l'édition de **Live 12** (idéalement Intro/Standard/Suite si dispo, sinon au moins une
   édition + un `.app` renommé pour confirmer que c'est le **bundle id**, pas le nom, qui
   décide). Plusieurs Live 12 (ex. 12.0 + 12.4) → le plus récent (`CFBundleVersion`).
   **Sans Live 12** (ou seulement Live 11) → `install.sh` affiche « Ableton Live 12
   required » et sort en non-zéro, sans rien copier.
3. Permission : accorder **Input Monitoring** (en secours Accessibility) au binaire agent ;
   `launchctl kickstart -k gui/$(id -u)/live.protocol0.agent`.
4. Agent : `launchctl print …` tourne ; `agent.log` → « keyboard listener started »,
   « web server listening on http://127.0.0.1:9010 » + version.
5. **Launcher / web** : ouvrir `http://127.0.0.1:9010/shortcuts` (ou cliquer le
   launcher) → la SPA charge **même Ableton fermé**. Le StatusPill affiche `no_ableton`.
6. Ableton : redémarrer Live ; Control Surface → « Protocol 0 ». `runtime.json` apparaît,
   StatusPill passe `ready`.
7. Port : l'URL du script (port dynamique) répond ; `/status` du launcher reflète l'état.
8. Fonctionnel : combo + Ableton focus → action + log `combo … -> …` ; autre app focus →
   `ignored (Ableton not foreground)` (le match foreground se fait sur le bundle id
   `com.ableton.live`). Si KO → relancer avec `P0_AGENT_DEBUG=1` (logge le bundle id
   détecté au premier plan).
9. Autostart : logout/login → agent relancé.
10. Crash-restart : `kill <pid>` → KeepAlive relance.
11. Uninstall : `uninstall.sh` → tout retiré, **`shortcuts.json` préservé**.

## Risques

- **Foreground non testable sans Mac** — la règle (match `com.ableton.live` via
  `lsappinfo`) est sourcée, mais le format brut de sortie `lsappinfo`/`osascript` n'est pas
  byte-vérifié ; best-effort + mode debug. Risque principal.
- **Détection bundle/process par id + version 12** — repose sur `CFBundleIdentifier ==
  com.ableton.live` (validé par `ableton-detect`) + `CFBundleVersion` majeur 12. Le bundle
  id est stable sur toutes les éditions, mais **pas une garantie vendeur** pour un futur
  Live 13 (id possiblement inchangé → le filtre `== 12` resterait le garde-fou). Les
  **bêtas Live 12 partagent le même id ET le majeur 12** → non exclues par défaut (cf.
  « Toutes éditions »).
- **TCC Input Monitoring** — binaire non signé : accord **manuel** (aucune API d'octroi),
  et **grant perdu à chaque update** (cdhash churn). Mitigé par chemin stable + ad-hoc
  codesign + détection runtime, mais reste **le plus gros risque UX mac**. `install.sh`
  guide (deep-link + instructions) mais ne peut pas auto-accorder.
- **pynput `vk`/`char` sur macOS non vérifié** — fallback char non testé sous
  modificateurs.
- **Bundle app + sudo + update de Live** — écrire dans le bundle exige sudo et **casse à
  chaque mise à jour de Live** (dossier recréé) → réinstall nécessaire. Contrepartie
  assumée du choix iso-Windows (vs User Library).
- **Stdlib-only côté SCRIPT** — le remote script doit le rester ; `appdata_dir()`
  n'utilise que `os`/`sys`. (L'agent, lui, a déjà `requests` + `pynput` : pas une
  contrainte stdlib, juste à embarquer via PyInstaller.)
- **Cmd→`win`** — token `win` = Cmd sur mac ; portable, documenté.
- **Serveur web 9010** — port fixe partagé Win/mac ; collision gérée par le retry
  d'arrière-plan (`web/server.py`), le clavier continue de fonctionner.

## Sources (recherche best practices OSS)

- skhd — service launchd + launchctl + Accessibility :
  [`src/service.h`](https://github.com/koekeishiya/skhd/blob/master/src/service.h),
  [`src/skhd.c`](https://github.com/koekeishiya/skhd/blob/master/src/skhd.c),
  [README](https://github.com/koekeishiya/skhd/blob/master/README.md). cdhash/TCC churn :
  [#371](https://github.com/koekeishiya/skhd/issues/371),
  [#312](https://github.com/koekeishiya/skhd/issues/312) ;
  recette `tccutil reset` : [skhd.zig UPGRADING.md](https://github.com/jackielii/skhd.zig/blob/main/docs/UPGRADING.md).
- yabai — `--*-service`, plist généré, codesign pour préserver le grant :
  [`src/misc/service.h`](https://github.com/koekeishiya/yabai/blob/master/src/misc/service.h),
  [man page](https://raw.githubusercontent.com/koekeishiya/yabai/master/doc/yabai.asciidoc),
  [README](https://github.com/koekeishiya/yabai/blob/master/README.md).
- Karabiner-Elements — Input Monitoring vs Accessibility, fichiers installés, config :
  [required-macos-settings](https://karabiner-elements.pqrs.org/docs/manual/misc/required-macos-settings/),
  [installed-files](https://karabiner-elements.pqrs.org/docs/help/advanced-topics/installed-files/),
  [security (session GUI)](https://karabiner-elements.pqrs.org/docs/help/advanced-topics/security/).
- pynput — choix du mode de tap (ListenOnly vs Default) :
  [`_util/darwin.py`](https://github.com/moses-palmer/pynput/blob/master/lib/pynput/_util/darwin.py),
  [limitations](https://pynput.readthedocs.io/en/latest/limitations.html),
  [échec silencieux #389](https://github.com/moses-palmer/pynput/issues/389).
- Apple — mapping permission/tap :
  [Developer Forums thread 122492](https://developer.apple.com/forums/thread/122492),
  [silent-disable race](https://danielraffel.me/til/2026/02/19/cgevent-taps-and-code-signing-the-silent-disable-race/).
- Hammerspoon — prompt Accessibility via API :
  [`MJAccessibilityUtils.m`](https://github.com/Hammerspoon/hammerspoon/blob/master/Hammerspoon/MJAccessibilityUtils.m),
  [FAQ (tccutil reset)](https://www.hammerspoon.org/faq/).
- Syncthing — plist LaunchAgent documenté, config-as-files :
  [`etc/macos-launchd/syncthing.plist`](https://github.com/syncthing/syncthing/blob/main/etc/macos-launchd/syncthing.plist),
  [autostart](https://docs.syncthing.net/users/autostart.html),
  [config](https://docs.syncthing.net/users/config.html).
- Ableton macOS — bundle id / chemins / éditions (détection edition-agnostique) :
  [`stonegray/ableton-detect`](https://github.com/stonegray/ableton-detect)
  ([`scanApplication.js`](https://github.com/stonegray/ableton-detect/blob/main/src/scanApplication.js) :
  `CFBundleIdentifier === 'com.ableton.live'`, `Contents/MacOS/Live`, `Installation.cfg`
  `.variant`, parse `CFBundleVersion` ;
  [`getAppPaths.js`](https://github.com/stonegray/ableton-detect/blob/main/src/getAppPaths.js) :
  `/Applications` + `~/Applications`) ;
  MIDI Remote Scripts path `Contents/App-Resources/MIDI Remote Scripts/` :
  [Ableton KB](https://help.ableton.com/hc/en-us/articles/209072009-Installing-third-party-remote-scripts),
  [laidlaw42 README](https://github.com/laidlaw42/ableton-live-midi-remote-scripts) ;
  frontmost via `lsappinfo` :
  [Cycling74 forum](https://cycling74.com/forums/detect-when-ableton-is-the-currentfront-application-on-an-os) ;
  bêtas installées séparément :
  [Ableton KB](https://help.ableton.com/hc/en-us/articles/115001663870-Live-Beta-FAQ).
  *(KB Ableton citée via extraits de recherche — l'hôte renvoie 403 au fetch automatisé.)*
