# Sprint 1 Workstreams: Hero Workflow + Minimum Core

This is the active workstream plan for Sprint 1 from `revised_sprints_v0.1.md`.

Sprint 1 has one goal: ship the `idea-to-prepared-task` hero workflow with the minimum core needed to make it credible, measurable, and publishable as v0.1.0.

## Operating Constraint

Do not expand into the original eight-sprint architecture during Sprint 1. Anything outside the hero workflow, minimum core, Codex adapter, Claude Code adapter, LM Studio adapter, and measurement proof belongs in v0.2+.

## Workstream A: Minimum Core

Owner:

- Codex

Purpose:

Create the smallest durable core that can support the hero workflow without becoming a general prompt library.

Files:

- `core/principles/development-principles.md`
- `core/rules/token-efficiency.md`
- `core/rules/maintainability.md`
- `core/rules/model-routing.md`
- `core/templates/codemap.md`
- `core/templates/project-context.md`

Acceptance criteria:

- Each file is under 200 lines.
- The rules are tool-neutral.
- Maintainability is condensed to six dimensions: architecture fit, coupling, naming, testability, error handling, change cost.
- Model routing has objective local/cloud/human review triggers.
- Templates are usable without reading the whole build plan.

## Workstream B: Hero Skill

Owner:

- Codex

Purpose:

Define the workflow users will actually copy first.

Files:

- `core/skills/idea-to-prepared-task/SKILL.md`

Required headings:

- `## Trigger`
- `## Workflow`
- `## Output`
- `## Verification`

Acceptance criteria:

- The skill describes capture -> local prework -> cloud handoff -> human review.
- The skill references core rules instead of duplicating them.
- The skill includes stop conditions for unsafe local-model use.

## Workstream C: Scheduling Scripts And Queue

Owner:

- Codex

Purpose:

Make the hero workflow executable from the terminal.

Files:

- `core/scheduling/templates/scheduled-task.md`
- `core/scheduling/queue/captured/.gitkeep`
- `core/scheduling/queue/prework-ready/.gitkeep`
- `core/scheduling/queue/scheduled/.gitkeep`
- `core/scheduling/queue/completed/.gitkeep`
- `scripts/schedule/capture-idea.sh`
- `scripts/schedule/prepare-task.sh`
- `scripts/schedule/list-queue.sh`

Acceptance criteria:

- `capture-idea.sh` creates a captured markdown task with a stable ID.
- `prepare-task.sh` calls an OpenAI-compatible LM Studio endpoint when configured.
- `prepare-task.sh` fails clearly if LM Studio is unavailable.
- `list-queue.sh` shows captured and prework-ready tasks.
- Runtime queue artifacts remain ignored except `.gitkeep` and example tasks.

## Workstream D: LM Studio Adapter

Owner:

- Codex

Local model role:

- Draft task briefs only.
- No code changes.
- No final review.

Files:

- `adapters/lm-studio/prework-prompt.md`
- `adapters/lm-studio/usage.md`

Acceptance criteria:

- Setup instructions explain LM Studio local server usage.
- The prompt produces a structured task brief.
- The adapter clearly states what local models must not do.
- The generated handoff is suitable for Codex or Claude Code.

## Workstream E: Cloud Tool Adapters

Owners:

- Codex owns `adapters/codex/`.
- Claude Code should draft or review `adapters/claude-code/`.

Files:

- `adapters/codex/AGENTS.md.template`
- `adapters/claude-code/CLAUDE.md.template`

Acceptance criteria:

- Each adapter is 30-80 lines.
- Each adapter references `core/` instead of duplicating full rules.
- Claude Code can use the prepared task brief without needing SustainDev-specific explanation.
- Codex can use the prepared task brief and project context templates directly.

## Workstream F: Measurement Proof

Owner:

- Codex

Support:

- Human supplies real task data where needed.
- Local model can help format the case study draft.

Files:

- `docs/measurement/methodology.md`
- `docs/measurement/case-study-01.md`

Acceptance criteria:

- Methodology explains how to count tokens, dollars, and time.
- Case study compares a baseline cloud-only flow against the hero workflow.
- The case study is honest about uncertainty and tokenizer differences.
- If real numbers are not available yet, the case study must be clearly marked `status: draft-needs-real-measurement`.

## Workstream G: Validation And Public Safety

Owner:

- Codex

Purpose:

Keep Sprint 1 publishable.

Tasks:

- Run required-file checks locally where possible.
- Check all markdown links that do not require network.
- Confirm private names do not appear in tracked public files.
- Confirm `projects/.private-map.md` stays ignored.
- Confirm generated queue artifacts are ignored.
- Confirm CI skill-schema stub passes for `idea-to-prepared-task`.

Acceptance criteria:

- `git status --short` contains no accidental private files.
- Forbidden project names do not appear outside `.github/forbidden-names.txt` and ignored private files.
- Sprint 1 files match `revised_sprints_v0.1.md`.

## Claude Code Handoff

Claude Code should work only on the Claude adapter during Sprint 1.

Suggested prompt:

```text
Read README.md, revised_sprints_v0.1.md, core/rules/*.md, core/skills/idea-to-prepared-task/SKILL.md, and adapters/codex/AGENTS.md.template. Draft adapters/claude-code/CLAUDE.md.template as a thin Claude Code adapter for SustainDev's hero workflow. Do not duplicate the full core rules. Reference core files and prepared task briefs. Keep it under 80 lines.
```

Expected Claude Code output:

- One file: `adapters/claude-code/CLAUDE.md.template`
- Optional notes: any Claude-specific friction or command ideas for v0.2

## Strong-Reviewer Package

At the end of Sprint 1, prepare:

- `README.md`
- `revised_sprints_v0.1.md`
- `docs/roadmap.md`
- `core/`
- `adapters/codex/`
- `adapters/claude-code/`
- `adapters/lm-studio/`
- `scripts/schedule/`
- `docs/measurement/`
- `git status --short`
- Validation results

Reviewer prompt:

```text
Review Sprint 1 of SustainDev against revised_sprints_v0.1.md. Focus on whether the v0.1 hero workflow is actually usable, whether the local/cloud model routing is safe, whether the repository stays public-safe, whether the adapters are thin, and whether the measurement claims are defensible. Return pass / pass with fixes / fail, with required fixes before v0.1.0.
```

## Stop Conditions

Stop and ask before continuing if:

- Real measurement data is required and unavailable.
- LM Studio endpoint assumptions need to match a specific local setup.
- Claude Code produces adapter content that duplicates core rules.
- Any private project detail appears necessary for the public case study.
- The work starts expanding into v0.2 adapter scope.

## Recommended Build Order

1. Workstream A: minimum core.
2. Workstream B: hero skill.
3. Workstream C: scheduling queue and scripts.
4. Workstream D: LM Studio adapter.
5. Workstream E: Codex adapter, then Claude Code handoff.
6. Workstream F: measurement methodology and case study.
7. Workstream G: validation and reviewer package.
