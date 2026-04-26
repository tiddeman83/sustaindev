---
name: idea-to-prepared-task
description: Captures a vague idea and produces a structured task brief queued for execution at a chosen time.
version: 0.1.0
status: experimental
---

# Idea To Prepared Task

## Trigger

Activate this skill when the user has a new idea they want to preserve but do not want to start working on immediately. Common signals: "I had an idea about…", "remind me to…", "I want to eventually…", or any request to queue work for a future session. The skill is also appropriate when the user wants to convert a rough note into something a cloud tool can execute without further clarification.

## Inputs

- The rough idea as free text, one to three sentences describing what the user wants to accomplish.
- The project context file at `projects/<name>/PROJECT_CONTEXT.md` for the relevant project.
- The project codemap at `projects/<name>/CODEMAP.md` for the relevant project.
- The user's preferred execution window: `low` (no urgency, schedule freely), `medium` (next available session), or `high` (next scheduled window, highest queue priority).

## Workflow

1. Capture the idea by running `scripts/schedule/capture-idea.sh "<short title>"` — this writes a stub file to `core/scheduling/queue/captured/` with a generated id, the raw idea text, a timestamp, and the execution-window preference.
2. Run `python3 scripts/schedule/prepare-task.py <id>` — this reads the captured stub plus the project layer files (`PROJECT_CONTEXT.md`, `CODEMAP.md`, `AI_POLICY.md`, `MAINTAINABILITY_NOTES.md`, `VERIFY.md`) and calls a local LM Studio model to produce a structured task brief in `core/scheduling/queue/prework-ready/`. See "Execution Tier Choice" below and `scripts/schedule/README.md` for full options.
3. Triage the prepared brief: open it in `core/scheduling/queue/captured/` and review the scope, file targets, verify commands, and maintainability constraints. Edit the brief if any field is wrong, missing, or overly broad — a brief that is wrong at preparation time will produce a wrong diff at execution time.
4. Move the reviewed brief to `core/scheduling/queue/scheduled/` and set the `execution_window` field to match the user's preference.
5. At the scheduled time, hand the brief to the chosen cloud tool (Codex, Claude Code, or equivalent) for execution; the brief contains everything the tool needs to act without follow-up questions.
6. After execution, review the resulting diff against the brief's `success_criteria` field and confirm that the acceptance criteria are met before treating the task as done.
7. Move the brief to `core/scheduling/queue/completed/` and append a short retrospective note — one to three sentences covering what matched the brief, what diverged, and why.

## Execution Tier Choice

The prepare step in step 2 can run on a local model or a cloud model. Route to a local model when the idea is well-scoped, the project context is complete, and the output will be reviewed by a human before any code change — local models handle structural expansion of a clear input well. Route to a cloud model when the idea spans multiple files, requires cross-document consistency checks, or when the project context is sparse and the model needs to reason about gaps. The detailed routing triggers are in `core/rules/model-routing.md`. Empirical evidence on which task classes the local tier handles well is in `docs/measurement/case-study-01.md`.

## Output

The prepared task brief follows the format defined in `core/scheduling/templates/scheduled-task.md`. That file is the authoritative schema; the fields it defines include:

- `scope` — what the task changes and what it explicitly does not change.
- `file_targets` — the specific files expected to be modified, with rationale.
- `verify_commands` — the commands to run after the change to confirm correctness.
- `maintainability_constraints` — which of the six dimensions from `core/rules/maintainability.md` are most at risk and what the constraint is.
- `success_criteria` — the acceptance criteria the reviewer uses to approve the diff.
- `execution_tier_suggestion` — local or cloud, with one-sentence rationale.
- `time_window_suggestion` — the recommended execution window based on scope and priority.

## Verification

After step 1: the captured stub exists at `core/scheduling/queue/captured/<id>.md` and contains the raw idea text, timestamp, and execution-window preference.

After step 2: the prepared brief exists in the same directory and contains all fields listed in "Output" above with no empty required fields.

After step 6: the diff produced at execution addresses each item in `success_criteria` and does not touch files outside `file_targets` without a documented reason in the retrospective note.

## Maintainability Impact

This skill produces no code change directly; it produces a brief that a cloud tool executes in a later session. The maintainability impact note required by `core/rules/maintainability.md` applies at execution time, not at preparation time — the brief's `maintainability_constraints` field prepares the executing tool to produce that note, but the note itself is the executing tool's responsibility. The preparation workflow is read-only with respect to the codebase.
