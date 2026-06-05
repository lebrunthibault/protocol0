# Bundle « script seul » pour power users (sans agent)

**Statut : backlog / à implémenter plus tard.** L'idée est validée, le code viendra
dans une session dédiée. Cette spec décrit le quoi/pourquoi/comment pour démarrer
sans clarification.

## Le sujet

Aujourd'hui le seul chemin d'install est l'installeur Windows (`Protocol0-Setup-<version>.exe`),
qui déploie **trois choses** : l'agent (exe + tâche planifiée d'autostart), le
remote script dans le dossier *MIDI Remote Scripts* d'Ableton, et l'autostart.

Certains **power users** ne veulent que le **remote script** :

- ils veulent gérer eux-mêmes leurs raccourcis clavier (via un autre outil, ou les
  raccourcis natifs d'Ableton) et **ne pas avoir un agent qui tourne** en permanence ;
- ils sont à l'aise pour copier un dossier dans *MIDI Remote Scripts* à la main ;
- ils tournent peut-être sur une plateforme/configuration non couverte par l'exe.

Or le remote script est **stdlib-only** (cf. `scripts/stage_remote_script.py` : pur
copier-coller, pas de vendoring) — il est donc trivial à distribuer seul comme un
simple zip à déposer dans le dossier des remote scripts.

## Objectif

1. **Publier un artefact « script seul »** sur chaque GitHub Release, à côté de
   l'installeur : un zip du dossier `Protocol_0/` prêt à copier dans *MIDI Remote
   Scripts*. Nom proposé : `Protocol0-RemoteScript-<version>.zip`.
2. **Documenter** l'install manuelle pour power users, en bas de
   `src/website/docs/installation.html`, dans une section dédiée (l'actuelle note
   « Want to run from source » pointe vers le README dev ; on veut un chemin
   intermédiaire : *script packagé, pas de build, pas d'agent*).

## Ce qui existe déjà (à réutiliser)

- `scripts/stage_remote_script.py` produit déjà `build/stage/Protocol_0/` avec
  exactement le bon contenu (`__init__.py` = loader prod, `protocol0/` sans tests ni
  `__pycache__`, `VERSION` à la racine du bundle). **C'est le dossier à zipper.**
- `.github/workflows/release.yml` build l'installeur sur tag `v*` et attache l'exe
  via `gh release create ... "$exe"`. Le stage du remote script est déjà fait à
  l'intérieur de `scripts/windows/build_installer.ps1` (étape 3/4).
- Le loader prod (`src/remote-script/script_templates/Protocol_0/__init__.prod.py`) est
  autonome (pas de `__P0_SOURCE_DIR__` à remplacer, contrairement au loader dev).

## Implémentation proposée

### 1. Produire le zip en CI

Dans `release.yml`, après le build de l'installeur (le stage existe déjà sous
`build/stage/Protocol_0/`), ajouter une étape qui zippe ce dossier en
`dist-installer/Protocol0-RemoteScript-<version>.zip` — l'archive doit contenir le
dossier `Protocol_0/` à sa racine (pour qu'un simple « extraire dans MIDI Remote
Scripts » donne `.../MIDI Remote Scripts/Protocol_0/`).

- Lire la version depuis le fichier `VERSION` (déjà présent à la racine du repo).
- `Compress-Archive -Path build/stage/Protocol_0 -DestinationPath dist-installer/Protocol0-RemoteScript-<version>.zip`.
- Attacher l'asset : ajouter le zip à la liste de `gh release create` (passer l'exe
  **et** le zip).

Point d'attention : s'assurer que `build_installer.ps1` n'a pas nettoyé
`build/stage/` avant cette étape ; sinon re-lancer `python scripts/stage_remote_script.py`
juste avant de zipper (idempotent, rapide, stdlib-only).

> Alternative plus propre : extraire la fabrication du zip dans un petit
> `scripts/package_remote_script.py` (stdlib `zipfile`, cross-platform) appelé à la
> fois en local (`make package-script` ?) et en CI. Préférable pour tester sans
> pousser un tag. À trancher au moment de l'implémentation.

### 2. Documenter l'install manuelle

Ajouter en bas de `src/website/docs/installation.html` une section
**« Install the remote script only (power users) »** :

- pour qui : ceux qui veulent les actions Protocol 0 dans Ableton **sans l'agent**
  (donc sans les raccourcis clavier globaux gérés par l'agent — ils mappent
  eux-mêmes) ;
- comment : télécharger `Protocol0-RemoteScript-<version>.zip` depuis la release,
  l'extraire dans le dossier *MIDI Remote Scripts* de Live 12 (rappeler le chemin
  type `%ProgramData%\Ableton\Live 12 <edition>\Resources\MIDI Remote Scripts`),
  puis activer la control surface « Protocol 0 » dans les préférences (réutiliser la
  section « Enable the control surface in Live » déjà présente) ;
- limite claire : **sans agent**, pas de web UI de config sur `:9010`, pas de
  raccourcis clavier globaux — seul le remote script tourne dans Ableton.
- garder la note existante « Want to run from source » (README dev) distincte : trois
  niveaux d'install = installeur complet → script packagé (cette section) → from
  source (README).

## Hors scope

- Pas d'auto-update du script seul (l'agent gère ses propres updates via l'installeur ;
  le power user re-télécharge le zip à la main).
- Pas de version macOS spécifique ici — le zip est OS-agnostique (pur Python), mais le
  chemin d'install documenté est Windows ; un addendum macOS suivra la spec
  `docs/specs/todo/2026-06-02-macos-installer.md` le jour venu.

## Note connexe (issue de l'audit multi-version du 2026-06-04)

La détection est maintenant **durcie sur Live 12 uniquement** (glob `Live 12*` dans
l'installeur et `scripts/_pyfind.py`), avec une **préférence pour la Beta** quand une
Beta et une stable de Live 12 coexistent (l'installeur l'indique par un texte inline
sur la page de choix du dossier, pas une pop-up). La
version supportée est centralisée : `SupportedLiveVersion` dans `installer/protocol0.iss`
et `SUPPORTED_LIVE_VERSION` dans `scripts/_pyfind.py` — passer à **Live 13** = changer
ces deux constantes (un endroit par langage, Pascal vs Python, pas de partage possible).

## Vérification (au moment de l'implémentation)

1. Localement : produire le zip, l'extraire dans un dossier *MIDI Remote Scripts*
   factice, vérifier l'arborescence `Protocol_0/{__init__.py, protocol0/, VERSION}`.
2. Charger la control surface dans Live 12 depuis ce dossier (sans agent lancé) et
   confirmer qu'elle s'initialise (serveur HTTP in-Ableton up).
3. Sur un tag de test, confirmer que la release porte **deux** assets : l'exe et le
   zip.
