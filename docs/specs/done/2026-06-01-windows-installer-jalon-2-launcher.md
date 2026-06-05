# Installeur Windows — Jalon 2 : launcher web + découverte de port

Suite du Jalon 1 (`docs/specs/done/2026-06-01-windows-installer-jalon-1.md`), qui livre
l'installeur Inno Setup, l'exe `protocol0-detector.exe` autonome (PyInstaller) et son autostart
en tâche planifiée au logon. Le Jalon 2 donne un **point d'accès visible** à l'utilisateur (un
raccourci Windows + une page de diagnostic) et fiabilise la **découverte du port** du serveur HTTP.

Toujours **Windows uniquement**, pas de portage Mac (les helpers sont isolés pour un futur portage).

## But

1. **Point d'accès** : l'utilisateur doit pouvoir ouvrir la config Protocol0 depuis un raccourci
   Windows, et obtenir un message clair quand ce n'est pas possible (Ableton fermé, ou control
   surface pas activée) plutôt qu'une page d'erreur navigateur.
2. **Découverte de port robuste** : ne plus dépendre d'un port `9000` câblé qui crashe le chargement
   du script s'il est pris.

## Décision d'architecture — pas de systray

> **Révisé (2026-06-05)** — décision inversée par
> `docs/specs/in-progress/2026-06-05-systray-and-startup-folder-autostart.md`. L'objection ci-dessous
> (« le systray pointe vers une page qui meurt avec Ableton ») ne tient plus : c'est désormais
> **l'agent** — process survivant — qui sert la page launcher sur `9010` et calcule `/status`, donc un
> tray porté par l'agent a toujours une page vivante derrière lui. L'autostart bascule aussi du
> scheduled task vers un raccourci Startup folder.

La première version de cette spec prévoyait une **icône systray** (pystray). Abandonnée :

- **Le systray ne couvre pas le cas d'échec principal.** Le serveur de la page de config est servi
  par le script *dans* Ableton : il vit et meurt avec Ableton. Quand Ableton est fermé, « ouvrir la
  config » tombe sur une page morte. Le message utile ne peut venir que d'un process qui survit à
  Ableton — le **detector**.
- **Profil antivirus.** Le detector est déjà un keylogger gelé (profil sensible). Une icône systray
  aggrave le profil « malware ». Inspiration Syncthing : son core est headless, le tray vit dans des
  projets séparés.
- **Moins de code, moins de binaire.**

À la place : **raccourci Windows + page launcher servie par le detector.**

## Hors périmètre

- Systray (abandonné, cf. ci-dessus).
- **« Check for updates » / mise à jour en-app** (abandonné) : l'utilisateur met à jour lui-même en
  re-téléchargeant l'installeur. Garde le profil AV propre (pas d'appel sortant ni de download +
  lancement d'.exe). Une mise à jour reste un acte explicite et manuel.
- Signature de code / SmartScreen (souhaitable à terme — backlog `installer-code-signing.md`).
- Portage Mac.

## Launcher web (servi par le detector)

Le detector — toujours vivant via la tâche planifiée — sert une petite page sur un **port fixe
9010** (thread daemon, ne bloque ni la boucle principale ni le listener pynput). Le raccourci
Windows pointe dessus en dur (donc pas de fallback de port côté launcher ; si 9010 est pris, le
launcher log et réessaie en arrière-plan, le clavier continue de fonctionner).

`GET /status` calcule l'un de trois états ; la page (HTML/JS inline, zéro build) le poll toutes les
~2 s :

- **`no_ableton`** (process Ableton absent) → « Protocol0 is accessible only when Ableton is running. »
- **`script_inactive`** (Ableton lancé mais `/health` du script injoignable) → « Please activate the
  Protocol0 remote script inside Ableton (Preferences → Link/Tempo/MIDI). »
- **`ready`** (script joignable) → redirige vers `<script_url>/shortcuts` (l'UI réelle).

Chaque message d'échec porte un lien d'aide vers https://www.protocol0.live/.

La distinction `no_ableton` vs `script_inactive` s'appuie sur une **détection du process Ableton par
nom** (préfixe `"ableton live "`, exclut `Ableton Index.exe`) en plus de la joignabilité du script.

## Découverte de port

- **Script** : tente `9000` ; si pris, bind un port libre choisi par l'OS. Publie l'URL effective dans
  `%APPDATA%\Protocol0\runtime.json` au démarrage, supprime le fichier à `disconnect()`.
- **Detector** : `ScriptClient` résout l'URL **à chaque appel** (le detector survit à plusieurs
  sessions Ableton, chacune sur un port potentiellement différent) — via `runtime.json`, ou
  `P0_SCRIPT_PORT` comme escape hatch manuel. Absence de fichier = script inactif = no-op.
- Best-practice OSS : port fixe par défaut + fallback + fichier d'adresse (Jupyter / RFC 8252 ;
  Syncthing publie via `config.xml`).

## Installeur

- **Launcher = dedicated exe, not a `.url`.** The clickable shortcut points to
  `protocol0-launcher.exe` (`src/agent/agent/launcher_entry.py`), a tiny PyInstaller
  `--windowed` exe that opens `http://127.0.0.1:9010/` in the default browser then exits. It
  is NOT the resident agent: it merely opens the page served by the agent (started at logon by
  the scheduled task). Port 9010 = `WEB_PORT` on the agent side (single source of truth,
  imported by the launcher).
  - **Why an exe rather than a `.url`**: an Internet Shortcut necessarily takes the browser's
    icon + the shortcut-overlay arrow ("ugly"). An exe carries its own icon — the "P" badge
    (`installer/assets/protocol0.ico`, generated by `scripts/windows/generate_icon.py` from
    `src/website/favicon.svg`) — and, dropped directly on the desktop, has no shortcut overlay.
    Looks like a "real app".
- Shortcuts created via `[Icons]` (Start Menu + desktop), pointing to the launcher exe:
  - Start Menu: always created.
  - **Desktop: optional**, via a `[Tasks]` checkbox "Create a desktop shortcut" (previously
    created unconditionally). The user chooses.
- Upgrade from an earlier version: the old `.url` shortcuts (Start Menu + desktop) are cleaned
  up at install time (`[InstallDelete]`) to avoid a duplicate "Protocol 0".

## Dépend de

- Jalon 1 mergé : exe PyInstaller, `.iss`, tâche planifiée, publication des releases.

## Vérification

- runtime.json apparaît au chargement du script (url/pid/version), disparaît à la fermeture propre.
- Port 9000 occupé → le script bind ailleurs, un raccourci fire toujours.
- Les 3 états du launcher s'affichent correctement (Ableton fermé / control surface non activée / prête).
- `Ableton Index.exe` seul ne déclenche pas l'état « ready » ni « script_inactive » faussement.
- Collision 9010 → log, clavier OK, retry.
- Raccourcis installés (Start Menu + bureau) ouvrent la page ; désinstall les retire.
- The shortcut carries the "P" icon (not the browser icon) and has no shortcut-overlay arrow
  on the desktop (exe dropped directly).
- "Create a desktop shortcut" unchecked → no desktop shortcut; Start Menu present.
- Upgrade from a `.url` version → a single "Protocol 0" (the old `.url` is cleaned up).
