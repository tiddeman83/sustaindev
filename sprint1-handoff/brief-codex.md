# Brief: Codex

You are OpenAI Codex working on Sprint 1 of SustainDev v0.1. This brief assigns you six deliverables (one adapter template, two `core/` templates, two shell scripts, four trivial `.gitkeep` files). Complete in the order listed.

## Setup

Branch:

```bash
git checkout main
git pull
git checkout -b sprint1/codex
```

Required reading before touching any file:

1. `sprint1-handoff/README.md`
2. `sprint1-handoff/context.md` — tone rules, vocabulary, anti-patterns
3. `sprint1-handoff/review-criteria.md` — what will get your PR rejected
4. `core/rules/token-efficiency.md` — primary style anchor

## Tasks

### Task 1: `adapters/codex/AGENTS.md.template`

**Goal.** A thin Codex adapter — the `AGENTS.md` template Codex reads when working in a project. Refers to `core/` files rather than duplicating content. Lives as a template; project owners copy it to `<project>/AGENTS.md` and fill in placeholders.

**Length.** 30–80 lines.

**Required structure.** Top of file: HTML comment block stating what the template is, who reads it (OpenAI Codex CLI), how to install it (`cp adapters/codex/AGENTS.md.template <project>/AGENTS.md` and fill placeholders), which `core/` files are referenced.

Then sections matching what Codex expects in a project's `AGENTS.md`:

1. **Project Identity.** One-line project name + one-paragraph purpose. Placeholder.
2. **Read Before Acting.** Bulleted list pointing to `core/principles/development-principles.md`, `core/rules/token-efficiency.md`, `core/rules/maintainability.md`, `core/rules/model-routing.md`, the project's `PROJECT_CONTEXT.md`, the project's `CODEMAP.md`, the project's `VERIFY.md`. Each link is a relative path.
3. **Verification Commands.** Pointer to `<project>/VERIFY.md`.
4. **AI Policy.** Pointer to `<project>/AI_POLICY.md`.
5. **Maintainability Constraints.** Pointer to `<project>/MAINTAINABILITY_NOTES.md`.
6. **Skills Available.** Mention that Codex consumes the same workflows as other tools via the documented skills under `core/skills/`. For v0.1 the relevant skill is `idea-to-prepared-task`.

**Do not include:**

- Any `core/` content inline. Reference, do not duplicate.
- Project-specific text beyond placeholders.
- Codex-specific configuration (model preferences, tool definitions, command shortcuts) — those go in `adapters/codex/commands.md` and `adapters/codex/usage.md`, deferred to v0.2.

**Acceptance.** The template is under 80 lines, all referenced paths resolve once Sprint 1 merges, and matches the structure of `adapters/claude-code/CLAUDE.md.template` (Claude Code's deliverable) for cross-tool consistency.

---

### Task 2: `core/templates/codemap.md`

**Goal.** A fillable codemap template that every project under `projects/<name>/` uses to give an AI tool a fast, narrow view of where things live without scanning the whole repository. The codemap is the single most-referenced artifact in the routing rules; it must be small enough to read in one model turn.

**Word count.** 400–600 (mostly placeholder structure with short prose explanations).

**Required sections, in this order:**

1. `# Codemap: <project-name>` (H1, with placeholder)
2. HTML comment block at the top explaining: what this template is for, when to update it (when the project's structure changes meaningfully), what files reference it (`PROJECT_CONTEXT.md`, `CLAUDE.md`, `AGENTS.md`, the hero skill), how big it should stay (target: under 200 lines for any project; otherwise it's not a codemap, it's a directory listing).
3. `## Top-Level Layout` — code block showing a tree-like view of the project's top-level directories with a one-line purpose for each. Use placeholder content like `<dir-name>/   # <one-line purpose>`.
4. `## Where Common Tasks Touch` — bulleted list. Each bullet is "to do X, look in Y". Five to eight common tasks: e.g., "to add a new API endpoint, see `src/api/`"; "to change the data model, see `src/models/`"; "to update build configuration, see `pyproject.toml` and `Makefile`". Use placeholders.
5. `## Stable Anchors` — bulleted list. Files that almost never change but are central to understanding the project: entry points, main config files, public interfaces. Three to five entries.
6. `## Hot Spots` — bulleted list. Files or directories that change frequently and where most bugs land. Three to five entries with one-sentence "why it changes a lot" notes.
7. `## What's Out of Scope` — short prose section. Mention parts of the repo an AI tool should generally not need to read: generated code, vendored dependencies, build artifacts, test fixtures unless the task is testing-specific.
8. `## Last Verified` — single line: `Last verified: <YYYY-MM-DD> by <person-or-tool>`. The codemap is only as good as its currency; require a date.

**Format.** Use placeholders consistently. Include one short worked example at the bottom under `## Example (Filled In)` showing 12–20 lines of what a real codemap looks like for a sanitized example project — pick something generic like "a Python CLI for parsing logs". No names from `.github/forbidden-names.txt`.

**Acceptance.** A new project can produce a usable codemap from this template in under 30 minutes. The resulting codemap is small enough to fit in a single AI tool turn alongside the project context.

---

### Task 3: `core/scheduling/templates/scheduled-task.md`

**Goal.** A fillable template for a single scheduled task brief. The hero skill (`core/skills/idea-to-prepared-task/SKILL.md`, owned by Claude Code) writes briefs that follow this format. Every queued idea ends up in this shape.

**Word count.** 350–500 (mostly placeholder structure).

**Required sections, in this order:**

1. `# Scheduled Task: <id>` (H1, with placeholder; `<id>` is a UUID or a short slug like `2026-04-26-add-csv-export`)
2. YAML front matter (between `---` lines) with fields: `id`, `title`, `captured_at`, `prepared_at`, `status` (one of: `captured`, `prework-ready`, `scheduled`, `running`, `needs-review`, `completed`), `priority` (one of: `low`, `medium`, `high`), `execution_tier_suggested` (one of: `local`, `cloud`, `human`), `cloud_tool_suggested` (free text, e.g., `claude-code`, `codex`), `time_window_suggested` (free text, e.g., `22:00-06:00`).
3. `## Captured Idea` — placeholder paragraph. The original rough idea, 1–3 sentences, as the user wrote it.
4. `## Scope` — placeholder paragraph. What this task changes and what it explicitly does not change.
5. `## File Targets` — bulleted placeholder list. Files the task is expected to touch.
6. `## Verify Commands` — bulleted placeholder list. The commands run after execution to confirm the change works. References `<project>/VERIFY.md`.
7. `## Maintainability Constraints` — placeholder paragraph. Which of the six dimensions from `core/rules/maintainability.md` are most at risk for this task; what to preserve.
8. `## Success Criteria` — bulleted placeholder list. Concrete pass/fail conditions.
9. `## Notes for Execution` — placeholder paragraph. Anything the executor (cloud tool or human) should know that isn't captured above. Free-form.
10. `## Retrospective` — placeholder paragraph, filled in after completion. What actually happened, what diverged from the brief, what to remember next time.

**Format.** Placeholders in `<angle-brackets>` consistent with `project-context.md` and `codemap.md`. Include one short worked example at the bottom under `## Example (Filled In)` — a sanitized example, no real customer data.

**Acceptance.** The hero skill workflow can produce a brief in this exact shape, and the brief is readable enough that a cloud tool can execute it without needing to ask clarifying questions.

---

### Task 4: `core/scheduling/queue/{captured,prework-ready,scheduled,completed}/.gitkeep`

**Goal.** Trivial — create empty `.gitkeep` files in four queue directories so git tracks the directories before any task files exist.

**Files (four total):**

- `core/scheduling/queue/captured/.gitkeep`
- `core/scheduling/queue/prework-ready/.gitkeep`
- `core/scheduling/queue/scheduled/.gitkeep`
- `core/scheduling/queue/completed/.gitkeep`

Each file is empty (zero bytes is fine; or contains a single comment `# placeholder for git`).

**Acceptance.** `git ls-files core/scheduling/queue/` lists all four `.gitkeep` files.

---

### Task 5: `scripts/schedule/capture-idea.sh`

**Goal.** A POSIX-compliant shell script that captures an idea as a stub task file under `core/scheduling/queue/captured/`. The simplest piece of the scheduling system — must work reliably.

**Length target.** 60–120 lines (including comments, help text, and basic error handling).

**Behavior.**

```bash
./scripts/schedule/capture-idea.sh "add csv export to report screen"
```

Should:

1. Generate a unique id: `YYYY-MM-DD-<slug-of-title>` where slug is the title lowercased, spaces and special chars replaced with `-`, truncated to a reasonable length (~50 chars).
2. Write a stub file at `core/scheduling/queue/captured/<id>.md` with YAML front matter (`id`, `title`, `captured_at: <ISO-8601 timestamp>`, `status: captured`, `priority: <user-supplied or default 'medium'>`) and a single section `## Captured Idea` containing the title text.
3. Print the captured file path to stdout so the user can pipe it forward.
4. Be idempotent: if a file with the same id already exists, append a numeric suffix (`-2`, `-3`) rather than overwriting.

**Required structure of the script:**

- First line: `#!/bin/sh`.
- `set -eu` near the top.
- Help text printed when called with no arguments or `--help`. Help text shows usage, arguments, exit codes.
- Optional argument `--priority <low|medium|high>` (default `medium`).
- Comments at the head of the file explaining what the script does and which files it reads/writes.

**Error handling.**

- Exit 2 with a clear message if no title is given.
- Exit 3 with a clear message if the queue directory does not exist (suggest the user check the repository layout).
- Exit 4 if the title is empty after slug normalization.

**Do not:**

- Use bash-only features (`[[`, arrays, `${var,,}`). Stick to POSIX `sh`.
- Hardcode user paths.
- Require curl, jq, python, or any binary that is not standard on macOS and Linux.

**Acceptance.** Running `./scripts/schedule/capture-idea.sh "test idea"` from the repo root produces a file at `core/scheduling/queue/captured/<today>-test-idea.md` matching the stub format. Running it twice with the same title produces `<today>-test-idea-2.md`. Running with `--help` prints usage and exits 0.

---

### Task 6: `scripts/schedule/list-queue.sh`

**Goal.** A POSIX-compliant shell script that prints a summary of all queued tasks across the four queue directories.

**Length target.** 60–120 lines.

**Behavior.**

```bash
./scripts/schedule/list-queue.sh
```

Should print a tabular summary grouped by status:

```text
captured (2):
  2026-04-26-add-csv-export       medium  captured 2026-04-26T08:14:00Z
  2026-04-25-fix-login-redirect   high    captured 2026-04-25T22:01:00Z

prework-ready (1):
  2026-04-24-rename-models        medium  prepared 2026-04-25T03:30:00Z

scheduled (0):
  (none)

completed (3):
  ...
```

The script reads each `.md` file in each queue directory, parses the YAML front matter to extract `id`, `priority`, and a relevant timestamp (`captured_at`, `prepared_at`, etc.), and prints the rows.

**Optional flags:**

- `--status <captured|prework-ready|scheduled|completed>` to filter to one queue.
- `--priority <low|medium|high>` to filter by priority.
- `--json` to emit machine-readable output instead of a table.

**Required structure.**

- First line: `#!/bin/sh`.
- `set -eu`.
- Help text via `--help`.
- Comments at the top.

**YAML parsing.** YAML in this codebase is restricted to flat key/value pairs. Use `awk`, `sed`, or `grep`/`cut` — do not require `yq`, `jq`, or python.

**Error handling.**

- If a queue directory is missing, print a warning and continue with the others.
- If a `.md` file lacks expected fields, print "(malformed: <path>)" and continue.

**Acceptance.** Running `./scripts/schedule/list-queue.sh` prints the four sections in order. With sample tasks present in `captured/`, the captured section shows them sorted by `captured_at` descending. `--help` and `--json` work.

---

## Hand Back

When all six deliverables are on `sprint1/codex` and pass `.github/workflows/validate.yml` locally:

```bash
git add adapters/codex/AGENTS.md.template core/templates/codemap.md core/scheduling/ scripts/schedule/
chmod +x scripts/schedule/*.sh
git commit -m "Sprint 1 Codex deliverables"
git push -u origin sprint1/codex
```

Open a PR titled `Sprint 1: Codex deliverables` against `main`. PR description: list deliverables, note any brief deviations, confirm CI passes locally, tag the reviewer.

## Self-Check Before Pushing

- All six deliverables exist at the exact paths in this brief.
- Shell scripts are executable (`chmod +x`).
- Shell scripts pass `sh -n <script>` syntax check.
- Running `./scripts/schedule/capture-idea.sh "test"` from the repo root produces a valid stub file. Running `./scripts/schedule/list-queue.sh` lists it. (Clean up the test stub before pushing.)
- No private project names anywhere.
- Voice and structure of `AGENTS.md.template` matches `adapters/claude-code/CLAUDE.md.template` (cross-tool consistency).
- Templates use `<angle-bracket>` placeholders consistently with the project-context template.

If anything blocks you for more than 30 minutes, leave a note in `docs/reviews/sprint-01-blockers.md` and continue.
