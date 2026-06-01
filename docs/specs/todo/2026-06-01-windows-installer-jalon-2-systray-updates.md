# Installeur Windows — Jalon 2 : systray + mise à jour

Suite du Jalon 1 (`docs/specs/in-progress/2026-06-01-windows-installer-jalon-1.md`), qui
livre l'installeur Inno Setup, l'exe `protocol0-detector.exe` autonome (PyInstaller) et son
autostart en tâche planifiée au logon. Le Jalon 2 ajoute une **présence utilisateur** (icône
systray) et un **mécanisme de mise à jour** déclenché manuellement.

Toujours **Windows uniquement**, pas de portage Mac.

## But

1. **Icône systray** pour le detector — donner une présence visible et un point de contrôle à
   un service qui tourne sinon invisible en arrière-plan.
2. **« Check for updates »** — permettre de mettre à jour le detector + le remote script sans
   réinstaller à la main, mais **sans auto-update silencieux** : c'est l'utilisateur qui clique.

## Hors périmètre

- Auto-update silencieux / en arrière-plan (refusé : la mise à jour reste un acte explicite).
- Signature de code / suppression des avertissements SmartScreen (souhaitable à terme, mais
  traité séparément).
- Portage Mac.

## Icône systray

Ajouter une icône dans la zone de notification Windows, portée par le process detector (ou un
petit process compagnon lancé par la même tâche planifiée). Menu attendu :

- **Ouvrir la config** → ouvre `http://127.0.0.1:9000/shortcuts` (la page déjà servie par le
  remote script) dans le navigateur par défaut.
- **Check for updates** → cf. section suivante.
- **Voir les logs** → ouvre `%APPDATA%\Protocol0\logs\detector.log`.
- **Quitter** → arrête le detector (et désactive temporairement la tâche jusqu'au prochain logon,
  à préciser à l'implémentation).

État visuel : idéalement l'icône reflète si le remote script (:9000) est joignable
(Ableton lancé + control surface actif) vs injoignable. À confirmer selon l'effort.

Choix technique à trancher à l'implémentation : `pystray` (simple, pur Python, s'intègre bien au
bundle PyInstaller existant) vs une lib plus riche. `pystray` est le point de départ recommandé.

La page `/shortcuts` servie par le script reste le lieu principal de configuration ; le systray
n'est qu'un raccourci d'accès + le point d'entrée des updates. (Décision Jalon 1 : on voulait les
deux surfaces — page web ET systray.)

## Check for updates

Décisions actées (Jalon 1) :

- **Source des releases : GitHub Releases.** Les installeurs versionnés y sont publiés
  (`Protocol0-Setup-<version>.exe`).
- **Comportement : télécharge + lance.** « Check for updates » interroge l'API GitHub pour la
  dernière release, compare à la version locale, et si plus récente : télécharge le nouvel
  installeur puis le lance (l'utilisateur confirme l'UAC). **Pas** de téléchargement ni
  d'installation en arrière-plan : l'action est déclenchée manuellement et visible.

À définir à l'implémentation :

- **Où vit la version locale** : embarquée dans l'exe (constante de build) et/ou écrite par
  l'installeur. Doit être lisible par le systray pour la comparaison et affichée dans le menu/about.
- **Couverture de la mise à jour** : l'installeur met à jour **et** le detector (exe) **et** le
  remote script (dossier `Protocol_0`) — l'installeur Jalon 1 fait déjà les deux, donc relancer
  l'installeur suffit. Préserver `%APPDATA%\Protocol0\shortcuts.json` (déjà garanti par le `.iss`).
- **Endpoint exact** : `GET https://api.github.com/repos/<owner>/<repo>/releases/latest`,
  comparaison de tag de version (semver).
- **Arrêt propre du detector** avant que l'installeur n'écrase l'exe (l'installeur Jalon 1 doit
  déjà stopper la tâche ; vérifier la séquence quand le déclencheur est le systray lui-même).

## Dépend de

- Jalon 1 mergé (`docs/specs/.../2026-06-01-windows-installer-jalon-1.md`) : exe PyInstaller,
  `.iss`, tâche planifiée, publication des releases.

## Vérification (esquisse)

- L'icône systray apparaît au logon ; les 4 entrées de menu fonctionnent.
- Avec une version locale < dernière release : « Check for updates » détecte, télécharge et lance
  l'installeur ; après install, la nouvelle version tourne et `shortcuts.json` est préservé.
- Avec une version locale = dernière release : « Check for updates » indique « à jour », ne fait rien.
- « Quitter » arrête bien le detector (plus de process, plus de capture clavier).
