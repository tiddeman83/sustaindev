# Revised Sprint Plan: Publishable v0.1 in Two Sprints

## Why This Revision Exists

The original `implementation_plan.md` defines 8 sprints before public launch. This contradicts the stated principle in `build_plan.md`: *"Publish early with a strong README"* and *"Keep the first public version small enough to understand in 10 minutes."*

This document collapses the path to v0.1 into **two focused sprints** that produce a publishable, useful, defensible repository. The remaining sprints from the original plan move to v0.2+ as a public roadmap, where they belong.

The optimization target for v0.1 is: **one developer copies one workflow and feels the token/cost savings within one hour.** Everything else is deferred.

---

## Cross-Cutting Decisions (Make Before Sprint 0 Starts)

These decisions block both sprints and must be made first. None of them require model time.

### License: Apache-2.0

Decide today. Apache-2.0 is preferred over MIT because:

- It includes an explicit patent grant, which matters when prompts and workflows could encode patentable methods.
- It's compatible with broad reuse, including commercial.
- It's the de facto standard for AI-adjacent open infrastructure (LangChain, vLLM, Ollama all use Apache-2.0).

Add `LICENSE` file at repo root. Update `contribution.md` Section "License" to remove the "not decided yet" caveat and add a standard Apache-2.0 contributor language.

### Reviewer Role: Tool-Neutral

Replace every single-model review mandate in `implementation_plan.md` with:

> Sprint review by a strong-reviewer pair: one capable reasoning model (Claude Opus, GPT-5, Gemini Pro, or equivalent) and one human. Either may be skipped if the other surfaces no blocking issues.

Rationale: locking the QA loop to one paid tier of one provider violates the tool-neutrality principle the system is teaching.

### Project Naming Sanitization

In all public docs, two private project names are replaced with `project-a` and `project-b`. The real-name mapping lives in a gitignored private file (`projects/.private-map.md`). Stack-specific identifying details (framework versions, distinctive technical specifics) also move to that private file.

A CI check (`.github/workflows/validate.yml` + `.github/forbidden-names.txt`) fails the build if any of the original names slip into a tracked file.

### Project Name Sanity Check

Before publishing, search GitHub, npm, PyPI, and Google for "SustainDev" / "sustaindev". If there's a high-traffic conflict (sustainability-focused dev events, existing tooling), pick a backup from the rejected alternatives. Current shortlist for backup: `LeanLoop`, `DurableLoop`, `ConserveDev`. A 10-minute check now prevents a rename later.

---

## Revised Sprint 0: Publishable Foundation

### Goal

Produce a public repository that explains itself, positions clearly against existing tools, and contains one fully worked artifact that proves the thesis. Nothing more.

### Owner

Solo: you (with model assistance as needed). No multi-agent coordination overhead at this stage — that itself burns tokens.

### Sprint Length

3–5 working days.

### Deliverables

**Repository hygiene (all at root):**

- `README.md` — see structure below
- `LICENSE` — Apache-2.0
- `.gitignore` — covers `.DS_Store`, `node_modules/`, `__pycache__/`, `.env`, `projects/.private-map.md`, local model output cache
- `CONTRIBUTING.md` — renamed from `contribution.md` (GitHub convention)
- `CODE_OF_CONDUCT.md` — renamed from `code_of_conduct.md` (GitHub convention)
- `build_plan.md` — keep, but resolve the publish-first vs craft-first contradiction
- `implementation_plan.md` — replace with this document plus a roadmap pointer

**Positioning and roadmap:**

- `docs/positioning.md` — *"How SustainDev differs from Cursor Rules, Cline rules, Aider conventions, Continue.dev, OpenHands, Claude Code commands"*. 1–2 paragraphs each. Be specific and fair to the alternatives.
- `docs/roadmap.md` — what's in v0.1, what's planned for v0.2, v0.3
- `docs/sustainability-defined.md` — short page defining what *sustainable* means here: token cost, $ cost, environmental footprint, accessibility for devs without paid budgets, longevity across model generations

**Issue templates:**

- `.github/ISSUE_TEMPLATE/skill_request.md`
- `.github/ISSUE_TEMPLATE/adapter_request.md`
- `.github/ISSUE_TEMPLATE/measurement_report.md` — new: invites users to share before/after token measurements

**Minimal CI from day one:**

- `.github/workflows/validate.yml` — runs on every PR:
  - Markdown link checker (e.g. `lycheeverse/lychee-action`)
  - Required-files check (LICENSE, README, CONTRIBUTING, CODE_OF_CONDUCT exist)
  - Skill schema check stub (will become useful in Sprint 1)

### README Structure (the most important file in v0.1)

The README must answer five questions in this order, in under 400 words total above the fold:

1. **What is this?** One sentence. *"A portable, tool-neutral layer for AI-assisted development that reduces token waste and protects code maintainability across Codex, Claude Code, LM Studio, and MCP-enabled tools."*
2. **Who is it for?** One sentence. *"Developers who use multiple AI coding tools daily and want to stop reinventing prompts and burning tokens on rediscovery."*
3. **What's the one workflow that proves it?** Link to the hero workflow built in Sprint 1.
4. **How does it differ from X, Y, Z?** Link to `docs/positioning.md`.
5. **Status and roadmap.** *"v0.1 is one workflow + the minimum core. v0.2 adds X, Y. See `docs/roadmap.md`."*

Below the fold: quickstart, file layout, contribution path.

### Acceptance Criteria

- A new visitor reads the top of the README in under one minute and understands the project.
- The license is set; contributors have clear rights.
- No private project names appear anywhere in the repo.
- Issue templates exist.
- CI runs on PRs.
- Positioning paragraph cites at least 4 existing alternatives by name.

### Explicitly Deferred from Original Sprint 0

- The full `core/` skeleton (moves to Sprint 1)
- Multi-model coordination ceremony (not needed yet)

---

## Revised Sprint 1: The Hero Workflow + Minimum Core

### Goal

Build *one* end-to-end workflow that a developer can copy and feel the savings from within an hour. Plus the minimum core scaffolding to support it. Then ship v0.1.0.

### Owner

Solo, with one local model (LM Studio) and one cloud model (Claude Code or Codex) as supporting tools, not as parallel collaborators.

### Sprint Length

5–8 working days.

### The Hero Workflow

**Name:** `idea-to-prepared-task`

**Story:** Developer has a vague idea ("add CSV export to the report screen"). Instead of dropping it into Claude Code immediately and burning 30k tokens on context discovery, they:

1. Run `scripts/schedule/capture-idea.sh "add csv export to report screen"` — saves to `core/scheduling/queue/captured/`
2. Run `scripts/schedule/prepare-task.sh <id>` — sends the idea + project codemap + verify rules to a **local** LM Studio model, which produces a structured task brief in `core/scheduling/queue/prework-ready/`
3. Open the prepared brief in Claude Code or Codex. The cloud model now starts with: clear scope, file targets, verify commands, maintainability constraints, success criteria. **No rediscovery.**
4. Cloud model implements. Human reviews diff against the prepared brief.

**What this proves:** Local model handles 80% of the context-gathering work for free. Cloud model only handles the irreducible reasoning + code change. This is the entire thesis in one workflow.

### Deliverables

**Minimum core (5 files, not 30):**

- `core/principles/development-principles.md` — the 15 principles from `build_plan.md` Section 5, condensed
- `core/rules/token-efficiency.md` — concrete rules: codemap before scan, narrow over broad, stop conditions
- `core/rules/maintainability.md` — condense the 12 maintainability dimensions to 6: architecture fit, coupling, naming, testability, error handling, change cost
- `core/rules/model-routing.md` — see "Concrete Routing Triggers" below
- `core/templates/codemap.md` and `core/templates/project-context.md`

**The hero workflow (the actual sprint deliverable):**

- `core/skills/idea-to-prepared-task/SKILL.md`
- `core/scheduling/templates/scheduled-task.md`
- `core/scheduling/queue/{captured,prework-ready,scheduled,completed}/.gitkeep`
- `scripts/schedule/capture-idea.sh`
- `scripts/schedule/prepare-task.sh` — calls LM Studio's OpenAI-compatible local API
- `scripts/schedule/list-queue.sh`
- `adapters/lm-studio/prework-prompt.md` — the prompt sent to the local model
- `adapters/lm-studio/usage.md` — setup: install LM Studio, recommended model (Qwen 2.5 Coder 14B or equivalent), enable local server

**Two adapters only:**

- `adapters/codex/AGENTS.md.template`
- `adapters/claude-code/CLAUDE.md.template`

Both adapters are thin: 30–80 lines each, referencing `core/` rather than duplicating it.

**Defer to v0.2:** Warp, Antigravity, VS Code adapters. Mark in roadmap as *experimental, contributions welcome*.

**Measurement baseline (the credibility deliverable):**

- `docs/measurement/methodology.md` — how to count tokens for a task, how to compare before/after
- `docs/measurement/case-study-01.md` — one worked example with real numbers: *"Task X done without prework cost N tokens / $Y. Same task with the hero workflow cost M tokens / $Z. Local model handled K tokens at $0."*

Without this, "sustainable" is a marketing claim. With it, you have evidence.

### Concrete Routing Triggers (replaces hand-waved "low risk vs high risk")

Add to `core/rules/model-routing.md`:

```text
Use the local model when ALL of these are true:
- Task is read-only or produces a draft artifact (not a code change)
- No secrets, auth, payment, or migration logic in scope
- Output will be reviewed by a human or stronger model before any commit
- Total input fits in the local model's context (typically <32k tokens)

Use the cloud model when ANY of these are true:
- Code change touches >3 files
- Code change touches auth, security, payment, migration, or production config
- Task requires multi-step planning across architectural boundaries
- Task is the final review gate before merge
- Local model produced a draft and you need verification

Always require human review when:
- Diff touches dependencies
- Diff touches infrastructure-as-code
- Diff touches anything matching the project's RISKS.md
```

These are objective triggers a script or a developer can apply in seconds.

### Acceptance Criteria

- A developer reading the README can run the hero workflow end-to-end on a sample task in under 60 minutes including LM Studio setup.
- The case study shows a measurable reduction in cloud tokens or cost on at least one real task.
- All five core files are under 200 lines each.
- Both adapters reference `core/` rather than duplicating content.
- CI passes.
- Issue templates accept measurement reports from the community.

### Then: Tag v0.1.0 and Publish

- Push to public GitHub.
- Add topics: `ai-development`, `developer-tools`, `local-llm`, `lm-studio`, `claude-code`, `codex`, `mcp`, `software-maintainability`, `token-efficiency`.
- Tag `v0.1.0`.
- Open 5 *good first issue* labels for the v0.2 backlog (Warp adapter, VS Code adapter, additional skills, more case studies, MCP policy expansion).
- Write a short launch post that *leads with the case-study numbers*, not with the architecture.

---

## What Moves to v0.2+ (the Public Roadmap)

These are not abandoned — they're sequenced after the public launch so the community can see them and contribute.

**v0.2 — Adapters expansion:**

- Warp adapter (terminal recipes)
- VS Code adapter (MCP config + tasks)
- Additional MCP policy templates

**v0.3 — More skills:**

- `repo-onboarding`, `feature-delivery`, `bug-investigation`, `maintainability-review`, `low-token-debugging`
- Each shipped only after at least one case study demonstrating its value

**v0.4 — Agents and commands:**

- The agent and command layer from original Sprint 3
- Defer until skills have shaken out — agents on top of unstable skills create churn

**v0.5 — Project adoption:**

- The sanitized project adapter examples
- Original Sprint 6 work, with `project-a` / `project-b` naming

**v0.6 — Antigravity adapter:**

- Wait for Antigravity's API/MCP surface to stabilize

**v0.7 — Validation and sync automation:**

- Original Sprint 7 work, beyond the minimal CI shipped in v0.1

This sequencing means the community sees a usable, opinionated v0.1 and can contribute to v0.2+ in parallel with you. The original 8-sprint-then-launch plan denies them that opportunity.

---

## Sprint Review Format (Replaces Original "Claude Opus Review")

At the end of each sprint, produce one short review document at `docs/reviews/sprint-XX-review.md` with this structure:

```text
Sprint XX review

Reviewer pair:
- Model: [Opus / GPT-5 / Gemini Pro / etc.]
- Human: [name]

Decision: pass / pass with fixes / fail

Alignment with build_plan.md:
Maintainability findings:
Token-efficiency findings:
Public usability findings:
Required fixes before next sprint:
Optional improvements:
```

Either reviewer may be skipped if the other surfaces no blocking issues. This avoids tool lock-in and reduces review-cycle token cost.

---

## Open Questions Resolved

From `implementation_plan.md` Section 17:

1. **License?** Apache-2.0. Decided.
2. **How to store reviews?** Markdown files in `docs/reviews/`. Decided.
3. **Branching for parallel work?** Not needed in v0.1 (solo). Reconsider for v0.2.
4. **Local model: documented or scripted in v0.1?** Both. The hero workflow needs the script to be credible.

## What Stays the Same

The architectural bet (core/adapters/projects), the local-model-as-first-class-tier idea, the maintainability-as-required-output principle, the queue lifecycle, the honesty about not pretending to know live model load — all of this carries through unchanged. This revision changes the *sequencing and scope* of the launch, not the design.

## Final Note

The revised plan asks you to do something uncomfortable: ship a deliberately small public version that's clearly labeled *v0.1 — early, with a roadmap*. The instinct to launch only when the cathedral is built is strong, but it's wrong for community projects. A small, honest, measurably useful v0.1 attracts contributors. A perfect-but-private v0.8 attracts nothing.

Ship the hero workflow with one case study. Let the community help you build the rest.
