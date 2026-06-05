# Systray + autostart par Startup folder (révise « pas de systray » du Jalon 2)

Suite des Jalons 1 et 2 (`docs/specs/done/2026-06-01-windows-installer-jalon-*.md`). Cette spec
change **deux** choix de fond pour rendre l'install/setup le plus **idiomatique et non-invasif**
possible — qu'un utilisateur ne voie pas « un keylogger caché qui tourne en arrière-plan » :

1. **L'autostart passe de la tâche planifiée Windows à un raccourci dans le Startup folder.**
2. **L'agent porte une icône systray** (visible, avec un Quit un-clic).

Toujours **Windows uniquement**.

## Pourquoi ce revirement

Le Jalon 2 avait explicitement **rejeté le systray**. Ce rejet reposait sur le fait que le tray
aurait pointé vers la page servie par le *script* (qui vit et meurt avec Ableton) — « ouvrir la
config » serait tombé sur une page morte. **L'architecture a changé** : c'est désormais l'**agent**
(process toujours vivant, indépendant d'Ableton) qui sert lui-même la page launcher sur le port
fixe `9010` et calcule `/status` (`src/agent/agent/web/status.py`). L'objection tombe : un tray porté
par l'agent a toujours une page vivante derrière lui, et `/status` lui donne déjà les trois états
(`no_ableton` / `script_inactive` / `ready`).

### Autostart : Startup folder, pas tâche planifiée

- **Modèle des analogues les plus proches.** AutoHotkey et **Espanso** (tous deux : global keyboard
  hook + systray + desktop app, exactement notre profil) utilisent le **Startup folder**, pas un
  scheduled task ni une clé Run.
- **Le scheduled task se justifie pour d'autres besoins que les nôtres.** PowerToys l'utilise pour
  l'**élévation silencieuse** au logon ; Syncthing le *propose* parmi trois options (Startup folder,
  task, service NSSM) pour le cas serveur « tourne sans session ouverte »
  (https://docs.syncthing.net/users/autostart.html). Un hook `WH_KEYBOARD_LL` n'a **pas** besoin
  d'élévation → aucune de ces raisons ne s'applique.
- **Contrôle utilisateur > robustesse au crash.** On est en beta ; l'agent ne crashe pas en usage
  normal. La priorité est que l'user **voie** et **désactive facilement** ce qui se lance : un `.lnk`
  Startup est listé et togglable dans **Gestionnaire des tâches → Démarrage** (surface native
  Windows), là où une tâche planifiée est cachée. On accepte donc de **perdre le restart-on-crash**
  (`RestartCount 999`) que donnait le task — **sans watchdog de remplacement** (over-engineering pour
  la beta ; le crash se verrait dans `agent.log` et on reverrait la décision au besoin).
- **Pas un argument antivirus.** Changer de mécanisme ne réduit pas le flag AV : Espanso, en Startup
  folder, est quand même détecté `Trojan:Win32/Bearfoos.A!ml` (espanso#2499). Le vrai levier reste le
  **code signing** (backlog `docs/specs/todo/2026-06-02-installer-code-signing.md`). Le Startup
  folder est choisi pour l'**ergonomie/contrôle**, pas pour l'AV.

### Systray

Une icône visible + un **Quit** un-clic transforment la lecture « spyware » → « un outil que je fais
tourner ». Une icône de tray est de l'**UI**, pas un comportement : les heuristiques AV flaggent le
hook + l'autostart, pas un `Shell_NotifyIcon` (Espanso ship un tray *et* est flaggé — ce n'est pas le
tray qui déclenche).

## Comportement

### Systray (porté par l'agent)

- Icône = le « P » badge (`installer/assets/protocol0.ico`), embarqué dans l'exe.
- **Clic-gauche** (action par défaut) : ouvre `http://127.0.0.1:9010/shortcuts` dans le navigateur
  (la page que l'agent sert déjà).
- **Clic-droit (menu)** :
  - une ligne de **statut** non-cliquable reflétant `status.compute()`
    (no_ableton / script_inactive / ready), rafraîchie périodiquement ;
  - **Open config** → même chose que le clic-gauche ;
  - **Open releases page** → ouvre la page releases dans le navigateur (un **lien**, jamais un
    download+exec — garde le profil AV propre ; « check for updates » in-app reste abandonné comme au
    Jalon 2) ;
  - **Quit** → arrêt propre (`web.stop()`, `listener.stop()`) puis sortie du process.
- Tourne sur son propre thread daemon, comme le serveur web : ne bloque ni la boucle principale ni le
  listener pynput.

### Lancement à la main

L'icône Menu Démarrer / bureau **lance l'agent** (modèle AHK « on clique pour démarrer »), au lieu
de seulement ouvrir le navigateur. Le mutex single-instance (`single_instance.acquire()`) rend un
2e lancement inoffensif (no-op). Au lancement manuel, l'agent ouvre aussi la page config.

### Autostart

- Raccourci `Protocol 0.lnk` dans le Startup folder de l'utilisateur (`{userstartup}`), cible
  `Protocol0.exe` **sans `--open`** (le lancement au logon doit être silencieux, pas ouvrir
  un onglet navigateur à chaque session). Créé par l'installeur via la section **`[Icons]`** d'Inno
  (pas de PowerShell), **gaté sur une case « Start Protocol 0 at login »** (cochée par défaut).
  Inno le retire automatiquement à la désinstallation.
- L'user le désactive à tout moment via Gestionnaire des tâches → Démarrage ou en supprimant le
  `.lnk`.

### Élévation (installeur admin + raccourci per-user)

L'installeur tourne **admin** (écrit dans Program Files + le dossier Ableton), mais l'autostart est
**per-user**. Deux conséquences gérées :
- Le **raccourci Startup** est posé par `[Icons]` sous `{userstartup}` (sous admin install mode, ça
  cible le profil de l'utilisateur qui installe — le bon pour un outil desktop mono-utilisateur).
- Le **démarrage immédiat** de l'agent (`[Run]`) utilise le flag **`runasoriginaluser`** : l'agent
  doit tourner dans la **session interactive de l'utilisateur loggé** (le hook clavier bas-niveau et
  le foreground check y vivent), pas dans le contexte élevé. Il n'a besoin d'aucun droit admin.
- `UsedUserAreasWarning=no` assume explicitement cette écriture per-user voulue.

## Upgrade

Les versions antérieures installaient une **tâche planifiée `Protocol0`**. À l'install, on la
supprime (`schtasks /Delete /TN "Protocol0" /F`) avant de poser le `.lnk` Startup, sinon les deux
coexistent et l'agent se lance deux fois (double hook clavier → raccourci en double).

## Hors périmètre

- Watchdog / restart-on-crash (assumé, cf. ci-dessus).
- « Check for updates » in-app (toujours abandonné — profil dropper).
- Code signing (backlog séparé).
- Portage Mac.

## Vérification

Voir la section « Vérification » du plan : install propre (case cochée → `.lnk` + tray « P »),
clic-gauche/droit du tray, Quit qui tue le process, logon/logoff, désactivation par l'user,
single-instance, **upgrade depuis une version à tâche planifiée** (l'ancienne tâche disparaît, un
seul agent tourne), désinstall (shortcuts.json préservé), case décochée.
