# Plan d'exploration : release p0 comme gestionnaire de raccourcis Ableton

## Context

Question d'exploration pure (pas d'implémentation immédiate). L'user envisage de release p0 sous une forme grand public : un **gestionnaire de raccourcis clavier customisables** pour Ableton, avec une UI d'édition et un layer type AutoHotkey qui intercepte les raccourcis et déclenche les actions actuellement exposées par le script (endpoints HTTP localhost:9000).

Trois questions sous-jacentes :
1. Peut-on **hacker Ableton** pour ajouter des entrées de menu natives ?
2. Sinon, quelle **archi UI externe** : page web hébergée, localhost, ou app desktop ?
3. Review du projet **Live Enhancement Suite (LES)** qui fait quelque chose de proche.

Objectif du plan : document factuel + reco d'archi claire pour le release. **Pas de pas-à-pas d'implémentation.**

---

## État des lieux p0 actuel

Recherche faite sur `D:\dev\p0`. Voir agent Explore ([rapport détaillé](question-d-exploration-pure-par-expressive-acorn-agent-Explore.md)).

- **Communication Ableton** : Remote Script Python (`script/protocol0/application/Protocol0.py`) via ControlSurface + LOM + MIDI. Pas d'OSC.
- **Réception commandes** : double serveur HTTP :
  - Script `:9000` — `ThreadingHTTPServer` stdlib avec drain thread-safe sur le tick Live (`script/protocol0/application/http/HttpServer.py` + `Router.py`). Routes : `/device/load`, `/track/select`, `/song/toggle_follow`, `/clip/key_detected`, `/set/get_state`.
  - Backend `:9001` — FastAPI/uvicorn lancé comme Scheduled Task pour les jobs lourds (analyse tonalité MIDI).
- **UI actuelle** : aucune. `p0_web` legacy supprimé. Tk absent. Interaction uniquement via raccourcis AHK (le code AHK a été retiré du repo au commit `bc183da0`).
- **Mapping raccourcis → actions** : non-configurable. Routes HTTP hardcodées en Python, chacune mappe directement à un service via container DI. Pas de registre d'actions énumérable.
- **AHK/keyboard hooks** : aucune lib intégrée actuellement.

**Conclusion** : p0 a déjà la moitié backend du release potentiel (script + endpoints HTTP). Il manque (a) un **registre d'actions énumérable et exposable**, (b) une **UI de mapping**, (c) un **layer hotkeys** qui remplace AHK retiré.

---

## Q1 — Hacker Ableton pour des entrées de menu natives

Recherche menée sur l'écosystème Max for Live, Remote Scripts, hacks communautaires.

| Option | Faisabilité | Verdict |
|---|---|---|
| **Max for Live device** | Officiel | Confiné à la **device chain** (hauteur 169px figée). Pas d'API pour menu global, top bar, browser. Fenêtres flottantes (`thispatcher window flags float`) buggées : passent derrière Live, cassent fullscreen, topmost ne marche pas. |
| **Remote Script Python** | Officiel | **Aucun élément UI custom**. Juste `Live.Application.show_message` (status bar read-only écrasée par Live en permanence) et `log_message`. Confirmé via julienbayle/StudioTalk, nsuspray/Live_API_Doc. |
| **DLL injection / reverse** | Hacky | **Aucun projet open-source connu** n'injecte de l'UI dans `Live.exe`. Push 2 (officiel Ableton) reverse le hardware, pas l'app. Disqualifié pour release : updates Live cassent tout, EULA, AV, signature requise. |
| **Overlay window externe** | Réaliste | Fenêtre topmost transparente collée à Live. **Précédent fonctionnel : [Advanced Toolbar Buttons v2](https://maxforlive.com/library/device/8132) de killihu** (M4L + barre transparente, Windows-only, maintenu en 2025). Trade-offs : vol de focus au clic, fullscreen Ableton problématique, multi-monitor nécessite WinEvent hooks pour suivre la fenêtre Live. |
| **TouchOSC / Lemur** | HS grand public | Friction install énorme (app séparée + bridge + template). OK pour power-users iPad, pas pour release mass-market. |

**Verdict Q1** : pas de menu natif possible sans hack risqué. **Overlay window est l'unique option "fausse UI dans Ableton"** et reste suffisamment fragile (focus, fullscreen) pour ne pas en faire le pilier du produit. **Out-of-scope pour le MVP** ; éventuellement V2 si demande.

---

## Q2 — Archi UI externe

Recherche sur contraintes navigateur 2025-2026 et patterns établis.

### Contraintes navigateur clés

- **Local Network Access (LNA)** : Chrome 142 (28 oct 2025) et Edge 143 ajoutent un **prompt de permission** quand une origine publique (https://tib-tools.com) fait `fetch("http://127.0.0.1:...")`. Preflight `OPTIONS` avec `Access-Control-Request-Private-Network: true`, serveur doit répondre `Access-Control-Allow-Private-Network: true` + CORS classique.
- **Mixed content** : `http://127.0.0.1` reste traité comme secure origin → pas bloqué, mais LNA prompt s'applique.
- **Le prompt LNA est anxiogène pour un non-tech** ("votre réseau local"), même si techniquement le clic est unique.
- **loopback → loopback** (UI servie par le script lui-même) : pas de prompt LNA, pas de CORS du tout.

### Recommandation : **site vitrine séparé + UI localhost servie par le script**

- **tib-tools.com** = site marketing statique (landing, features, screenshots, download installer, docs). Pas d'UI de config dessus.
- **UI de config** = SPA statique buildée (Vite/équivalent), shippée comme dossier `static/` dans le repo, servie par le serveur HTTP du script sur `http://127.0.0.1:9000/`. Auto-ouverte au lancement (`webbrowser.open`).

### Pourquoi pas tout sur tib-tools.com

- LNA prompt à la première utilisation = friction UX et signal "danger" pour un user non-tech.
- CORS preflight à configurer côté serveur Python (~10 lignes), gérable mais une source de bugs en plus.
- Persistance des mappings : soit localStorage navigateur (perdu au clear, pas portable), soit backend tib-tools (compte user, infra, RGPD — contredit le statut legacy de `p0_web` qui a été abandonné).

### Pourquoi servir la SPA depuis le script est OK

Inquiétude initiale : "ça fait pas trop de servir une SPA direct depuis le script ?". Non :

- Une SPA buildée = quelques fichiers statiques (HTML/CSS/JS bundle ~500KB). `ThreadingHTTPServer` sait déjà servir des fichiers, il faut juste ajouter une route catch-all `SimpleHTTPRequestHandler` sur un dossier `static/`.
- ~30 lignes Python, zéro nouvelle dépendance, zéro cold-start.
- Précédents directs : **Bitfocus Companion** (Stream Deck pros, sert son UI sur `:8000`), **Jupyter**, **Plex**, **Home Assistant**, **OBS**, **Ollama**, **ComfyUI**, **Stable Diffusion WebUI**, **qBittorrent**, **Sonarr**. C'est le pattern standard pour les outils créatifs/dev qui pilotent un daemon local.

### Adoucir le côté "localhost ça fait peur"

- **Auto-open** : `webbrowser.open("http://127.0.0.1:9000")` au démarrage du script → l'user voit son navigateur s'ouvrir sur une UI brandée, il ne tape jamais d'URL.
- **Branding** : nom produit en gros, design soigné → ça fait sentir "app", pas "page de debug".
- **Site marketing rassurant** : tib-tools.com fait le travail de vente et de docs.

### Persistance des mappings

JSON dans `%APPDATA%\p0\shortcuts.json` (Windows) / équivalent OS. Source unique, zéro réseau, portable, versionable avec un champ `schema_version` pour les migrations futures.

---

## Q3 — Layer hotkeys (remplacer AHK)

Choix user : **Python intégré au script** (un seul process, config rechargée à chaud).

### Comparatif rapide (Windows 2026)

| Lib | Admin requis | Suppression frappe | Verdict |
|---|---|---|---|
| **`keyboard` (boppreh)** | Oui sur Windows pour bas niveau | Oui (`suppress=True`) | Puissant, mais UAC = friction install |
| **`pynput.GlobalHotKeys`** | Non (sauf Task Manager / jeux fullscreen) | Limité | Bon défaut cross-platform, **recommandé** |
| **AHK v2 sous-process** | Non | Excellent | Le plus fiable Win32 historiquement mais ré-introduit AHK, deux runtimes à shipper, antivirus false-positives connus |
| **`ahk` wrapper Python** | Comme AHK | Oui | Compromis, mais embarque AHK quand même |

**Reco** : commencer avec **`pynput`** dans le même process que le serveur HTTP. C'est cross-platform (Mac/Linux futur), pas d'UAC, fiable pour des combos `Ctrl+Shift+X` etc. Si suppression de la frappe originale s'avère insuffisante dans certains contextes (Ableton fullscreen, modifier keys exotiques), fallback `keyboard` ou AHK v2 sous-process en option avancée.

### Reload à chaud

Bénéfice de l'intégration in-process : quand l'user save un mapping dans l'UI, le handler HTTP `POST /shortcuts/save` écrit le JSON **et** appelle `hotkey_manager.reload()` sur le listener pynput. Latence zéro, pas de redémarrage script, pas de polling, pas de WebSocket nécessaire.

---

## Q4 — Review Live Enhancement Suite (LES)

Review détaillée. [Rapport agent complet](question-d-exploration-pure-par-expressive-acorn-agent-LES.md).

### Le scoop principal

**LES est officiellement discontinué** ([enhancementsuite.me/discontinued](https://enhancementsuite.me/discontinued)). Le créateur a jeté l'éponge, justification : "Live 12 a intégré la plupart des features nativement". Code MIT, forks explicitement encouragés. Pas de support Live 12 prévu. Mainteneur redirige vers Shortcut Buddy (M4L) et LoadR.

### Stack LES — important à comprendre

- **Windows** : AutoHotkey v1 monolithique, **un seul `.ahk` de 3422 lignes** (l'auteur lui-même : *"this source code is a complete mess"*), compilé Ahk2Exe, installer Inno Setup **non signé**.
- **Mac** : codebase **complètement séparée**, fork de Hammerspoon + Lua. Mainteneur différent. Zéro code partagé.
- **Détection Ableton** : juste `#IfWinActive ahk_exe Ableton Live.+` (regex sur nom d'exe).
- **Aucun Remote Script Python, aucun MIDI, aucun IPC, aucun parsing .als**. 100% hotkeys synthétiques envoyés à la fenêtre. Une seule exception : un companion M4L "InsertWhere" pour l'insertion de plugin.
- **Config** : pas de GUI. Édition manuelle de `menuconfig.ini` et `settings.ini`. Syntaxe maison fragile (le fichier doit *impérativement* finir par un commentaire "Readme", sinon crash).

### Santé chiffrée

- 220 stars Windows / 148 Mac.
- Dernière release Windows v1.3.5 (juin 2024 selon page releases, sources contradictoires), Mac v1.3.3 mai 2023.
- ~19/32 issues ouvertes, pas de merge récent.
- Un seul mainteneur par plateforme, projet de fan, financement par donations.

### Avantage structurel pour p0

1. **LOM via Remote Script Python** : accès aux objets (tracks/devices/clips/automation), pas string-match de libellés. Les issues LES #25, #33 (shortcuts cassés sur Live en Espagnol/Allemand car match des libellés de menu) **n'existent simplement pas** avec p0.
2. **HTTP + UI web** : cross-platform gratuit. p0 a une codebase unique, LES en a deux à maintenir.
3. **Live 12** : créneau libre.
4. **Pas de false-positive antivirus** (AHK compilé est notoirement flag par Defender — sujet récurrent forums AHK).

### À repomper de LES

- **Format de menu INI** pour le quick device menu (killer feature de LES, le radial qui apparaît au clic milieu).
- **Project timer** (trivial, valeur perçue forte).
- Liste de hotkeys "évidentes" qui ont fait leur preuve : Buplicate (Ctrl+B = duplication ×7), Close all plugin windows, Clear clips on hover, Save versioned, scale stamping piano roll.
- **Modèle de distribution** : MIT + GitHub releases + Inno Setup = standard de facto pour ce public.

### Pièges à éviter

- Ne pas livrer un AHK pur (AV false positives garantis).
- Ne pas string-matcher les menus Ableton (LES en souffre sur non-EN).
- **Signer l'installer** ou au minimum publier les hashes SHA256.
- **Auto-update dès le jour 1** (LES n'en a pas, chaque release = réinstall complète).
- JSON + schema versionné pour la config, pas un parser INI maison fragile.
- Positionnement : pas "remplaçant de LES" frontal (Shortcut Buddy et LoadR ont la mindshare des successeurs M4L). Positionner sur "ce que AHK ne pouvait pas faire" = **deep LOM integration + UI web vraie**.

---

## Recommandation d'architecture finale

```
┌─────────────────────────────────────────────────────────────────┐
│                      tib-tools.com                              │
│   Site vitrine statique : landing, features, install, docs      │
│            (HTML statique, hébergé n'importe où)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ download installer
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                Installer Windows (Inno Setup signé)             │
│  → copie le Remote Script dans le dossier Ableton User Library  │
│  → installe le service Python (script + backend déjà existants) │
│  → enregistre la scheduled task wscript.exe shim (cf. memory)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ au lancement
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           Service Python (script Ableton + backend)             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ThreadingHTTPServer :9000                              │   │
│  │  - Routes /action/* (registre énumérable, exposable)    │   │
│  │  - Route /shortcuts (GET/POST mappings JSON)            │   │
│  │  - Route static catch-all → sert la SPA buildée         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  pynput.GlobalHotKeys (même process)                    │   │
│  │  - charge shortcuts.json                                │   │
│  │  - reload à chaud sur POST /shortcuts                   │   │
│  │  - sur trigger → appelle la route /action/* in-process  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Persistance : %APPDATA%\p0\shortcuts.json (versionné)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ webbrowser.open() au démarrage
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│       SPA dans navigateur : http://127.0.0.1:9000/              │
│  - liste les actions disponibles (GET /actions)                 │
│  - éditeur de mappings shortcut → action                        │
│  - save → POST /shortcuts → reload à chaud                      │
│  - design brandé pour ne pas sentir "page de debug"             │
└─────────────────────────────────────────────────────────────────┘
```

### Composants à construire (résumé non-pas-à-pas)

1. **Registre d'actions** côté script : remplacer le décorateur `@route("GET", path)` actuel par un registre qui énumère les actions (id, label, description, params optionnels), et expose `GET /actions` pour la SPA. Aujourd'hui les routes sont énumérables dans `Router.py` mais sans metadata user-facing.
2. **SPA** : framework au choix (Vite + Svelte/Solid recommandés pour bundle léger), build statique committé dans `static/` du script. Pas de backend, juste fetch contre `:9000`.
3. **Layer hotkeys** : `pynput.GlobalHotKeys` listener dans un thread daemon du script, lecteur de `shortcuts.json`, callback qui dispatch sur le registre d'actions.
4. **Persistance** : module simple lecture/écriture JSON dans `%APPDATA%\p0\`.
5. **Auto-open navigateur** : une ligne `webbrowser.open` au démarrage du script (`Protocol0.__init__` ou équivalent).
6. **Site vitrine** : statique, n'importe quel hébergeur (GitHub Pages, Cloudflare Pages, Vercel).
7. **Installer** : Inno Setup signé (certificat code signing ~$200/an chez SSL.com ou équivalent — ou GitHub releases avec hashes publiés en V1 si budget limité).

### Out-of-scope MVP

- Overlay window topmost dans Ableton (feature V2 si demande utilisateurs).
- Backend tib-tools.com avec comptes user / sync cloud.
- Compatibilité macOS (le script p0 actuel est très Windows-centré ; gérer Mac plus tard).
- Companion M4L device pour intégration plus profonde.

---

## Vérification (pour la phase d'implémentation future)

Quand viendra le moment de coder :

- **Smoke test SPA** : `curl http://127.0.0.1:9000/` retourne le HTML, `curl http://127.0.0.1:9000/actions` retourne le JSON des actions.
- **Smoke test hotkey** : enregistrer `Ctrl+Alt+T` → appeler une action visible (ex : toast dans la status bar Ableton via `show_message`), vérifier le déclenchement.
- **Smoke test reload** : modifier `shortcuts.json` via UI, déclencher l'ancien raccourci doit échouer, le nouveau doit marcher, sans restart.
- **Smoke test installer** : VM Windows propre, installer → lancer Ableton → vérifier que le Remote Script charge et que `:9000` est joignable.
- **Test LNA** : ouvrir Chrome 142+ sur la SPA localhost, vérifier qu'aucun prompt n'apparaît (sinon on a accidentellement introduit une fetch cross-origin).

---

## Fichiers de référence (pour exploration ultérieure)

- `D:\dev\p0\script\protocol0\application\http\HttpServer.py` — serveur HTTP du script (~100 lignes, base pour ajouter static + LNA-aware si jamais)
- `D:\dev\p0\script\protocol0\application\http\Router.py` — mini-routeur (~150 lignes, à étendre avec registre énumérable)
- `D:\dev\p0\script\protocol0\application\http\routes\*` — endpoints existants à wrapper en actions
- `D:\dev\p0\backend\backend\api\http_server\main.py` — backend FastAPI (séparé, garde son rôle de jobs lourds)
- `D:\dev\p0\.env` — `P0_SCRIPT_PORT=9000`, `P0_BACKEND_PORT=9001`

---

## Sources

- Rapports des sous-agents :
  - Explore archi p0 (en mémoire de session)
  - [Recherche extension Ableton](question-d-exploration-pure-par-expressive-acorn-agent-a286519756f075fa1.md)
  - [Recherche archi UI web/localhost](question-d-exploration-pure-par-expressive-acorn-agent-a6321731e9ed875b9.md)
  - [Review Live Enhancement Suite](question-d-exploration-pure-par-expressive-acorn-agent-a9f1786da8cfb3803.md)
- [LES discontinued](https://enhancementsuite.me/discontinued) / [LESforWindows](https://github.com/LiveEnhancementSuite/LESforWindows) / [LESforMacOS](https://github.com/LiveEnhancementSuite/LESforMacOS)
- [Chrome Local Network Access](https://developer.chrome.com/blog/local-network-access) / [Chrome 142 release notes](https://developer.chrome.com/release-notes/142)
- [Advanced Toolbar Buttons v2 (killihu)](https://maxforlive.com/library/device/8132) — précédent overlay topmost
- [Bitfocus Companion](https://bitfocus.io/companion) — exemple canonique du pattern localhost UI
