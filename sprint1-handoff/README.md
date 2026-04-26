# Sprint 1 Handoff Package

This folder coordinates Sprint 1 implementation across three AI tools: **Claude Code**, **Codex**, and **Antigravity** (Gemini-powered). The Cowork session that prepared this package will be used only for review and integration going forward.

The package is itself a real-world test of SustainDev's tool-neutrality thesis: the same v0.1 release is being built by three different AI providers contributing to the same repository. If the architecture works, the deliverables will integrate cleanly with no rewriting; if it doesn't, we'll learn exactly where the friction is.

## Coordination Model

**Pre-divided work.** Each tool has a dedicated brief at `sprint1-handoff/brief-<tool>.md` listing the files it owns, with full task constraints. Tools do not pick from a shared pool; each task has exactly one owner.

**No cross-tool dependencies inside the sprint.** The briefs are sequenced so each tool can complete its files independently. Where one tool's output is referenced by another's, the reference uses a relative repo path that will be valid after both are committed; no tool needs to wait for another to finish.

**Single review surface.** All work returns to this Cowork session for review. The reviewer checks each file against `review-criteria.md` and either accepts it, requests changes (recorded as comments on the PR or as inline edits), or rewrites it. Cowork is not authoring v0.1 deliverables; it is the integration and quality gate.

## Ownership Table

| File | Owner | Why this tool |
|------|-------|---------------|
| `adapters/claude-code/CLAUDE.md.template` | Claude Code | Authors its own adapter — best knowledge of Anthropic's CLAUDE.md conventions. |
| `core/skills/idea-to-prepared-task/SKILL.md` | Claude Code | Knows the Anthropic SKILL.md format from native skill ecosystem. |
| `core/rules/maintainability.md` | Claude Code | Strong at code-review-shaped reasoning; consistent with how Claude Code thinks about diffs. |
| `core/templates/project-context.md` | Claude Code | The template feeds into Claude Code's CLAUDE.md.template; same author keeps voice aligned. |
| `adapters/codex/AGENTS.md.template` | Codex | Authors its own adapter — best knowledge of OpenAI Codex's AGENTS.md conventions. |
| `core/templates/codemap.md` | Codex | Strong at code-structure analysis and structured templates. |
| `core/scheduling/templates/scheduled-task.md` | Codex | Template-shaped output; pairs naturally with the shell scripts also owned by Codex. |
| `core/scheduling/queue/{captured,prework-ready,scheduled,completed}/.gitkeep` | Codex | Trivial; bundled with the scheduling task set. |
| `scripts/schedule/capture-idea.sh` | Codex | Shell scripting strength. |
| `scripts/schedule/list-queue.sh` | Codex | Shell scripting strength. |
| `core/principles/development-principles.md` | Antigravity (Gemini) | Broad analytical synthesis; condenses 15 build-plan principles into a tight rule sheet. |
| `core/rules/model-routing.md` | Antigravity (Gemini) | Strong-fit/weak-fit matrix grounded in case-study-01 data; analytical reasoning task. |
| `adapters/lm-studio/usage.md` | Antigravity (Gemini) | User-facing setup guide; pairs with the routing rules above. |
| `adapters/lm-studio/prework-prompt.md` | Antigravity (Gemini) | Prompt engineering for the prework tier; benefits from Gemini's long-context reasoning. |
| `docs/measurement/methodology.md` | Antigravity (Gemini) | Statistical hygiene for measurement protocol. |
| `docs/measurement/case-study-01.md` | Antigravity (Gemini) | Writes the case-study prose around `case-study-01-data.md`. |

## What's Already Done (Cowork-Authored)

These files exist in the repo and serve as **style anchors** for the new work. New files should match their tone and structure conventions.

- `core/rules/token-efficiency.md` — primary style anchor. Match its prose density and section shape.
- `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE` — repository foundation.
- `build_plan.md`, `revised_sprints_v0.1.md` — strategic source of truth.
- `docs/positioning.md`, `docs/roadmap.md`, `docs/sustainability-defined.md` — public-facing framing.
- `scripts/sprint1/` — the test run that produced the data behind case-study-01.

## Branching Convention

Each tool works on its own branch off `main`:

```text
main
  ├── sprint1/claude-code     # Claude Code's deliverables
  ├── sprint1/codex           # Codex's deliverables
  └── sprint1/antigravity     # Antigravity's deliverables
```

When a tool finishes its brief, it opens a PR against `main`. The Cowork reviewer integrates merges in this order to minimize conflict:

1. `sprint1/claude-code` — adds `CLAUDE.md.template`, hero SKILL, maintainability rule, project-context template.
2. `sprint1/codex` — adds `AGENTS.md.template`, codemap template, scheduling templates and scripts.
3. `sprint1/antigravity` — adds principles, model-routing, LM Studio docs, measurement docs.

If a PR fails CI (`.github/workflows/validate.yml`), the owning tool fixes its branch and re-pushes. The reviewer does not silently fix CI failures.

## Review Flow

For each PR:

1. CI must pass. No human review until CI is green.
2. Reviewer reads each new file against `review-criteria.md`. Pass / fix / rewrite.
3. Fixes preferred to rewrites; rewrites only when the file fundamentally misses the brief.
4. Decisions are recorded as PR comments. The conversation history is the audit trail.
5. On accept, merge with squash so each tool has one clean commit on `main`.

## Definition of Done for Sprint 1

All sixteen files in the ownership table exist on `main` and pass CI. `core/rules/token-efficiency.md` (already merged) is unchanged. The repository is ready for the v0.1.0 tag.

A short sprint review document is written by the Cowork reviewer at `docs/reviews/sprint-01-review.md` covering: which tool owned which file, where each tool excelled, where each tool struggled, and what this means for v0.2 ownership choices.

## How to Start

Each tool's user opens that tool, points it at the repo root, and pastes or references the corresponding brief:

```text
Claude Code: open repo, read sprint1-handoff/brief-claude-code.md, complete tasks in order.
Codex:       cd into repo, read sprint1-handoff/brief-codex.md, complete tasks in order.
Antigravity: open repo workspace, read sprint1-handoff/brief-antigravity.md, complete tasks in order.
```

Each brief is **self-contained**: required reading, system prompt, target structure, word count, acceptance criteria are all inline. A tool should be able to complete its work without asking clarifying questions, though Cowork is available for blocking ambiguities.

## Risks and Tradeoffs

- **Antigravity is experimental.** If its MCP surface or agent loop fails on any task, fall back to Gemini chat with the brief pasted manually. The brief is structured to support either flow.
- **Voice drift.** Three tools produce three voices. The Cowork review pass exists specifically to catch and reconcile this. Style anchor: `core/rules/token-efficiency.md`.
- **Schedule risk.** Each tool moves at its own pace. The longest brief (Antigravity's, six items) sets the critical path. Reviewer can begin merging completed branches before all are done.
- **Empirical lessons.** Track how each tool actually performed — wall-clock, rework rate, voice quality — and write the lessons into `docs/reviews/sprint-01-review.md`. This becomes case-study-02.
