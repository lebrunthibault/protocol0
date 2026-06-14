# Generated smart actions + verification (feature B)

> Parent : [2026-06-13-agentic-vision](2026-06-13-agentic-vision.md)
>
> **Dépendances** : [action-catalog](2026-06-13-action-catalog.md) — fournit (a) le **catalogue
> typé** qui sert de vocabulaire au DSL, et (b) les **fakes LOM mutants** qui servent d'oracle à
> la boucle de vérification.

## Context

Transformer un prompt en **smart action réutilisable** : l'agent **génère du code fonctionnel**
qui devient une `@action` assignable à un raccourci clavier (façon « Claude Code génère du
code »). Une fois généré, l'utilisateur peut **assigner un raccourci et tester immédiatement**,
puis continuer la conversation pour itérer.

Tension à résoudre (du parent) : actions **« sans limite »** vs **fiables**. Réponse = un
**gradient à deux niveaux**, exposé en UX.

## Le gradient à deux niveaux

```
Niveau 1 — DSL composable (fiable, vérifiable, lisible)
   └─ le DSL EST l'explication montrée à l'utilisateur
Niveau 2 — Python brut généré (illimité, vérifié, signalé "moins fiable")
   └─ notification UX "l'agent est parti en mode custom, résultat moins fiable"
```

### Niveau 1 — DSL composable
Evidence (papier Anka : +4.6 pts global, **+40 pts sur le multi-step** vs Python ; itemis :
100 % de validité syntaxique via décodage contraint) → un DSL borné **améliore réellement**
fiabilité + lisibilité, surtout sur les pipelines multi-étapes (= exactement les smart actions).

**MAIS** un vrai langage = ~6 400 LoC d'interpréteur (Anka) : trop cher. La bonne forme : le
DSL **n'est presque rien à construire** car c'est de la **composition sur le catalogue `@action`
typé** (vocabulaire auto-dérivé de `/openapi.json`, grammaire d'adressage déjà spécifiée dans
[action-catalog](2026-06-13-action-catalog.md) sur le modèle ClyphX). Génération **deux-tiers** :
raisonnement libre d'abord (évite la « format tax »), puis **émission DSL contrainte**, puis
**transpilation déterministe** (verbe → appel typé), pas un second passage LLM fragile. Le DSL
sert d'**explication lisible** à l'utilisateur — objectif UX atteint avec le même artefact.

### Niveau 2 — échappatoire Python brut
Pour les conditions/boucles/maths que le DSL n'exprime pas, l'agent génère du **Python brut**,
passé par la **même boucle de vérification**, avec une **notification UX « mode custom, moins
fiable »**. Validé par ClyphX lui-même, qui garde un escape hatch Variables→`song`→LOM.

### Différé — Blockly
Une vue no-code/blocs n'a de sens que comme **vue éditable sur le DSL** (sérialisation JSON),
pas comme système parallèle. À ne construire que si l'édition par non-codeurs devient un
objectif. Confirmé « overkill si le NL marche ».

## La boucle de vérification (poussée d'emblée)

Pipeline, court-circuit au premier échec :

```
générer → lint → tests/propriétés (hypothesis) → exécuter contre fakes LOM
        → sur 1er échec : réflexion (erreur brute + région de code fautive
          + signature du stub concerné devient le message suivant)
        → cap dur (3 itérations, style aider)
        → confirmation humaine one-click avant de sauvegarder l'action
```

### Boucle de correction — style aider
aider (`base_coder.py`) : l'erreur lint/test **brute devient le message suivant** ; cap dur
`max_reflections=3` ; « done » = plus d'erreur. On renvoie la **région de code fautive** + la
**signature du stub concerné**, pas juste la stack.

### Exécution — sous-process, pas sandbox cloud
e2b/Vercel/Firecracker = cloud/Linux → **rejetés** (contredisent local-first). Comme le code de
vérif tourne contre des **fakes LOM in-process sans I/O réel**, le rayon d'explosion est
neutralisé : un **sous-process Python timeout-gardé** (venv de vérif, CWD temp, `setrlimit` où
dispo) suffit. Docker en *opt-in* de durcissement, jamais obligatoire. Variante JS : sous-process
`node` timeout contre des fakes JS.

### Oracle — le piège n°1
Les tests générés par LLM « partagent les défauts du code qu'ils valident » (cycle
d'auto-illusion : le modèle écrit un test qui certifie le bug). Parade :
- **property-based testing** (`hypothesis`) : invariants dérivés de **l'intention**, pas de
  l'implémentation (« après l'action, `song.tracks` a grandi de 1 », « `loop_end ≥ loop_start` »),
  idéalement générés dans un **appel séparé** du générateur de code ;
- **évaluateur distinct du générateur** (evaluator-optimizer d'Anthropic) ;
- **confirmation humaine one-click** (mono-utilisateur desktop : « ce test correspond-il à ce
  que tu voulais ? » est cheap et casse l'auto-illusion).

### Fakes — l'« Ableton virtuel »
Il n'existe **aucun simulateur Ableton headless** OSS — les fixtures de Protocol0
(`tests/domain/fixtures/`) sont une prior-art rare. Les faire passer de *stubs* (`pass`) à
**fakes qui mutent l'état** sur le périmètre que les actions relisent (cette mutation est
produite côté [action-catalog](2026-06-13-action-catalog.md), où chaque action en a besoin pour
son test headless). Garder les fakes honnêtes via une petite **suite de conformité LOM**
rejouée dans le vrai Ableton (contract testing) au bump de version Live.

## Grounding pour la génération

Pas de fine-tuning. Contexte direct (Anthropic *context engineering*) : injecter
`/openapi.json` (signatures exactes), des **exemples d'actions existantes**, la **doc
`Sequence`** (`shared/sequence/Sequence.py` — primitive async incontournable pour toute action
non triviale), et du **LOM grep-able du wiki** (`raw/.../live12/Live.*`). RAG léger sur ces
sources quand le volume dépasse la fenêtre. Le wiki et le code de Protocol0 *sont* la base de
connaissances.

## Sortie / intégration

L'action générée (DSL transpilé ou Python brut vérifié) est chargée par un **nouveau plugin
`smart_actions`** dans le remote script → devient une `@action` → assignable à un raccourci via
le keymapper existant. Flux UX : aperçu (DSL lisible ou Python + badge « mode custom ») →
« assigner un raccourci & tester » → itérer dans le chat.

## Jalons

- **J3 — Boucle de vérification (le cœur dur).** Pipeline lint → property-tests → exécution
  sous-process contre fakes LOM, réflexion sur échec (cap 3), confirmation humaine. Suite de
  conformité LOM rejouable dans le vrai Ableton.
- **J4 — Niveau 1 (DSL composable).** DSL = composition typée du catalogue, génération deux-tiers,
  transpilation déterministe → `@action`. Aperçu lisible + « assigner & tester ».
- **J5 — Niveau 2 (échappatoire Python brut).** Génération Python libre passée par la même
  boucle, notification UX « mode custom ».
- **J6 — (différé) Blockly** comme vue éditable sur le DSL.

## Pièges

- **Ne pas faire confiance à un test généré par le LLM seul** — propriétés issues de l'intention
  + évaluateur distinct + confirmation humaine.
- **Pas de sandbox cloud** — fakes sans I/O ⇒ sous-process timeout suffit.
- **Pas de vrai langage DSL** — composition sur actions typées, transpilée déterministiquement.
- **Pas de Blockly tant que le NL+DSL suffit.**

## Vérification

Une smart action générée passe lint + propriétés + exécution fakes, est assignée à un raccourci,
et **fait réellement la bonne chose dans Ableton** ; le fallback Python affiche bien la
notification « mode custom ». Régression : suite de conformité LOM (fakes ↔ vrai Ableton) verte
au bump de version Live.

## Sources

- DSL — [Anka, DSL pour codegen LLM fiable (arXiv 2512.23214)](https://arxiv.org/html/2512.23214v1) ·
  itemis [How to Constrain Your Dragon](https://medium.com/itemis/large-language-models-for-domain-specific-language-generation-part-2-how-to-constrain-your-dragon-e0e2439b6a53) ·
  [Self-Planning Code Generation (arXiv 2303.06689)](https://arxiv.org/abs/2303.06689) ·
  [Format Tax (arXiv 2604.03616)](https://arxiv.org/pdf/2604.03616) · [Blockly](https://en.wikipedia.org/wiki/Blockly)
- Codegen + vérif — aider [base_coder.py](https://github.com/Aider-AI/aider/blob/main/aider/coders/base_coder.py) ·
  [lint/test docs](https://aider.chat/docs/usage/lint-test.html) ·
  [RestrictedPython n'est pas un sandbox](https://github.com/zopefoundation/RestrictedPython)
- Oracle — [LLM test oracles capturent l'implémentation buggée (arXiv 2410.21136)](https://arxiv.org/pdf/2410.21136) ·
  [Property-based testing pour valider la codegen (arXiv 2506.18315)](https://arxiv.org/html/2506.18315v1) ·
  Fowler [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) ·
  [Consumer-driven contract testing](https://pactflow.io/what-is-consumer-driven-contract-testing/)
- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
  (evaluator-optimizer) · [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Wiki — `[[sdk-transactions]]`, `[[sdk-resources-et-filesystem]]`, `[[live-object-model]]`
