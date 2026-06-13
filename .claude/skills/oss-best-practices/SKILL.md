---
name: oss-best-practices
description: Research how to do something well in an open-source project by combining your own knowledge with evidence from real, comparable OSS repositories on GitHub. Use when the user asks to "find OSS best practices on X", "trouve les best practices open source sur ce sujet", "comment font les autres projets open source pour Y", or wants a topic studied against reference repos (Syncthing, Transmission, Grafana, audio/DAW tooling, etc.) or authoritative LLM-engineering sources (Anthropic, OpenAI, Pydantic AI, LangChain, Mistral) before making a decision.
---

# OSS best practices research

Study a topic against how comparable open-source projects actually do it, then give
Protocol0 a concrete, opinionated recommendation. The point is **evidence, not vibes**:
every claim should be backed either by your reasoning or by a real repo you looked at.

## What Protocol0 is (so you pick relevant references)

Protocol0 is a companion/extension for Ableton Live:
- a **detector** (local background process) owns a global keyboard hook,
- a **remote script** runs inside Ableton, exposes a **local HTTP API on :9000**, and
  **serves a self-hosted config web UI**,
- config is JSON on disk, shared between the two surfaces,
- **cross-platform target is Windows + macOS only** (no Linux), shipped as a desktop
  installer with autostart.

So the closest references share these traits: a **daemon/background service that serves a
local self-hosted web UI**, ideally also a **plugin/extension of a host app** (audio or
graphics), ideally in the **music/audio** domain, and ideally **cross-platform desktop**
(not server/Linux-only). Weight references by how many of these they share.

## Workflow

1. **Frame the topic.** Restate what's being studied in one sentence and pin it to a
   Protocol0 decision (e.g. "how to auto-update a self-hosted desktop daemon"). If the
   topic is vague, ask one clarifying question, then proceed.

2. **Think first, from your own knowledge.** Before touching GitHub, write down what you
   already know: the common approaches, their trade-offs, and a tentative recommendation.
   This is the baseline the repo evidence will confirm or correct.

3. **Pick references.** Choose 3-6 sources that genuinely match Protocol0 on the
   traits above — not just any popular OSS. Two reference files:
   - [references/reference-projects.md](references/reference-projects.md) — OSS repos
     (show *how it's coded*).
   - [references/authoritative-sources.md](references/authoritative-sources.md) — vendor
     engineering blogs, official docs, recognized practitioners (show *what the right
     pattern is*). For **LLM pattern/architecture topics** (code generation, agents vs
     workflows, sandboxed execution, LLM-as-judge, evals, structured output, prompting,
     cost), consult this FIRST — the big players' guidance outweighs user repos there.

   Then add topic-specific ones via `WebSearch`. Prefer sources that *actually solved the
   exact problem* over merely famous ones. State why each was chosen (which traits it shares).

4. **Go look — don't guess.** For each reference, get real evidence:
   - `WebSearch` for "<project> <topic>" to find the relevant code/docs/discussions,
   - `WebFetch` the actual source file, README section, docs page, or issue/ADR. Quote or
     cite the specific file/section — a path or URL, not "I believe Syncthing does X".
   - If the question is deep or spans several repos, fan out with **subagents** (see below)
     so each repo is investigated in parallel and independently.

5. **Compare and decide.** Synthesize into:
   - a short **comparison** (what each reference does for this topic, in a table when it helps),
   - **convergence** (what most good projects agree on — usually the safe default),
   - **divergence** (where they differ and why — usually driven by a trait Protocol0 may or
     may not share),
   - a **recommendation for Protocol0** that respects its constraints (Windows+macOS desktop,
     local HTTP, stdlib-only remote script, OSS-friendly), with the rejected alternatives named.

6. **Cite sources.** End with a `Sources:` list of every repo file / docs page / issue you
   actually used, as markdown links. No uncited claims about what a project does.

## Depth: solo vs. subagents

- **Shallow** (one focused question, 1-3 references): do it inline. Think, fetch a few
  sources, recommend.
- **Deep** (broad topic, comparison across many repos, or "be thorough"): use the `Agent`
  tool to fan out — **one subagent per reference repo** (or per sub-question), each tasked to
  return structured findings (approach, key files/links, trade-offs, applicability to a
  Windows+macOS local-HTTP daemon). Then you synthesize. This keeps each repo's investigation
  isolated and lets them run in parallel. Give each subagent the Protocol0 trait list so it
  judges applicability, and tell it to cite real files/URLs.

  If the user explicitly opted into heavy multi-agent orchestration ("use a workflow",
  "ultracode"), a `Workflow` (pipeline: per-repo investigate -> verify -> synthesize) is the
  scaled-up version of the same shape. Default to plain `Agent` subagents otherwise.

## Guardrails

- **Match Protocol0, not popularity.** A 40k-star Linux-only server daemon is a weaker
  reference than a 2k-star cross-platform desktop tray app that serves a local web UI.
  Exception: the vendor guides in `authoritative-sources.md` (Anthropic, OpenAI, Pydantic
  AI, LangChain, Mistral) are admissible even outside the desktop/audio domain — they
  distill thousands of production deployments. Cite them for the *LLM pattern*, not the domain.
- **Windows+macOS only.** Discount Linux-/server-specific patterns (systemd units, Docker
  Compose deploys, reverse-proxy assumptions) unless they translate to desktop.
- **Don't invent repo behavior.** If you can't find/verify how a project does something, say
  so rather than guessing. Unverified is fine to mention — just label it.
- **Respect Protocol0's spec workflow.** If the research is meant to feed a feature, point at
  `docs/specs/` rather than starting to implement.
