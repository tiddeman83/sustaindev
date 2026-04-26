# Brief: Claude Code

You are Claude Code working on Sprint 1 of SustainDev v0.1. This brief assigns you four files. Complete them in the order listed; later tasks reference earlier ones.

## Setup

Branch:

```bash
git checkout main
git pull
git checkout -b sprint1/claude-code
```

Required reading before touching any file:

1. `sprint1-handoff/README.md`
2. `sprint1-handoff/context.md` — tone rules, vocabulary, anti-patterns
3. `sprint1-handoff/review-criteria.md` — what will get your PR rejected
4. `core/rules/token-efficiency.md` — primary style anchor; match its voice

## Tasks

### Task 1: `core/rules/maintainability.md`

**Goal.** A tool-neutral rule document that makes maintainability a required output of every code-changing workflow. Six condensed dimensions (replacing the original 12).

**Word count.** 500–700.

**Required sections, in this order:**

1. `# Maintainability` (H1)
2. `## Purpose` — one short paragraph. Why maintainability is treated as a required output, not an optional concern. What this rule file is and is not (it is a discipline; it is not a substitute for code review).
3. `## The Six Dimensions` — list the dimensions with one-sentence definitions each: **architecture fit**, **coupling**, **naming**, **testability**, **error handling**, **change cost**. Each definition is a sentence, not a paragraph.
4. `## Required Output: Maintainability Impact Note` — explain that every code-changing workflow must produce a short note covering which dimensions were touched and how. Show the expected shape of that note (~5 lines).
5. `## When to Apply` — short prose section. The dimensions apply to: feature delivery, bug fixes, refactors, dependency upgrades. They do not apply to: read-only investigation, documentation-only changes, formatting-only changes.
6. `## Project-Specific Overrides` — short prose section. Each project under `projects/<name>/` may add maintainability rules tied to its stack and architecture, recorded in `MAINTAINABILITY_NOTES.md`. The core dimensions still apply.
7. `## Verification` — short prose section. Reference where evidence lives. The maintainability impact note is checked during code review, not after merge. Cite `core/rules/token-efficiency.md` as a tone reference.

**Do not include:**

- Marketing voice.
- The full 12-dimension list from `build_plan.md` Section 6.E. Six is the new canonical set.
- Specific framework names (React, .NET, Django) unless the dimension genuinely needs an example.

**Acceptance.** Reviewer compares your six dimensions against build_plan Section 6.E and confirms the condensation is principled, not arbitrary.

---

### Task 2: `core/templates/project-context.md`

**Goal.** A fillable template that every project under `projects/<name>/` uses to record its compact, durable context. The template feeds into Claude Code's `CLAUDE.md.template` (Task 4) — same author should keep them voice-aligned.

**Word count.** 400–600 (mostly placeholder structure with short prose explanations).

**Required sections, in this order:**

1. `# Project Context: <project-name>` (H1, with placeholder)
2. `<!-- TEMPLATE COMMENT -->` block at the top explaining: what this template is for, when to update it, what files reference it (CLAUDE.md.template, AGENTS.md.template, the hero skill).
3. `## What This Project Is` — placeholder paragraph. One-sentence purpose, who uses it, what it integrates with.
4. `## Tech Stack` — bulleted placeholder list: language, framework, runtime, key libraries, datastore, deployment target.
5. `## Architecture (One Paragraph)` — placeholder paragraph constraining the description to one paragraph, not a treatise.
6. `## Where Things Live (Codemap Pointer)` — references the project's `CODEMAP.md` (Codex's deliverable) by relative path.
7. `## Verification Commands` — bulleted placeholder list: build command, test command, lint command, run-locally command. References `VERIFY.md` if more detail is needed.
8. `## AI Policy Pointers` — references `AI_POLICY.md` and `MAINTAINABILITY_NOTES.md` by relative path.
9. `## Known Risks` — references `RISKS.md` by relative path.
10. `## Decisions Log` — references `DECISIONS.md` by relative path.

**Format.** Use `<angle-bracket>` placeholders consistently. Include one short worked example at the bottom under `## Example (Filled In)` showing 6–10 lines of what a real project's filled-in section looks like. The example must be sanitized — no names from `.github/forbidden-names.txt`, no real customer or business names. Use a generic example like "an internal CLI tool for log analysis."

**Acceptance.** A new project can copy this template, fill it in within 15 minutes, and produce something Claude Code or another AI tool can use as initial context.

---

### Task 3: `core/skills/idea-to-prepared-task/SKILL.md`

**Goal.** The hero skill of v0.1. Documents the workflow that takes a vague idea and produces a structured task brief queued for execution at a chosen time. This is the central document of the v0.1 release; the README and roadmap link to it.

**Word count.** 600–900.

**Required sections, in this order:**

1. YAML front matter (between `---` lines) with fields: `name: idea-to-prepared-task`, `description: <short>`, `version: 0.1.0`, `status: experimental`.
2. `# Idea To Prepared Task` (H1)
3. `## Trigger` — concrete prose. What the user says or does that should activate this skill. Example: "User has a new idea they don't want to lose but don't want to start working on right now."
4. `## Inputs` — bulleted list. The rough idea (free text, 1–3 sentences), the project context (path to `projects/<name>/PROJECT_CONTEXT.md`), the project codemap (path to `projects/<name>/CODEMAP.md`), the user's preferred execution window (low / medium / high priority).
5. `## Workflow` — numbered steps, each one or two sentences:
   1. Capture the idea via `scripts/schedule/capture-idea.sh "<short title>"` — this writes a stub to `core/scheduling/queue/captured/`.
   2. Run `scripts/schedule/prepare-task.sh <id>` — produces a structured task brief from the captured stub plus the project context and codemap. See "Execution Tier Choice" below.
   3. Triage the prepared brief: review the scope, file targets, verify commands, maintainability constraints. Edit the brief if anything is wrong.
   4. Move the brief to `core/scheduling/queue/scheduled/` with the chosen execution window.
   5. At the scheduled time, hand the brief to a cloud-tool (Codex, Claude Code) for execution.
   6. Human reviews the resulting diff against the brief's acceptance criteria.
   7. Move the brief to `core/scheduling/queue/completed/` with a short retrospective note.
6. `## Execution Tier Choice` — short prose section. The prepare step can run on a local model OR a cloud model. Reference `core/rules/model-routing.md` for the routing decision. Note that empirical evidence in `docs/measurement/case-study-01.md` informs which task classes the local tier handles well.
7. `## Output` — describes the prepared task brief format. Reference `core/scheduling/templates/scheduled-task.md` (Codex's deliverable) by relative path. Briefly list the fields the brief contains: scope, file targets, verify commands, maintainability constraints, success criteria, execution-tier suggestion, time-window suggestion.
8. `## Verification` — how the user confirms each step worked. The captured stub exists with the expected fields. The prepared brief contains all required sections. The diff produced at execution matches the brief's acceptance criteria.
9. `## Maintainability Impact` — one short paragraph. This skill produces no code change directly; it produces a brief that is later executed. The maintainability impact note is required at execution time, not at preparation time. Reference `core/rules/maintainability.md`.

**Do not include:**

- Specific local-model recommendations (those live in `adapters/lm-studio/usage.md`).
- Specific cloud-model recommendations.
- Code blocks for shell commands beyond the three referenced above.

**Acceptance.** A reviewer can read the SKILL.md and execute the workflow end-to-end on a sample idea using only the documented commands and templates. References to other Sprint 1 files must resolve once those files are merged.

---

### Task 4: `adapters/claude-code/CLAUDE.md.template`

**Goal.** A thin Claude Code adapter — the `CLAUDE.md` template that Claude Code reads when working in a project. Refers to `core/` files rather than duplicating content. Lives as a template; project owners copy it to `<project>/CLAUDE.md` and fill in the project-specific sections.

**Length.** 30–80 lines.

**Required structure.** Top of file: HTML comment block stating what the template is, who reads it (Claude Code), how to install it (`cp adapters/claude-code/CLAUDE.md.template <project>/CLAUDE.md` and fill in placeholders), which `core/` files are referenced.

Then sections matching what Claude Code expects in a project's `CLAUDE.md`:

1. **Project Identity.** One-line project name + one-paragraph purpose. Placeholder.
2. **Read Before Acting.** Bulleted list pointing to `core/principles/development-principles.md`, `core/rules/token-efficiency.md`, `core/rules/maintainability.md`, `core/rules/model-routing.md`, the project's `PROJECT_CONTEXT.md`, the project's `CODEMAP.md`, the project's `VERIFY.md`. Each link is a relative path.
3. **Verification Commands.** Pointer to `<project>/VERIFY.md`.
4. **AI Policy.** Pointer to `<project>/AI_POLICY.md`.
5. **Maintainability Constraints.** Pointer to `<project>/MAINTAINABILITY_NOTES.md`.
6. **Skills Available.** Bulleted list of relevant `core/skills/<name>/SKILL.md` entries. For v0.1, only `idea-to-prepared-task` is shipped.

**Do not include:**

- Inline copies of any `core/` content. The point of an adapter is to reference, not duplicate.
- Project-specific text beyond placeholders.
- Slash command definitions or hook configurations — those go in `adapters/claude-code/commands/` and `adapters/claude-code/agents/`, deferred to v0.2.

**Acceptance.** The template is under 80 lines, all references resolve once Sprint 1 merges, and a project owner can fill it in for a sample project in under 5 minutes.

---

## Hand Back

When all four files exist on `sprint1/claude-code` and pass `.github/workflows/validate.yml` locally:

```bash
git add core/rules/maintainability.md core/templates/project-context.md core/skills/idea-to-prepared-task adapters/claude-code/CLAUDE.md.template
git commit -m "Sprint 1 Claude Code deliverables"
git push -u origin sprint1/claude-code
```

Open a PR titled `Sprint 1: Claude Code deliverables` against `main`. The PR description should:

- List the four files added.
- Note any deviations from the brief and why.
- Confirm the four CI checks pass locally.
- Tag the Cowork reviewer for review.

## Self-Check Before Pushing

- All four files exist at the exact paths in this brief.
- Each file's word count is within the specified range (run `wc -w <file>` to check).
- No file contains any of the names listed in `.github/forbidden-names.txt` (CI catches these but spotting early is faster).
- Voice matches `core/rules/token-efficiency.md` — no first person, no marketing language, no FAQ sections.
- All cross-file references use relative paths and resolve once the other tool branches merge.
- `core/skills/idea-to-prepared-task/SKILL.md` has correct YAML front matter (parses as YAML; `name`, `description`, `version`, `status` fields present).

If anything blocks you for more than 30 minutes, leave a comment on the PR or in `docs/reviews/sprint-01-blockers.md` and continue with the next task.
