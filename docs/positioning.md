# Positioning: How SustainDev Differs

SustainDev is not the only project trying to make AI-assisted development saner. Several mature ecosystems already exist for prompt rules, agent workflows, and tool-specific configurations. This document is an honest, specific comparison so you can decide whether SustainDev is for you.

## TL;DR

Most existing systems are **tool-bound** — they live inside one editor or one CLI. SustainDev is the **cross-tool layer above them**, plus three things that are rare elsewhere:

1. An explicit **local-model prework tier** with objective routing rules.
2. **Maintainability as a required output** of every workflow.
3. A **measurement methodology** so "sustainable" is evidence, not aspiration.

If you only use one AI coding tool and you're happy with it, you may not need SustainDev. If you bounce between Codex, Claude Code, your IDE's assistant, and occasionally a local model — and you're tired of redoing the same context every time — keep reading.

## Comparison

### Cursor Rules (`.cursorrules`, `.cursor/rules/`)

**What it is:** Per-repo rules files that Cursor's editor reads and prepends to prompts. Strong ecosystem, well-known format.

**What it does well:** Project-specific guidance, narrow and effective inside Cursor. Excellent for "always use TypeScript strict mode" or "prefer Tailwind over inline styles."

**Where it leaves a gap:** Rules don't move when the developer moves. If you also use Claude Code, Codex, Aider, or Cline on the same repo, you re-author the rules — or accept divergence.

**SustainDev's relationship:** Complementary. SustainDev's `core/` rules can be exported into a Cursor rules file via an adapter (planned for v0.2). The durable rules live once; tool-specific exports stay thin.

### Cline rules (`.clinerules`)

**What it is:** Cline's per-repo rule file, similar concept to Cursor rules.

**What it does well:** Tightly integrated into Cline's autonomous-agent loop. Good for constraining what an agent can do.

**Where it leaves a gap:** Same tool-binding problem as Cursor rules. Cline-specific syntax doesn't transfer.

**SustainDev's relationship:** A Cline adapter is on the roadmap. The shared rules in `core/rules/` apply; the adapter handles the syntax.

### Aider conventions (`CONVENTIONS.md`)

**What it is:** Aider's pattern of pointing the CLI at a `CONVENTIONS.md` file describing project rules and architectural decisions.

**What it does well:** Very simple, very portable. The convention is "just write a markdown file."

**Where it leaves a gap:** Aider doesn't prescribe structure for the file, doesn't ship reusable templates, and doesn't address scheduling, local-model prework, or measurement. It's a convention, not a system.

**SustainDev's relationship:** SustainDev's `core/templates/project-context.md` is essentially a richer, more structured `CONVENTIONS.md` that also feeds Codex, Claude Code, and LM Studio. If you already use Aider conventions, you can adopt SustainDev incrementally — start with the project-context template.

### Continue.dev

**What it is:** An open-source IDE assistant with config-driven prompts, slash commands, and context providers. Strong customization model.

**What it does well:** Excellent extension surface. Strong context providers (codebase, docs, terminal, etc.). Local model support is first-class via Ollama and others.

**Where it leaves a gap:** The config lives inside Continue's extension. If your team uses Continue + Codex + Cursor in mixed environments, the prompts, commands, and context providers are not shared.

**SustainDev's relationship:** Continue's local-model orientation is the closest in spirit to SustainDev's. The difference: Continue is an editor extension; SustainDev is a portable knowledge layer that an extension (Continue, Cursor, Claude Code) can consume.

### OpenHands (formerly OpenDevin)

**What it is:** An open-source autonomous coding agent platform. Runs full agent loops, not just prompts.

**What it does well:** Full execution, sandboxed environments, multi-agent coordination. A genuine alternative to closed agent products.

**Where it leaves a gap:** Different problem domain. OpenHands is *the agent runtime*; SustainDev is *the durable knowledge an agent should consume regardless of runtime*. They're complementary, not competing.

**SustainDev's relationship:** OpenHands could read SustainDev's `core/` content as agent context. An adapter is plausible for v0.3+.

### Claude Code commands and agents

**What it is:** Anthropic's CLI ships with slash commands, sub-agents, hooks, and skills. Increasingly powerful primitives.

**What it does well:** Tight integration with Claude. Strong primitives for delegation and skill packaging.

**Where it leaves a gap:** Claude-bound by design. If you also use OpenAI Codex or Gemini Code, the slash commands and agents don't transfer.

**SustainDev's relationship:** SustainDev's `adapters/claude-code/` exposes the shared `core/` content as Claude Code commands and agents. Same workflow, exposed natively. If you only use Claude Code, you may prefer to use Anthropic's primitives directly — that's a fair choice.

### Codex `AGENTS.md`

**What it is:** OpenAI Codex's convention for a project-level instruction file the agent reads.

**What it does well:** Simple, similar to Aider's `CONVENTIONS.md`. Readable for humans.

**Where it leaves a gap:** Same single-tool binding. Doesn't structure scheduling or local-model use.

**SustainDev's relationship:** `adapters/codex/AGENTS.md.template` generates a Codex-compatible file from `core/`.

## Where SustainDev Is Genuinely Different

These are three things you won't find in the systems above, in this combination:

### 1. Local-model prework as a routing decision

Most systems either ignore local models or treat them as a swap-in for cloud models on the same task. SustainDev treats them as a **different tier with different responsibilities**: local for context preparation (codemaps, idea triage, documentation drafts, classification), cloud for code change and final reasoning, with explicit triggers for when to escalate. See [`core/rules/model-routing.md`](../core/rules/model-routing.md) (shipping in Sprint 1).

### 2. Maintainability as a required output

Most prompt systems optimize for "the AI did the task." SustainDev requires every code-changing workflow to also produce a maintainability impact note — coupling, naming, testability, change cost. The point is to stop accumulating AI-generated entropy.

### 3. Measurement methodology

Most "save tokens" claims are not backed by numbers. SustainDev ships a methodology and a worked case study with real before/after measurements (shipping in Sprint 1). Contributors are invited to submit their own measurement reports.

## When SustainDev Is *Not* The Right Choice

- You only use one AI tool and you're happy with its native rule format.
- You prefer fully autonomous agent runtimes (use OpenHands or commercial alternatives instead).
- You want an editor extension (use Continue.dev, Cursor, or Claude Code natively).
- You don't care about portability between tools.

## When SustainDev *Is* The Right Choice

- You use multiple AI coding tools daily.
- You've felt the pain of re-pasting the same project context into three tools.
- You want to use a local model for prework but haven't found a clean pattern.
- You care about maintainability of the codebase the AI is editing.
- You want evidence, not slogans, that a workflow saves tokens.

## Honest Limitations

- SustainDev is v0.1. The hero workflow ships first; the rest is on the public roadmap.
- It's opinionated about a small number of things, not exhaustive about everything.
- Some adapters (Antigravity, Warp) are deferred until those ecosystems stabilize.
- Local-model quality varies by hardware and model choice. Recommendations are documented, but your mileage may vary.
