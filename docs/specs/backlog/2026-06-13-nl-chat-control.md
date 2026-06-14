# Natural-language chat control (feature A)

> Parent : [2026-06-13-agentic-vision](2026-06-13-agentic-vision.md)
>
> **Dépendances** : [action-catalog](2026-06-13-action-catalog.md) — sans un catalogue
> conséquent, le chat n'a pas de valeur (l'UI + raccourcis suffisent déjà pour 2 actions).

## Context

Une **box de chat intégrée** où l'utilisateur contrôle Ableton en langage naturel — « transpose
le clip MIDI sélectionné d'un demi-ton », « supprime tous les devices disabled du set ». Le LLM
**mappe le NL vers les actions du catalogue** (`@action` via `/openapi.json`) et orchestre
plusieurs appels si besoin.

Exigence produit : **chat intégré clé en main**. La cible inclut des utilisateurs non familiers
de Claude Desktop / Cursor — on ne peut pas se reposer uniquement sur MCP + un client tiers.

## Décisions de design (issues de la recherche)

### Workflow, pas agent
NL → catalogue d'actions borné = un **workflow / tool-calling** (routing + tool use), pas une
boucle agentique autonome — même quand le catalogue atteint des centaines d'actions
(Anthropic, *Building Effective Agents* : workflows = chemins prédéfinis).

### Pas de framework lourd
Convergence forte (Anthropic, Pydantic AI, la doc *workflows-vs-agents* de LangChain
elle-même, Octomind) : **pas de LangChain/LangGraph** pour du tool-calling borné — couches
d'abstraction qui masquent les prompts, debug pénible, et surface AV/CVE supplémentaire dans un
**outil installé**. → **boucle tool-calling brute (quelques centaines de lignes)** derrière une
petite abstraction `Provider`. **Pydantic AI en réserve** comme *seule* dépendance à adopter si
on veut son I/O typé + son harnais de test (`TestModel`/`FunctionModel`) ; jamais LangGraph.

### Sidecar séparé, provider-agnostique
Le LLM **ne vit pas dans le remote script** (stdlib-only, embedded Python). C'est un **process
sidecar Python à venv propre**. Le `Provider` abstrait couvre Anthropic natif **et** les
endpoints OpenAI-compatibles → permet **Ollama / LM Studio** en local (BYO-key cloud *ou*
modèle local), ce qui colle au positionnement local-first OSS.

### MCP en socle/bonus, pas en remplacement
`ableton-mcp` prouve le pattern (remote script + serveur MCP séparé piloté par le client).
Protocol0 est en avance : `/openapi.json` existe déjà → **`FastMCP.from_openapi(spec, client)`**
génère un serveur MCP en ~30 lignes (sidecar Python, ou crate Rust dans l'agent sur le catalogue
fusionné). MCP = **export bonus** (Claude Desktop/Cursor gratuits) ; le chat de la SPA est *un
client MCP de plus* sur le même catalogue. Le serveur MCP reste **toujours un process séparé**
du remote script stdlib-only.

## Architecture

```
SPA Vue3 (panneau chat)  ──HTTP──►  Sidecar LLM (Python, venv)
                                      • Provider (Anthropic | OpenAI-compatible→Ollama)
                                      • boucle tool-calling brute
                                      • tools dérivés de /openapi.json
                                      • (option) serveur MCP from_openapi()
                                            │ POST /api/action/<plugin>/<method>
                                            ▼
                                      Remote script (catalogue @action étendu)
```

Tools générés depuis `/openapi.json` (déjà servi par le script, déjà proxyé par l'agent Rust :
`src/agent/src/action_catalog.rs`). Sur tool-call : valider les args, POSTer l'action, éventuel
tour de suite pour les requêtes multi-actions.

## Jalons

- **J1 — Sidecar + chat.** Process Python (venv), `Provider` (Anthropic + Ollama), boucle
  tool-calling sur le catalogue, panneau chat dans la SPA (`src/frontend/src/`, réutilise
  `api/client.ts`). NL → actions existantes.
- **J2 — Serveur MCP (option/bonus).** `FastMCP.from_openapi()` sur le catalogue → clients MCP
  tiers gratuits. Décorrélé du chat ; peut être livré indépendamment.

## Composants

| Réutiliser | Construire |
|---|---|
| `/openapi.json`, proxy Rust (`action_catalog.rs`) | sidecar Python + boucle tool-call (raw SDK) |
| SPA Vue3, `api/client.ts` | panneau chat |
| catalogue `@action` (enfant action-catalog) | `Provider` (Anthropic + OpenAI-compatible) |
| — | (option) `FastMCP.from_openapi()` (~30 l.) |

## Pièges

- **LLM hors du remote script** (stdlib-only) — sidecar séparé obligatoire.
- **Pas de LangChain/LangGraph** — boucle brute suffit pour du tool-calling borné.
- **MCP seul ≠ produit** pour la cible non-experte — le chat intégré est requis.

## Vérification

Jeu de prompts canoniques (« transpose +1 », « supprime les devices disabled ») → bons appels
d'action, vérifiés dans un vrai set Ableton. Garde-fou : aucune dépendance lourde n'entre dans
l'installeur ; le sidecar reste un petit process à venv isolé.

## Sources

- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- Pydantic AI — [Multi-agent applications](https://ai.pydantic.dev/multi-agent-applications/) ·
  [Testing](https://ai.pydantic.dev/testing/)
- LangChain — [Workflows vs agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) ·
  Octomind — [Why we no longer use LangChain](https://octomind.dev/blog/why-we-no-longer-use-langchain-for-building-our-ai-agents)
- MCP — [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp) ·
  [jpoindexter/ableton-mcp](https://github.com/jpoindexter/ableton-mcp) (provider-agnostique) ·
  FastMCP [from_openapi](https://gofastmcp.com/integrations/openapi)
