---
name: release
description: Publie une release GitHub de Protocol0 — lit la version courante, génère un changelog depuis le dernier tag, le fait valider, puis crée et pousse le tag annoté v<version> qui déclenche le build CI et la publication de l'installeur Windows. Use when the user says "release", "on release cette version", "publish a version", "ship a release". Do NOT bump the version here — c'est /commit qui bump à chaque commit ; /release ne fait que tagger une version déjà bumpée.
allowed-tools: "Bash(git:*) Bash(gh:*) Read Write"
---

# Release

Publie une version déjà bumpée comme **GitHub Release**. Le déclencheur de la release est la
**création d'un tag git `v<version>`** : le workflow `.github/workflows/release.yml` (runner
Windows) build l'installeur et publie la release avec `--notes-from-tag`.

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

### Étape 4 — Faire valider (« auto + édition »)

Montrer le changelog généré à l'utilisateur et lui demander de **valider ou éditer** avant de
tagger. Ne pas créer le tag tant qu'il n'a pas confirmé. C'est un acte public et difficilement
réversible (tag + release).

Écrire le changelog validé dans un fichier temporaire (il servira de message d'annotation du tag) :

```bash
# écrire le changelog final dans .git/RELEASE_CHANGELOG.txt (hors arbre de travail)
```

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
