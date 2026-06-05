# Debug — un raccourci charge plusieurs devices (ex. ctrl+alt+u → 2-3 Utility)

**✅ RÉSOLU.** Cause racine : **deux instances zombies du detector** tournaient en parallèle,
lancées vers 00:39/00:40 par d'anciens shells de test (`poetry run detector` / `make detector`)
non nettoyés. Elles dataient d'**avant** les deux fixes (auto-repeat `a61a8843` à 14:47,
mutex `4c6a6443` à 17:00) : donc deux listeners pynput **sans aucune protection**. Chaque frappe
était doublée (deux captures au même ms — cf. paires dans `detector.log`), et un maintien était
démultiplié par l'auto-repeat **× 2 instances** → plusieurs dizaines de chargements.

La "contradiction centrale" (1 press pynput mais 2 requêtes HTTP ~50 ms d'écart) est ainsi levée :
1 press **par instance**, 2 instances → 2 requêtes séquentielles.

Le test décisif manquant (capture d'un **maintien**) a enfin été fait, code à jour, **après** avoir
tué les zombies : un maintien de ~1,3 s a produit **1 seul `FIRE` + 24 `BLOCKED`** sur `vk=85`
(`u`), sans aucun `on_release` intercalé. → La dédup front-montant `_held_keys` (`a61a8843`)
**fonctionne**, l'auto-repeat arrive bien en `PRESS×N`. Aucun debounce temporel n'a été nécessaire.

Le mutex single-instance (`4c6a6443`) empêche désormais la récidive ; les zombies lui étaient
antérieurs, d'où leur survie. Vérifié en conditions réelles : un seul `make detector`, Ableton
focus, maintien de ctrl+alt+u → **un seul** Utility chargé.

---

Ci-dessous, le topo d'investigation conservé pour mémoire (hypothèses testées, preuves récoltées).

## Symptôme

Dans Ableton, `ctrl+alt+u` (mappé sur load device "Utility") charge **plusieurs** Utility pour
une frappe (1, 2 ou 3, davantage si la touche est tenue).

## Architecture concernée (rappel)

- **detector** (`src/detector/`) : exe PyInstaller, lancé par une tâche planifiée Windows
  `Protocol0` au logon. Capte le clavier (pynput), résout la combo, envoie un
  `GET /device/load?name=...` au script.
- **script** (`src/remote-script/`) : tourne DANS Ableton, sert un serveur HTTP sur `127.0.0.1:9000`,
  reçoit la requête et charge le device via `DeviceService.load_device`.
- Chaîne : frappe → pynput `on_press` → `ShortcutListener._handle_main_key` → `client.execute`
  → `GET /device/load` → script `load_device`.

## Fichiers clés

- `src/detector/detector/listener.py` — capture clavier + dédup (voir hypothèse 2).
- `src/detector/detector/script_client.py` — `execute()` envoie la requête HTTP (1 par appel).
- `src/remote-script/protocol0/application/http/routes/device_routes.py` — `load_device` (retourne None
  → fire-and-forget via le Router).
- `src/remote-script/protocol0/application/http/Router.py` — dispatch ; handler sans retour = `submit()`
  sur le thread Live, handler avec retour = attente.
- `src/remote-script/protocol0/application/http/HttpServer.py` — serveur + `_drain` (traite la queue).

## Hypothèses testées

### H1 — Double instance de detector → INFIRMÉE
- Observé : 2 process `protocol0-detector.exe`.
- **Mais** `ParentProcessId` montre que c'est le pattern **PyInstaller onefile** : un bootloader
  parent + l'app enfant. Confirmé par les threads (parent=1 thread, enfant=5 threads) et le fait
  qu'un seul (l'enfant) tient le launcher 9010.
- Log : `keyboard listener started` n'apparaît **qu'une fois** par démarrage. → **un seul vrai
  listener**.
- Fix tenté quand même (mutex single-instance, commit 0.9.2) : inutile pour ce bug, mais pas
  nuisible. Cf. `src/detector/detector/single_instance.py`.

### H2 — Auto-repeat clavier (Windows répète on_press touche tenue) → FIX TENTÉ, INSUFFISANT
- Doc Win32 (MS Learn) : une touche tenue émet `KEYDOWN, KEYDOWN, …, KEYUP` (plusieurs press, UN
  seul release). `KBDLLHOOKSTRUCT` n'a aucun flag "repeat".
- Fix (commit 0.9.1) : dédup front-montant dans `listener.py` — set `_held_keys` des touches
  non-modificatrices tenues, on n'agit que si absente, on retire au release. Tests unitaires OK
  (`tests/test_listener_autorepeat.py`).
- **MAIS le bug persiste après ce fix.** Donc soit l'auto-repeat n'est pas (seul) en cause, soit
  le dédup est défait par un `on_release` émis entre chaque répétition (ce qui contredirait la
  doc Win32 — à vérifier sur la machine).

### H3 — AutoHotkey (ancien système) en parallèle → INFIRMÉE
- `AutoHotkey.exe` tournait (PID 31340), lancé via raccourci `mappings.ahk.lnk` dans le dossier
  Startup, cible `D:\dev\scripts\mappings.ahk`.
- **Mais** lecture du fichier : `mappings.ahk` ne contient **NI** `ctrl+alt+u`, **NI** appel à
  `:9000`/`load_device`. Il ne fait que des remaps média + 2 raccourcis Ableton (`^+z`, `^!q`),
  et filtre sur `ahk_exe Ableton Live 12 Suite.exe`.
- De plus l'Ableton actif est **Live 12.4.1** (≠ "12 Suite"), donc le `#IfWinActive` d'AHK ne
  matcherait même pas. → AHK hors de cause.

## PREUVES DURES récoltées

### Capture pynput brute, frappe BRÈVE de ctrl+alt+u (`_capture_events.py`)
Une seule frappe brève produit **exactement** :
```
PRESS ctrl_l
PRESS alt_l
PRESS vk=85 (u)      ← UN seul press de 'u'
REL  vk=85 (u)       ← UN seul release
REL  ctrl_l
REL  alt_l
```
→ pynput livre **1 press / 1 release** pour une frappe brève. Pas de doublon au niveau clavier
pour un appui court.

⚠️ **Non encore capturé : une frappe TENUE** (~2 s). C'est LA mesure manquante pour trancher H2 :
voir si le maintien donne `PRESS,PRESS,PRESS…` (dédup devrait bloquer) ou `PRESS,REL,PRESS,REL…`
(dédup défait → il faut un debounce temporel).

### Log du detector (`%APPDATA%\Protocol0\logs\detector.log`)
Frappe tenue ~1 s → ~10 lignes `combo ctrl+alt+u -> load_device` espacées de **~100 ms**
(cadence d'auto-repeat Windows). Parfois 2-3 lignes au **même milliseconde**.

### Log du script Ableton (`%APPDATA%\Ableton\Live 12.4.1\Preferences\Log.txt`)
Le script reçoit `HTTP GET /device/load?name=Utility` **par paires espacées de ~30-50 ms** :
```
17:22:55.909  HTTP GET /device/load?name=Utility
17:22:55.959  HTTP GET /device/load?name=Utility
```
→ **Deux requêtes HTTP partent réellement** pour ce qui devrait être une action. L'écart ~50 ms
(pas le même ms) suggère deux émissions séquentielles, pas deux hooks simultanés.

## Contradiction centrale à résoudre

- Capture pynput (frappe brève) = **1 press**.
- Mais detector.log + script.log montrent **2+ actions** par frappe.

Deux pistes non encore élucidées :
1. **Le comportement diffère entre frappe brève (1 event) et frappe tenue (auto-repeat)** — très
   probable. Le dédup `_held_keys` devrait gérer l'auto-repeat SI pynput envoie press répétés sans
   release. À CONFIRMER par la capture d'un maintien (cf. ci-dessus).
2. **L'exe installé ne contient pas forcément le dernier code** lors des tests — voir piste métier
   ci-dessous.

## Difficulté méthodologique (importante)

Impossible d'obtenir une fenêtre de test propre "**zéro detector pendant que l'utilisateur tape**" :
- La tâche planifiée `Protocol0` relance le detector ; `Stop-Process` ne le supprime que
  temporairement.
- **Le shell de l'agent n'est PAS admin** → `schtasks /Change /DISABLE` échoue (Access denied),
  donc impossible de désactiver la tâche depuis l'agent.
- Conséquence : plusieurs mesures "detector tué" étaient potentiellement faussées (le detector a pu
  revenir entre le kill et la frappe).

## Instrumentation en place (à nettoyer ensuite)

- `src/detector/detector/listener.py` — un log `DIAG on_press ...` ajouté en tête de `_on_press`
  (logge key, vk, `id(self)` du listener, thread id, état `_held_keys`). **Présent dans les
  SOURCES, pas dans l'exe installé** (il faut rebuild l'exe OU lancer `poetry run detector` depuis
  les sources pour le voir).
- `src/detector/_capture_events.py` — script de capture brute des events pynput (TEMPORAIRE).

## Prochaines étapes proposées (non faites)

1. **Capturer un maintien** de ctrl+alt+u avec `_capture_events.py` → trancher définitivement si
   l'auto-repeat arrive en `PRESS×N` (dédup ok à corriger) ou `PRESS/REL×N` (debounce temporel
   requis). C'est LE test décisif manquant.
2. **Faire tourner le detector depuis les sources** (`poetry run detector`, code instrumenté DIAG)
   pendant qu'on tape, après avoir garanti qu'aucun exe installé ne tourne (nécessite de désactiver
   la tâche → besoin d'un shell admin, OU `! ...` lancé par l'utilisateur).
3. Vérifier le **timing exact** des 2 requêtes côté script : si elles correspondent à 2 `combo`
   distincts dans detector.log au même ms vs à 100 ms → distingue "double traitement d'un event"
   de "auto-repeat".
4. Solution probable finale : **debounce temporel** dans le listener (ignorer la même combo si
   re-déclenchée < ~250 ms) — robuste quel que soit le mode de livraison pynput, là où le dédup
   front-montant par état peut être défait si des releases s'intercalent.

## Commits liés (sur main)

- `0.9.1` fix(detector): trigger shortcut once per keypress, not on auto-repeat (dédup front-montant)
- `0.9.2` fix(detector): enforce single instance via named mutex (H1, finalement hors-sujet)

## Note de revue

Le diagnostic a coûté plusieurs allers-retours et 2 fix qui n'ont pas réglé le symptôme. La cause
n'est PAS établie avec certitude. Les deux faits les plus fiables à exploiter :
(a) une frappe **brève** = 1 seul press pynput ; (b) le script reçoit **2 requêtes ~50 ms d'écart**.
Réconcilier ces deux faits (probablement via le comportement d'une frappe **tenue**, non encore
capturée) est la clé.
