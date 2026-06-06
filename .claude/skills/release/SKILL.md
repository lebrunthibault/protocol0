---
name: release
description: Publie une release GitHub de Protocol0 — lit la version courante, génère un changelog depuis le dernier tag, le fait valider, puis crée et pousse le tag annoté v<version> qui déclenche le build CI et la publication de l'installeur Windows. Use when the user says "release", "on release cette version", "publish a version", "ship a release". Do NOT bump the version here — c'est /commit qui bump à chaque commit ; /release ne fait que tagger une version déjà bumpée.
allowed-tools: "Bash(git:*) Bash(gh:*) Read Write"
---

# Release

Publie une version déjà bumpée comme **GitHub Release**. Le déclencheur de la release est la
**création d'un tag git `v<version>`** : le workflow `.github/workflows/release.yml` (runner
Windows) build l'installeur, extrait le message d'annotation du tag (`git tag -l --format=%(contents)`)
et le passe à `gh release create --notes-file`. (Pas `--notes-from-tag` : sur un tag annoté poussé
séparément, il retombe sur le message du *commit* pointé, pas du tag.)

**Séparation stricte bump ↔ release :**

- `/commit` bumpe `VERSION` à chaque changement fonctionnel, commit et push — **sans jamais tagger**.
- `/release` (cette skill) **ne bumpe pas**. Il tague la version courante de `VERSION` et pousse le
  tag. Ce push est le seul déclencheur de release.

## Workflow

### Étape 1 — Préconditions

```bash
git rev-parse --abbrev-ref HEAD        # doit être main
git status --short                      # doit être vide (working tree propre)
```

Si le working tree n'est pas propre, ou si on n'est pas sur `main` : **stop** et le signaler.
Une release se fait depuis un `main` propre déjà poussé.

Lire la version à publier depuis le fichier racine `VERSION` :

```bash
cat VERSION                             # ex. 0.1.0  -> tag = v0.1.0
```

### Étape 2 — Garde-fou anti-double-release

Le tag ne doit pas déjà exister (sinon la version a déjà été releasée → il faut d'abord un
`/commit` qui bump) :

```bash
git tag --list "v<VERSION>"                 # doit être vide
git ls-remote --tags origin "v<VERSION>"    # doit être vide
```

Si le tag existe déjà : **stop**. Expliquer que cette version est déjà releasée et qu'il faut
bumper (`/commit`) avant de releaser à nouveau.

### Étape 3 — Générer le changelog

Trouver le dernier tag de version, puis lister les commits depuis :

```bash
git describe --tags --abbrev=0 --match "v*" 2>/dev/null   # dernier tag, ou rien si premier release
git log <dernier-tag>..HEAD --pretty=format:"%s|%h"        # ou tout l'historique si premier release
```

Regrouper les commits par type conventionnel en sections markdown :

- `feat:` / `feat!:` → **### Features**
- `fix:` → **### Fixes**
- `chore:`, `docs:`, `refactor:`, `test:`, autres → **### Other**

Format de chaque ligne : `- <description sans le préfixe de type> (<hash court>)`.

Premier release (aucun tag précédent) : utiliser tout l'historique, ou un simple
`- Initial release` si l'historique est trop verbeux.

**Ne pas** répéter `v<version>` en tête du changelog : le titre de la release est déjà `v<version>`.
Commencer directement par les sections (`### Features`, …) — sinon la version apparaît en double
dans les notes publiées.

### Étape 4 — Faire valider (« édition dans l'éditeur »)

Écrire le changelog généré dans le fichier temporaire `.git/RELEASE_CHANGELOG.txt` (hors arbre de
travail — il servira de message d'annotation du tag), puis **l'ouvrir dans l'éditeur de texte de
l'utilisateur** pour qu'il puisse l'éditer avant de valider :

```bash
# écrire le changelog généré dans .git/RELEASE_CHANGELOG.txt (hors arbre de travail)
# puis l'ouvrir dans l'éditeur configuré, en bloquant jusqu'à fermeture du fichier :
"${GIT_EDITOR:-${VISUAL:-${EDITOR:-notepad}}}" .git/RELEASE_CHANGELOG.txt
```

Sous Windows / PowerShell, ouvrir en attendant la fermeture du fichier :

```powershell
# résoudre l'éditeur (fallback notepad), ouvrir et bloquer jusqu'à fermeture
$editor = if ($env:GIT_EDITOR) { $env:GIT_EDITOR } elseif ($env:VISUAL) { $env:VISUAL } elseif ($env:EDITOR) { $env:EDITOR } else { 'notepad' }
Start-Process -FilePath $editor -ArgumentList '.git\RELEASE_CHANGELOG.txt' -Wait
```

Une fois le fichier refermé, **relire** `.git/RELEASE_CHANGELOG.txt` et montrer le contenu final à
l'utilisateur pour une **confirmation explicite** avant de tagger. Ne pas créer le tag tant qu'il
n'a pas confirmé : c'est un acte public et difficilement réversible (tag + release).

### Étape 5 — Tag annoté + push (le déclencheur)

```bash
git tag -a "v<VERSION>" -F .git/RELEASE_CHANGELOG.txt
git push origin "v<VERSION>"
```

Le push du tag déclenche `.github/workflows/release.yml`. Le message du tag (le changelog) est
repris tel quel par `gh release create --notes-from-tag`.

### Étape 6 — Suivi

Indiquer à l'utilisateur comment suivre la CI et où sera la release :

```bash
gh run watch                                       # suit le build en cours
gh release view "v<VERSION>" --web                 # ouvre la release une fois publiée
```

La release contiendra `Protocol0-Setup-<VERSION>.exe` + les « Source code (zip/tar.gz) »
automatiques de GitHub.

### Étape 7 — Si une release est flaggée (faux positif AV)

L'agent est un hook clavier global, binaire natif (Rust) **non signé** : profil de faux positif
antivirus assumé (cf. `SECURITY.md`). Tant qu'on n'a pas de signature de code
(`docs/specs/in-progress/2026-06-02-installer-code-signing.md`) qui bâtit une réputation, **chaque
release a un nouveau hash** et peut être re-flaggée — donc c'est une étape **manuelle, par
release**, pas automatisable.

**Symptôme typique** : Chrome bloque le téléchargement (« Virus detected ») et/ou Defender flashe
une menace `Trojan:Win32/Wacatac.H!ml` qui disparaît après quelques minutes. Le suffixe `!ml` = un
verdict du **modèle ML cloud** de Defender (pas une signature), déclenché par la feature *block at
first sight* sur un binaire **neuf + rare + non signé**. C'est non-déterministe (fonction du hash et
de l'état du modèle cloud au moment du download) : une release passe, la suivante non. Diagnostic à
confirmer côté machine flaggée :

```powershell
Get-MpThreat | Select-Object ThreatName, SeverityID          # nom exact de la détection
Get-MpThreatDetection | Select-Object InitialDetectionTime, Resources  # quel fichier, quand
```

Si Windows Defender (ou un autre éditeur) flagge l'installeur de cette release, soumettre le
fichier comme faux positif :

- **Microsoft / Defender** : <https://www.microsoft.com/en-us/wdsi/filesubmission> — choisir
  « **Software developer** » → « **Incorrectly detected as malware** », joindre le
  `Protocol0-Setup-<VERSION>.exe` (ou son hash, déjà publié comme asset `SHA256SUMS`), cocher
  « I believe this file is incorrectly detected ». Justification type (à coller, adapter la version) :

  > Open-source Inno Setup installer for Protocol0 (https://github.com/lebrunthibault/protocol0),
  > MIT-licensed. The bundled agent is a native Rust binary (no PyInstaller/packer). The build is
  > fully public: GitHub Actions release workflow from a tagged commit, with a SHA256SUMS asset and
  > a Sigstore build-provenance attestation. VirusTotal shows 0–1/69 (no signature match, at most
  > one ML-only engine). This is an `!ml` heuristic false positive on a new, low-prevalence unsigned
  > build. Source and CI are auditable.

  Le verdict cloud se lève typiquement en **24–72 h**, pour **tous** les utilisateurs (pas que la
  machine qui a soumis).
- **Autres AV** : la plupart ont un portail équivalent de soumission de faux positif (rechercher
  « <vendor> false positive submission »).

Le lien VirusTotal des notes de release aide à constater l'ampleur (quelques flags heuristiques
parmi des dizaines de verdicts propres = faux positif).

> Une fois le **code-signing** en place (réputation d'une identité Authenticode stable), cette étape
> devient rare : Defender cesse de traiter chaque release comme « jamais vu ». Voir
> `docs/specs/in-progress/2026-06-02-installer-code-signing.md`.

## Garde-fous (non négociables)

- **Ne jamais bumper** la version ici — `/release` lit `VERSION`, il ne l'écrit pas.
- **Ne jamais `git push --force`** sur un tag.
- La **validation du changelog** (Étape 4) et la **vérification du tag existant** (Étape 2) sont
  les deux garde-fous contre une release accidentelle ou en double.

## Notes

- Owner/repo : `lebrunthibault/protocol0`. `gh` doit être authentifié (`gh auth status`).
- Si le build CI échoue, le tag reste poussé : corriger la cause, et soit re-déclencher le
  workflow (`gh workflow run` n'est pas câblé — le workflow est `on: push tags`), soit supprimer
  le tag (`git push origin :refs/tags/v<VERSION>` + `git tag -d`) et re-tagger après correctif.
