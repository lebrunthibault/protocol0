# Authoritative sources on LLM engineering patterns

Vendor engineering blogs, official docs and recognized practitioners. For **pattern and
architecture topics** (agents vs workflows, code generation, LLM-as-judge, evals, structured
output, prompting, tool use, sandboxed execution, cost), these carry MORE weight than user
repos — they distill thousands of production deployments. Use them alongside
`reference-projects.md` (repos show *how it's coded*, these sources show *what the right
pattern is*). All URLs verified 2026-06-13.

Note for Protocol0: unlike a fixed classification pipeline, a code-generation feature
(generate → test/execute in a sandbox → fix → retry) is a genuinely *agentic* loop — the
evaluator-optimizer and agent patterns below are warranted here, not over-engineering.

## Anthropic

Engineering blog index: `https://www.anthropic.com/engineering`

- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
  — THE foundational text: the 5 workflow patterns (chaining, routing, parallelization,
  orchestrator-workers, evaluator-optimizer) vs agents, and when an autonomous agent loop is
  warranted vs a fixed workflow.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
  — production multi-agent lessons; the 15× token figure; when parallel sub-agents pay off.
- [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices)
  — agentic coding patterns: how an LLM works effectively against a real codebase (most
  directly relevant to a code-generation feature).
- [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
  — running model-generated code through tools/sandboxes (the validation step of a code-gen loop).
- [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
  and [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)
  — tool/schema design and advanced tool-calling (e.g. a "run this in the sandbox" tool).
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  — what to put in context (codebase excerpts, references, docs) and how to structure it.
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
  — designing eval suites; automated vs human grading.
- [Claude cookbook](https://www.anthropic.com/cookbook) (repo:
  [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks)) — runnable
  notebooks; most relevant: agent patterns (`agent-patterns-evaluator-optimizer` = the
  generate→critique→fix loop, `agent-patterns-context-engineering`), tool use, building evals
  (`misc-building-evals`), prompt caching, the Claude Agent SDK tutorials.
- Docs (canonical host `platform.claude.com/docs`):
  [prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) ·
  [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) ·
  [tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) ·
  [define success criteria / evals](https://platform.claude.com/docs/en/test-and-evaluate/define-success)

## Pydantic (strong reference for building agents in Python, with typed I/O + evals)

- [Case studies](https://pydantic.dev/case-studies) — production Pydantic AI deployments
  (agentic RAG, agent evaluation platforms, AI security).
- [Multi-agent applications](https://pydantic.dev/docs/ai/guides/multi-agent-applications/)
  — the complexity ladder: single agent → delegation → programmatic hand-off → graphs;
  their own advice is plain code first.
- [Graphs](https://pydantic.dev/docs/ai/graph/graph/) — for multi-state loops, with their
  caution: "if you're not confident a graph-based approach is a good idea, it might be unnecessary".
- [Pydantic Evals](https://pydantic.dev/docs/ai/evals/evals/) — code-first eval framework
  (datasets, cases, evaluators, LLM judges) — fits "did the generated action behave correctly".
- [Testing agents](https://pydantic.dev/docs/ai/guides/testing/) — TestModel/FunctionModel
  to unit-test LLM code without API calls.
- [Structured output](https://pydantic.dev/docs/ai/core-concepts/output/) — output modes
  (tool/native/prompted), validators, streaming — useful to force generated code into a
  typed, validatable shape.

## LangChain

- [langchain-ai/langchain](https://github.com/langchain-ai/langchain) — the ecosystem repo.
- [Workflows vs agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
  — the canonical framing of the deterministic-vs-agentic decision.
- [How to build a custom agent harness](https://www.langchain.com/blog/how-to-build-a-custom-agent-harness)
  — agent = model + harness; middleware for context delivery and tool lifecycle.
- [Fault tolerance in LangGraph](https://www.langchain.com/blog/fault-tolerance-in-langgraph)
  — retry/timeout/error-handler primitives (a code-gen loop needs these around sandbox runs).
- [Introducing Rubrics](https://www.langchain.com/blog/introducing-rubrics-for-deepagents)
  — grader sub-agent reviewing outputs against criteria (LLM-as-judge applied to agent output).

## OpenAI

- [A practical guide to building agents (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
  — orchestration patterns, model selection, guardrails, from customer deployments.
- [Cookbook](https://developers.openai.com/cookbook) — topics: agents, evals, guardrails,
  optimization. See [Agent improvement loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)
  (traces + evals + code) — the generate/measure/improve cycle for an agent.
- [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
  — designing evals for production model behavior.

## Mistral

- [Structured output](https://docs.mistral.ai/capabilities/structured_output/) — custom
  structured outputs vs JSON mode.
- [Evaluation cookbook](https://docs.mistral.ai/resources/cookbooks/mistral-evaluation-evaluation)
  — metrics-based, code-based, and LLM-as-judge evaluation with rubric scoring.
- [Prompting best practices](https://docs.mistral.ai/models/best-practices) and
  [mistralai/cookbook](https://github.com/mistralai/cookbook).

## Recognized practitioners (evals & LLM-as-judge especially)

- Hamel Husain — [Creating a LLM-as-a-Judge that drives business results](https://hamel.dev/blog/posts/llm-judge/)
  (the 7-step judge framework) and [Your AI product needs evals](https://hamel.dev/blog/posts/evals/)
  (the 3-level eval strategy).
- Eugene Yan — [Patterns for building LLM systems](https://eugeneyan.com/writing/llm-patterns/),
  [Eval process](https://eugeneyan.com/writing/eval-process/) ("evals are the scientific
  method in disguise"), [Product evals in three steps](https://eugeneyan.com/writing/product-evals/).
- Lilian Weng — [LLM-powered autonomous agents](https://lilianweng.github.io/posts/2023-06-23-agent/)
  — the reference taxonomy (planning, memory, tool use).
- Chip Huyen — [Building LLM applications for production](https://huyenchip.com/2023/04/11/llm-engineering.html)
  and [Common AI engineering pitfalls](https://huyenchip.com/2025/01/16/ai-engineering-pitfalls.html)
  (incl. over-relying on AI-as-judge, premature complexity).
- Braintrust — [The six generations of AI agents and how to eval them](https://www.braintrust.dev/blog/six-generations-ai-agents/),
  [Evals are the new PRD](https://www.braintrust.dev/blog/evals-are-the-new-prd/),
  [Golden datasets with human review](https://www.braintrust.dev/blog/human-review-golden-datasets/).

## How to choose for a given topic

| Topic | Lean on |
|---|---|
| Code generation against a codebase | Anthropic Claude Code best practices, context engineering, Claude cookbook (agent SDK) |
| Generate → test/execute → fix loop | Anthropic Building Effective Agents (evaluator-optimizer), code-execution-with-mcp, OpenAI agent improvement loop |
| Sandboxed / safe code execution | Anthropic code-execution-with-mcp, advanced tool use, LangGraph fault tolerance |
| Agent vs workflow (per feature) | Anthropic Building Effective Agents, LangGraph workflows-vs-agents, Pydantic multi-agent |
| Feeding codebase + docs (Obsidian wiki) into context | Anthropic context engineering, Claude cookbook RAG |
| Structured / validatable generated output | Pydantic AI output docs, Mistral structured output |
| Tool / function design | Anthropic writing-tools-for-agents, advanced tool use |
| Evals & regression on generated actions | Pydantic Evals, Hamel evals, Eugene Yan eval-process, Braintrust golden datasets |
| LLM-as-judge / rubric grading | Hamel judge post, Anthropic demystifying-evals, LangChain Rubrics, Mistral evaluation cookbook |
| Prompt & context engineering | Anthropic context-engineering + prompt docs, Eugene Yan patterns |
| Cost / latency / caching | Anthropic prompt caching docs, multi-agent post (token economics) |
| Production reliability / fault tolerance | LangChain fault-tolerance, Chip Huyen pitfalls |

Note: the Langfuse blog was checked and is not fetchable (404s) — use the Langfuse repo and
its in-repo docs instead.
