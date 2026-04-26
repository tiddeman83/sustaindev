# SustainDev Public Roadmap

This roadmap is intentionally short. Each version aims to be small enough to understand, evaluate, and contribute to. Detailed sprint planning lives in [`revised_sprints_v0.1.md`](../revised_sprints_v0.1.md).

## Versioning Philosophy

- **Ship what's usable, label honestly.** v0.1 means *early, working, opinionated*. It does not mean *complete*.
- **One workflow per version, with measurement.** Every version adds at least one new workflow with a real before/after case study.
- **Adapters follow skills, not the other way around.** A skill must prove its value in `core/` before adapters export it.

## v0.1 — Hero Workflow + Foundation (current)

**Sprint 0:** Repository foundation. License (Apache-2.0), positioning, sustainability definition, issue templates, minimal CI, sanitized docs.

**Sprint 1:** The hero workflow `idea-to-prepared-task` end-to-end. Five core files (principles, token-efficiency, maintainability, model-routing, templates). Two adapters (Codex + Claude Code). LM Studio adapter with prework prompt. One measurement case study with real numbers.

**Then: tag v0.1.0 and publish.**

## v0.2 — Adapters Expansion

- Warp adapter (terminal recipes for capture, prepare, list, complete)
- VS Code adapter (MCP config + tasks.json template)
- Cursor rules export adapter
- Cline rules export adapter
- Additional MCP policy templates (GitHub, Linear, browser, docs, database)
- Second measurement case study from an outside contributor (target)

## v0.3 — More Skills

Each skill ships only after at least one case study demonstrating value:

- `repo-onboarding` — fast project understanding via codemap + project-context
- `feature-delivery` — structured feature work with maintainability gate
- `bug-investigation` — minimum-context bug isolation
- `maintainability-review` — standalone maintainability pass
- `low-token-debugging` — debugging without re-scanning the repo

## v0.4 — Agents and Commands

The agent and command layer from the original sprint plan, deferred until skills shake out. Includes:

- Planner, implementation, reviewer, maintainability-reviewer, test-strategist, MCP-context, scheduler agents
- Thin command entry points: `plan-feature`, `bugfix`, `review-maintainability`, `map-repo`, `prepare-idea`, `schedule-idea`, `run-prework`

## v0.5 — Project Adoption Examples

- Two sanitized example projects (`project-a`, `project-b`) demonstrating full project context, codemap, verify, maintainability notes, MCP policy, decisions, risks
- Project template (`projects/_template/`)

## v0.6 — Antigravity Adapter

Wait for Antigravity's API/MCP surface to stabilize. Marked experimental until at least one external user reports a working integration.

## v0.7 — Validation and Sync Automation

Beyond the minimal CI shipped in v0.1:

- Stale codemap detection
- Adapter sync scripts (`sync-codex`, `sync-claude-code`, `sync-cursor`, `sync-cline`)
- Skill format validation expanded to schema-level checks
- Pattern-promotion workflow (project-specific lessons → core skills)

## v1.0 — When?

When the system has been used by at least 10 outside developers across at least 3 different tool setups and the case-study repository has at least 5 entries with measurable savings, v1.0 becomes a meaningful milestone. Not before.

## How Versions Become Issues

Each roadmap version corresponds to a GitHub milestone. Issues are tagged to milestones. Contributors can pick anything tagged `good first issue` from the active or upcoming milestone. New ideas open as issues with no milestone until they earn one.

## What's Explicitly Not Planned

- A web UI. SustainDev is files and scripts; that's a feature, not a deficiency.
- Dependence on any single model provider.
- A package manager. Adoption is `git clone` + adapter install.
- "Auto-update" of project files from cloud. Adapters generate explicitly, never silently.

## Feedback

Open an issue tagged `roadmap` to propose additions, removals, or reordering. Roadmap-shaping is the most valuable contribution at this stage.
