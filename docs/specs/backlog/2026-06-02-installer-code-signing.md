# Signature de l'installeur (code signing commercial)

## Problème

`Protocol0-Setup-<version>.exe` n'est signé par aucun certificat Authenticode. À
l'exécution, la boîte UAC affiche **« Éditeur : Inconnu »** en jaune (warning), et
Windows SmartScreen peut bloquer le premier lancement (« Windows a protégé votre
PC »). C'est purement cosmétique aujourd'hui — l'install fonctionne — mais ça donne
une impression peu fiable, surtout si l'installeur est distribué hors du cercle perso.

À noter : le champ `MyAppPublisher "Thibault Lebrun"` du `.iss` n'a **aucun** effet
sur la boîte UAC (elle ne lit que la signature cryptographique) ; il n'apparaît que
dans « Programmes et fonctionnalités » après install. L'installeur reste de toute
façon admin (écriture dans `C:\ProgramData\Ableton` + Program Files), donc le prompt
UAC apparaîtra toujours — la signature en change seulement la couleur/texte.

## But

Signer l'exe (et idéalement aussi `protocol0-detector.exe`) avec un certificat de
**code signing commercial** pour que :
- la boîte UAC affiche « Éditeur : Thibault Lebrun » en bleu (plus de warning jaune),
- SmartScreen ne bloque plus (immédiat avec un certificat **EV** ; progressif avec un
  **OV** le temps de bâtir la réputation).

## Périmètre

- **Choisir/acheter un certificat** de code signing (OV ~75-200 €/an, EV ~250-400 €/an,
  chez DigiCert, Sectigo, SSL.com, etc.). Décision + coût à la charge de l'utilisateur ;
  ne peut pas être automatisé. EV supprime le warning SmartScreen dès la 1re signature.
- **Câbler la signature dans le build** : Inno Setup supporte la directive `SignTool`
  dans `installer/protocol0.iss` + définition de l'outil via `ISCC /Ssigntool=...`.
  Signer à la fois le Setup et, en amont (`build_detector_exe.ps1`), l'exe détecteur
  avec `signtool.exe sign /fd SHA256 /tr <timestamp-url> ...`.
- **Horodatage (timestamp)** obligatoire (`/tr` + serveur RFC 3161) pour que les
  binaires restent valides après expiration du certificat.
- **Documenter** la procédure (où vit le certificat/clé, comment ne pas le committer)
  dans le README de l'installeur ou ce dossier.

## Hors périmètre

- Certificat auto-signé : n'enlève le warning que sur les machines où le certif est
  importé dans le magasin de confiance ; inutile pour distribuer. Non retenu.
- Rendre l'installeur non-admin : impossible tant que le remote script vit sous
  `C:\ProgramData\Ableton` (imposé par Ableton). Sans rapport avec la signature.

## Notes

- Ne **jamais** committer le certificat (.pfx) ni son mot de passe. Le passer au build
  via variable d'environnement / magasin de certificats Windows, pas en clair dans le
  `.iss`.
- Lié au Jalon 2 (systray + updates, cf. `docs/specs/todo/`) : un updater qui télécharge
  des binaires a d'autant plus besoin que ceux-ci soient signés et vérifiables.
- Priorité basse tant que l'usage reste perso / petit cercle — le warning jaune est
  acceptable à ce stade.
