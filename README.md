# SustainDev

> A portable, tool-neutral layer for AI-assisted development that reduces token waste and protects code maintainability across Codex, Claude Code, LM Studio, and MCP-enabled tools.

**Status: v0.1 — early. The hero workflow ships first; the rest follows on a public roadmap.**

---

## What Is This?

SustainDev is a small, opinionated repository of reusable rules, skills, and adapters for AI-assisted software development. It separates **durable knowledge** (in `core/`) from **tool-specific glue** (in `adapters/`) so the same workflow is usable from Codex, Claude Code, LM Studio, Warp, Antigravity, VS Code, and MCP-enabled tools without duplicated prompts.

It also takes a position most prompt repositories avoid: **local models are a first-class execution tier for low-risk prework.** The cheaper your context preparation, the less you spend on cloud reasoning, and the longer the strong models stay accessible to everyone.

## Who Is It For?

Developers who use multiple AI coding tools daily and want to stop reinventing prompts, burning tokens on rediscovery, and producing code that gets harder to maintain with every AI session.

If you've ever pasted the same project context into three different tools in one week, this is for you.

## The Hero Workflow

The first usable workflow ships in v0.1: **`idea-to-prepared-task`**.

1. Capture an idea in seconds — `scripts/schedule/capture-idea.sh "add csv export to report screen"`
2. A **local model** (LM Studio) drafts a structured task brief with file targets, verify commands, and maintainability constraints — for free.
3. The cloud model (Codex / Claude Code) starts work with full context already prepared. No rediscovery, no 30k-token warmup.
4. Human reviews diff against the prepared brief.

Local model handles ~80% of context-gathering. Cloud model only handles the irreducible reasoning + code change. See [`docs/measurement/case-study-01.md`](docs/measurement/case-study-01.md) for real before/after numbers (shipping in Sprint 1).

## How This Differs From Cursor Rules, Cline, Aider, Continue.dev, OpenHands, Claude Code

Most existing prompt/rules ecosystems are **tool-bound** — they live inside one editor or one CLI. SustainDev is the **cross-tool layer above them**, plus three things they don't ship:

- **Explicit local-model prework tier** with objective routing rules.
- **Maintainability as a required output** of every workflow.
- **A measurement methodology** so "sustainable" is evidence, not vibes.

See [`docs/positioning.md`](docs/positioning.md) for a fair, specific comparison.

## Quickstart

**Start here:** [`docs/adoption/getting-started.md`](docs/adoption/getting-started.md) — your first 30 minutes from clone to first probe output.

For background before you start: [`docs/measurement/v0.1.x-lessons.md`](docs/measurement/v0.1.x-lessons.md) — what we learned in 7 case studies, summarized.

Common questions: [`docs/adoption/faq.md`](docs/adoption/faq.md).

Bare-minimum incantation:

```bash
git clone https://github.com/<username>/sustaindev.git
cd sustaindev

# Read the philosophy
cat core/principles/development-principles.md
cat core/rules/token-efficiency.md

# Try a probe on your own project (after LM Studio setup — see getting-started.md)
cd /path/to/your/project
python3 ~/sustaindev/scripts/sprint1/triage-files.py
```

Full LM Studio setup is in [`adapters/lm-studio/usage.md`](adapters/lm-studio/usage.md). The getting-started doc walks you through everything in order.

## Repository Layout

```text
sustaindev/
  core/         durable, tool-neutral knowledge (rules, skills, agents, templates)
  adapters/     thin per-tool integration (codex, claude-code, lm-studio, ...)
  projects/     sanitized examples of project-level adoption
  scripts/      shell/python helpers for capture, prepare, list, validate
  docs/         positioning, roadmap, measurement, decisions, reviews
```

Where a change lives matters more than how big it is. Tool-specific work goes in `adapters/`. Project-specific work goes in `projects/`. Reusable work goes in `core/`. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## What Sustainable Means Here

Token cost. Dollar cost. Environmental footprint. Accessibility for developers without paid API budgets or reliable internet. Longevity across model generations. See [`docs/sustainability-defined.md`](docs/sustainability-defined.md).

## Status

**v0.1.x line: complete.** Nine tagged releases (v0.1.0 → v0.1.8), seven measurement case studies, six of ten matrix rows empirically backed. Two unconditional strong-fit rows, three conditional, one weak. Probe scripts ship with shared post-processing utilities. Adopter walkthrough + FAQ at [`docs/adoption/`](docs/adoption/) and synthesis at [`docs/measurement/v0.1.x-lessons.md`](docs/measurement/v0.1.x-lessons.md) are the entry-point reads.

**v0.2.0-beta** — second v0.2-line release. Two adapters now ship:

- [`adapters/warp/`](adapters/warp/) — four Warp Workflows (capture-idea, list-queue, prepare-task, triage-files) one keypress away via Cmd+Shift+R. Install: `./adapters/warp/install.sh`.
- [`adapters/vscode/`](adapters/vscode/) — six VS Code Tasks covering all SustainDev probes (capture-idea, list-queue, prepare-task, triage-files, draft-catalog, extract-risks). Cmd+Shift+P → Tasks: Run Task. Install: `~/sustaindev/adapters/vscode/install.sh` from your project root. Cursor and Cline both read tasks.json so this adapter works for them too.

- v0.2 — Cursor / Cline rules export adapters; remaining four matrix rows; test suite for `scripts/lib/postprocess.py`.
- v0.3+ — agents, commands, project adoption examples, Antigravity adapter.

Public roadmap: [`docs/roadmap.md`](docs/roadmap.md).

## Contributing

Open an issue first. Keep the first change small. Documentation belongs alongside the change. See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

We especially welcome **measurement reports** — real before/after numbers from your own projects. Use [`.github/ISSUE_TEMPLATE/measurement_report.md`](.github/ISSUE_TEMPLATE/measurement_report.md).

## License

[Apache License 2.0](LICENSE). Use it, fork it, ship it.

## Strategic Documents

- [`build_plan.md`](build_plan.md) — long-term strategic plan
- [`revised_sprints_v0.1.md`](revised_sprints_v0.1.md) — current execution plan (replaces the original `implementation_plan.md`)
