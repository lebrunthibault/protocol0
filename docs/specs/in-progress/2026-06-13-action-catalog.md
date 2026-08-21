# Action catalog — broad LOM coverage

> Parent : [2026-06-13-agentic-vision](2026-06-13-agentic-vision.md)
>
> **Dépendances** : aucune — c'est le préalable. **Bloque** [nl-chat-control](2026-06-13-nl-chat-control.md)
> et [smart-actions-codegen](2026-06-13-smart-actions-codegen.md) (un catalogue riche est le
> vocabulaire dont les deux ont besoin).

## Context

Aujourd'hui Protocol0 expose **2 actions** (`track/select`, `device/load_device`). Les deux
features agentiques (chat NL, smart actions) n'ont de valeur que sur un catalogue **conséquent**
couvrant une bonne part du Live Object Model (LOM). Ce chantier construit ce catalogue.

Principe directeur : **le catalogue ne se conçoit pas à la main action par action — il se
dérive d'une source machine-readable du LOM, sur un modèle de design déjà éprouvé (ClyphX
Pro), validé contre une checklist de coverage (Max for Live + ableton-mcp).** Le contrat
d'exposition ne change pas : chaque action reste une `@action` (`application/plugin/action.py`)
publiée via `/openapi.json`.

## Source primaire = LOM Live 12 grep-able du wiki

Le wiki contient déjà la meilleure source : `raw/midi-remote-scripts/reference/live12/` —
**43 fichiers `Live.*.runtime.md`** (un par classe : `Live.Song`, `Live.Track`, `Live.Clip`,
`Live.Device`…), Markdown grep-able, **Live 12 courant**, avec signatures C++/Python +
docstrings Ableton. C'est la surface de production réelle atteinte depuis un remote script.

Stratégie d'extraction :
1. Parser chaque fichier → `{classe, méthode/propriété, params, type retour, docstring}`.
2. Filtrer les opérations **actionnables** : setters, `fire()`, `create_*`/`delete_*`/
   `duplicate_*` ; **exclure** accesseurs purs et listeners (ce sont des observables, pas des actions).
3. Produire un catalogue structuré (JSON) → générer les `@action` à partir de là.

Validateur structuré secondaire : `raw/live-object-model-m4l/nsuspray-Live_API_Doc-11.0.0.xml`
(XML parsable, mais **Live 11** — utile pour la *forme*, pas l'inventaire). La page M4L
Cycling'74 du wiki est **Live 8.1b7 obsolète** : à n'utiliser que pour comprendre le
*mécanisme* d'accès (`live.path`/`live.object`/`live.observer`), jamais l'inventaire.

Note version (cf. la décision « Live 12 only ; passer à Live 13 = 2 constantes ») : le
catalogue est régénérable depuis le dossier `live<N>/` correspondant — pas un inventaire figé
à la main.

## Modèle de design = ClyphX Pro (à copier, pas réinventer)

ClyphX Pro a déjà résolu, sur des milliers d'utilisateurs, les problèmes que pose un catalogue
composable. Quatre idées directement transposables (manuel §4 Action Reference, §5 General
Action Information) :

1. **Trois couches séparées** : *Action* (= notre `@action`) / *Action List* (`;`-séparées,
   séquentielles = la « smart action ») / *X-Trigger* (= notre couche keymap/HTTP). **Ne pas
   baker la composition dans les endpoints individuels** — la composition est une couche au-dessus.
2. **Grammaire d'adressage typée** plutôt que des params cible ad hoc : préfixe `track-spec/`
   + spécificateurs typés `DEV(…)`, `CLIP(…)`, `CH(…)`, `PAD(…)`, chacun acceptant
   `index | "nom" | SEL | LAST | ALL | < | > | ranges`. La **notation pointée nichée**
   `DEV(1.2.3)` (3e device de la 2e chaîne du 1er rack) est l'idée la plus copiable pour
   traverser les racks. C'est la grammaire du DSL composable de l'enfant codegen, déjà spécifiée.
3. **Tiers de valeurs uniformes** (3 classes), chacun avec un vocabulaire fixe :
   - *adjustable* (énumérés : routing, warp mode) : `x`, `<`/`>`, `<x`/`>x`.
   - *continuous* (0-127 : volume, params device) : + `x%`, `*x`, `RND`/`RNDx-y`, `RESET`,
     `TGL`, `ENABLE`, `RAMP n`.
   - *quasi-continuous* (unités d'affichage : BPM, gain) : comme continuous sans `%`/random custom.

   → le LLM (et l'utilisateur) apprend **un** système de valeurs, pas un par action.
4. **Escape hatch assumé** : ClyphX expose Variables → `song` → LOM brut + User Actions Python.
   → valide le **niveau 2 (Python brut)** du gradient parent : même un outil mature garde une
   porte vers le LOM complet.

Surface à fort levier / faible coût à mirrorer tôt : convention `ON`/`OFF`/toggle uniforme,
snapshots. La profondeur de coverage ClyphX par type LOM donne l'ordre de priorité naturel
(transport/track/clip/device/mixer/scene = très profond ; browser = moyen).

> **Code source ClyphX disponible (à demander au démarrage de l'implémentation).** Thibault a
> le code de ClyphX quelque part en local — très utile pour s'inspirer de l'**implémentation
> réelle** des actions (au-delà du manuel : comment l'adressage, les tiers de valeurs et les
> User Actions sont codés). **À réclamer explicitement avant d'attaquer ce chantier** ; ne pas
> réimplémenter à l'aveugle ce qui existe déjà comme référence.

## Checklist de coverage = M4L + ableton-mcp (les angles morts)

Le LOM M4L legacy seul **rate** des opérations qu'un vrai outil NL doit couvrir. ableton-mcp
(24 commandes shippées) prouve les **5 cas faciles à manquer** — à mettre explicitement au catalogue :

1. **Browser / chargement de contenu** — `Browser.load_item()`, navigation par URI
   (`get_browser_tree` / `get_browser_items_at_path`). Le `Browser` est **totalement absent de
   la page M4L legacy** alors que c'est le seul moyen d'« ajouter un Wavetable sur cette track ». Cas n°1.
2. **Encodage des notes MIDI** — `Clip.set_notes` / `add_new_notes` avec le tuple
   `(pitch, start, duration, velocity, mute)`. Le legacy ne montre que l'API basée sélection.
3. **Fonctions create/delete/duplicate** — `Song.create_midi_track/create_audio_track/
   create_return_track/delete_track/duplicate_track`, `create_scene/delete_scene`,
   `ClipSlot.create_clip/create_audio_clip` — majoritairement absentes du legacy, présentes en Live 12.
4. **Arrangement (timeline)** — `Track.arrangement_clips`, `duplicate_clip_to_arrangement`
   (Live 11+), absent du legacy.
5. **Heuristiques de classification device** — `can_have_drum_pads` / `can_have_chains` /
   `class_display_name` pour distinguer instrument / effet / rack.

La source primaire (Live 12 grep-able) **contient** déjà ces fonctions ; la liste des 24
commandes ableton-mcp sert de **test de non-régression de coverage** (« ai-je au moins tout ce
qu'eux ont ? »).

## Stratégie retenue

1. **Générer le catalogue semi-automatiquement** depuis `live12/Live.*.runtime.md`.
2. **Structurer selon le modèle ClyphX** : action + grammaire d'adressage typée + tiers de valeurs.
3. **Prioriser par profondeur** : transport / track / clip / device / mixer / scene d'abord ;
   browser / arrangement ensuite.
4. **Valider la coverage** contre les 24 commandes ableton-mcp + les 5 angles morts.
5. **Faire muter les fakes LOM** (`tests/domain/fixtures/`) en parallèle — passer de *stubs*
   (`pass`) à *fakes qui mutent l'état* sur le périmètre que les actions relisent — pour que
   **chaque action soit testable headless dès sa création**. (Détail de la mutation des fakes :
   voir l'enfant [smart-actions-codegen](2026-06-13-smart-actions-codegen.md), qui en dépend
   aussi comme oracle de vérification.)

Le `@action` + OpenAPI existants restent le point d'exposition ; **rien à changer côté contrat** —
les nouvelles actions apparaissent automatiquement dans `/openapi.json` et dans le catalogue
fusionné de l'agent Rust.

## Vérification

- Chaque nouvelle `@action` a un test headless contre les fakes LOM (vert).
- La coverage couvre au moins les 24 opérations d'ableton-mcp + les 5 angles morts.
- Le catalogue se régénère depuis `live<N>/` sans réécriture manuelle (preuve : régénérer
  produit le même set).

## Sources

- [ClyphX Pro User Manual](https://isotonikstudios.com/wp-content/uploads/ClyphX-Pro-User-Manual-1.pdf)
  — §4 Action Reference, §5 General Action Information (grammaire d'adressage, tiers de valeurs,
  3 couches, escape hatch Variables/User Actions).
- [LOM Max for Live (Cycling'74, legacy Live 8.1b7)](https://docs.cycling74.com/legacy/max5/refpages/m4l-ref/m4l_live_object_model.html)
  — mécanisme d'accès ; inventaire obsolète.
- [ableton-mcp remote script](https://github.com/ahujasid/ableton-mcp/blob/main/AbletonMCP_Remote_Script/__init__.py)
  — checklist de coverage (24 commandes), les 5 angles morts.
- Wiki — source primaire `raw/midi-remote-scripts/reference/live12/Live.*.runtime.md`
  (43 classes, Live 12, grep-able) ; validateur `raw/live-object-model-m4l/nsuspray-Live_API_Doc-11.0.0.xml` ;
  pages `[[live-object-model]]`, `[[lom-vue-max-for-live-vs-python]]`, `[[changements-live-11-vers-12]]`.
