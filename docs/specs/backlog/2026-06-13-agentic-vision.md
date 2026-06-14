# Agentic chat & generated smart actions — vision

> **Type** : spec vision (chapeau). Roadmap, pas immédiat. Porte le *pourquoi* et
> l'architecture globale ; le détail exécutable vit dans les trois specs enfants ci-dessous.

## Children specs

| Enfant | Périmètre | Statut | Dépend de |
|---|---|---|---|
| [action-catalog](2026-06-13-action-catalog.md) | Étendre massivement le catalogue `@action` (coverage LOM) | backlog | — (préalable à tout) |
| [nl-chat-control](2026-06-13-nl-chat-control.md) | Feature A : chat NL → contrôle Ableton | backlog | action-catalog |
| [smart-actions-codegen](2026-06-13-smart-actions-codegen.md) | Feature B : prompt → smart action générée + vérification | backlog | action-catalog |

Lié à [`2026-06-04-third-party-extension-integration.md`](../in-progress/2026-06-04-third-party-extension-integration.md)
(un agent peut s'exposer comme extension tierce).

## Context — pourquoi

Intégrer des fonctionnalités **agentiques / LLM** dans Protocol0, autour d'une **interface
de chat**, en deux capacités :

- **(A)** Contrôler Ableton en langage naturel (« transpose le clip MIDI sélectionné d'un
  demi-ton », « supprime tous les devices disabled du set »).
- **(B)** Transformer un prompt en **smart action réutilisable** — en **générant du code
  fonctionnel** (Python, ou JS via le SDK Extensions) qui devient une `@action` assignable à
  un raccourci clavier, façon « Claude Code génère du code », avec une **boucle de
  vérification** (lint → tests → exécution dans un « Ableton virtuel »).

### Décisions de cadrage (déterminantes)

1. **Feature A n'est pas « juste appeler les actions existantes ».** Pour ça l'UI +
   raccourcis suffisent. La valeur apparaît quand **le catalogue devient conséquent**
   (dizaines→centaines d'actions couvrant le LOM) — et là MCP devient pertinent. Mais on
   **veut un chat intégré clé en main** (cible : utilisateurs non familiers de Claude
   Desktop). Donc **MCP comme socle + chat intégré par-dessus**, pas MCP seul.
2. **La bibliothèque d'actions actuelle est minuscule** — **2 actions** (`track/select`,
   `device/load_device`) + un plugin exemple désactivé. Le catalogue est le pivot.
3. **Tension assumée** : on veut des actions générables **« sans limite »** tout en restant
   fiables. Compromis : un **ensemble composable couvrant la majorité de ce que fait du
   Python brut**, **+ fallback Python brut** signalé en UX (« mode custom, moins fiable »).
4. **Vérification poussée d'emblée**.

## La tension à résoudre : « sans limite » vs « fiable »

Pas binaire — un **gradient à deux niveaux**, exposé honnêtement en UX :

```
Niveau 1 — DSL composable (fiable, vérifiable, lisible, transpilation déterministe)
   └─ couvre le cas commun ; le DSL est montré à l'utilisateur comme explication
Niveau 2 — Python brut généré (illimité, vérifié par la boucle, signalé "moins fiable")
   └─ échappatoire quand le DSL ne suffit pas ; notification UX "mode custom"
```

**Le facteur limitant n°1 n'est pas le LLM, c'est le catalogue d'actions.** Pour que le
niveau 1 couvre « la majorité de ce que fait du Python brut », il faut étendre massivement le
catalogue — utile en soi (UI/raccourcis, MCP). D'où l'ordre : **catalogue d'abord**.

## Architecture globale

```
┌─────────────────────────────────────────────────────────────────────┐
│ SPA Vue3  ──  Box de CHAT  (nouveau)                                 │
│   feature A: NL → tool-calls sur le catalogue d'actions             │
│   feature B: NL → smart action (DSL ou Python) + aperçu + "assigner  │
│              un raccourci & tester" + suite de la conversation       │
└───────────────┬─────────────────────────────────────────────────────┘
                │ HTTP
┌───────────────▼─────────────────────────────────────────────────────┐
│ SIDECAR LLM  (nouveau process Python, venv propre — PAS le remote    │
│ script stdlib-only)                                                  │
│   • Provider abstrait (Anthropic natif + OpenAI-compatible→Ollama)   │
│   • Boucle tool-calling brute (feature A)                            │
│   • Boucle codegen evaluator-optimizer (feature B):                  │
│        générer → lint → tests/propriétés → exécuter contre fakes LOM │
│        → réfléchir sur 1er échec → cap 3                             │
│   • Grounding: /openapi.json + exemples + Sequence + LOM(wiki)       │
│   • (option) expose aussi un serveur MCP FastMCP.from_openapi()      │
└───────────────┬───────────────────────────────────┬─────────────────┘
                │ POST /api/action/...               │ écrit la smart action
┌───────────────▼──────────────┐      ┌──────────────▼──────────────────┐
│ Remote script (Ableton)      │      │ Nouveau plugin "smart_actions"   │
│   catalogue @action ÉTENDU   │      │   charge les actions générées    │
│   (le grand chantier)        │      │   → deviennent des @action       │
│   + Sequence pour l'async    │      │   → assignables à un raccourci   │
└──────────────────────────────┘      └──────────────────────────────────┘
```

### État des lieux du code (points d'ancrage réels)

| Brique | Fichier | Réutilisé pour |
|---|---|---|
| Décorateur `@action` | `src/remote-script/protocol0/application/plugin/action.py` | exposer une action ; `inspect.signature` = source de vérité du schéma |
| Routeur HTTP + OpenAPI | `application/http/Router.py`, `application/http/openapi.py` | `/openapi.json` 3.1 → catalogue de tools auto-dérivable |
| Primitive async | `shared/sequence/Sequence.py` | séquençage Ableton (wait beats/ms/event) |
| Agent local (Rust :9010) | `src/agent/src/web/api.rs`, `action_catalog.rs`, `script_client.rs` | sert la SPA, proxie `/openapi.json`, route les keypress, registre d'extensions |
| SPA Vue3 | `src/frontend/src/` | hôte de la box de chat |
| Fakes LOM | `tests/domain/fixtures/` + `protocol0_stub/_Framework/` | « Ableton virtuel » embryonnaire pour la vérif |
| Wiki | `D:\dev\obsidian\dev\` | LOM Live 12 grep-able + notes SDK — grounding codegen |

**Constat** : tout le squelette (registre d'actions typées, OpenAPI, routing, fakes LOM,
canal d'extensions) est en place. Manquent (1) le **volume d'actions**, (2) le **cerveau LLM
+ la boucle de vérification**.

### Réutiliser vs construire

| | Réutiliser | Construire |
|---|---|---|
| Catalogue | `@action`, OpenAPI, Router | **beaucoup de nouvelles `@action`** (coverage LOM) |
| Async | `Sequence` | — |
| Vérif | fixtures LOM existantes | les faire muter l'état + property tests + suite conformité |
| Orchestration | — | sidecar Python + boucle tool-call + boucle codegen (raw SDK) |
| MCP | `/openapi.json`, proxy Rust | `FastMCP.from_openapi()` (~30 l., optionnel) |
| Chat | SPA Vue3, `api/client.ts` | panneau chat + flux « aperçu→raccourci→test » |
| Grounding | wiki (LOM grep-able), code | injection contexte / RAG léger |

## Découpage en jalons (indicatif)

- **J0** — Fondations catalogue → enfant [action-catalog](2026-06-13-action-catalog.md).
- **J1** — Sidecar + chat feature A → enfant [nl-chat-control](2026-06-13-nl-chat-control.md).
- **J2** — Serveur MCP (option/bonus) → enfant [nl-chat-control](2026-06-13-nl-chat-control.md).
- **J3** — Boucle de vérification (cœur dur) → enfant [smart-actions-codegen](2026-06-13-smart-actions-codegen.md).
- **J4** — Feature B niveau 1 (DSL composable) → enfant [smart-actions-codegen](2026-06-13-smart-actions-codegen.md).
- **J5** — Feature B niveau 2 (échappatoire Python brut) → enfant [smart-actions-codegen](2026-06-13-smart-actions-codegen.md).
- **J6** — (différé) Blockly comme vue éditable sur le DSL, si l'édition par non-codeurs devient un objectif.

## Pièges transverses (issus de la recherche)

- **Ne pas mettre le LLM dans le remote script** (stdlib-only, embedded Python) — sidecar séparé.
- **Ne pas adopter LangChain/LangGraph** pour du tool-calling borné (debug/abstraction/CVE).
- **Ne pas faire confiance à un test généré par le LLM seul** comme oracle (auto-illusion) —
  propriétés dérivées de l'intention + évaluateur distinct + confirmation humaine.
- **Ne pas viser une sandbox cloud** (e2b/Vercel/Firecracker) — contredit local-first.
- **Ne pas construire un vrai langage DSL** (interpréteur 4-chiffres de LoC) — DSL = composition
  sur les actions typées, transpilée déterministiquement.
- **Surévaluer le LLM, sous-évaluer le catalogue** : le facteur limitant est le **volume d'actions**.

## Vérification (comment on saura que ça marche)

- **Feature A** : prompts canoniques (« transpose +1 », « supprime les devices disabled ») →
  bons appels d'action, vérifiés dans un vrai set Ableton.
- **Feature B** : une smart action générée passe lint + propriétés + exécution fakes, est
  assignée à un raccourci, et **fait la bonne chose dans Ableton** ; le fallback Python affiche
  bien la notification « mode custom ».
- **Régression** : suite de conformité LOM (fakes ↔ vrai Ableton) verte au bump de version Live.
- **Garde-fou framework** : aucune dépendance lourde dans l'installeur ; sidecar à venv isolé.

## Sources

- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) ·
  [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) ·
  [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Pydantic AI — [Multi-agent applications](https://ai.pydantic.dev/multi-agent-applications/) ·
  [Testing](https://ai.pydantic.dev/testing/)
- LangChain — [Workflows vs agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) ·
  Octomind — [Why we no longer use LangChain](https://octomind.dev/blog/why-we-no-longer-use-langchain-for-building-our-ai-agents)
- MCP — [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp) · FastMCP [from_openapi](https://gofastmcp.com/integrations/openapi)
- Les sources spécifiques (codegen, vérif, DSL, catalogue) sont citées dans chaque enfant.
