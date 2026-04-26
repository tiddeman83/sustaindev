# Sprint 1 Shared Context

Every brief in this folder assumes you have read or scanned the files listed here. They are the minimum context for producing work that integrates with the existing repository.

## Required Reading Before Starting Any Task

In this order, time-budgeted:

1. `sprint1-handoff/README.md` (3 min) — coordination model, ownership table, branching, review flow.
2. `revised_sprints_v0.1.md` (5 min) — current execution plan and Sprint 1 scope. Authoritative source for what v0.1 ships.
3. `core/rules/token-efficiency.md` (3 min) — **primary style anchor**. New rule files and prose docs should match its prose density, section shape, and tone.
4. `README.md` (2 min) — public framing.
5. `docs/positioning.md` (3 min) — how SustainDev differs from Cursor Rules, Cline, Aider, Continue.dev, OpenHands, Claude Code, Codex AGENTS.md. Useful when writing routing rules and adapter templates.
6. `docs/sustainability-defined.md` (2 min) — what "sustainable" means in this project.

## Optional But Useful

- `build_plan.md` — long-term strategic plan. Sections 5 (Design Principles), 6.E (Maintainability), 6.F (Token Efficiency), 6.G (MCP Strategy), 6.H (Scheduling) are particularly relevant.
- `CONTRIBUTING.md` — quality bar for contributions.
- `scripts/sprint1/` — the local-model test run that produced the data behind case-study-01. The data digest is in `case-study-01-data.md`.

## Tone Rules (Apply To All Prose Files)

These apply to every markdown file produced for Sprint 1 unless the brief overrides them.

- **No first person.** Write in second person ("you") or imperative ("Prefer narrow context"). The text should read as instruction or rule, not as a personal voice.
- **No invented numbers.** Do not write "saves 80%" or "$0.40 per task" or "10x faster" unless the number comes from `case-study-01-data.md` or measurement evidence already in the repo. If a claim needs a number, write "measured per task" or "varies by codebase" or cite the case-study file by relative path.
- **No marketing voice.** Closer to a senior engineer's wiki page than to a product landing page. Calm, opinionated, specific.
- **No "common pitfalls" or "FAQ" sections.** They pad files without adding signal.
- **No emojis** unless the brief explicitly asks for them.
- **References are relative repo paths**, not URLs. Example: link to `core/rules/maintainability.md`, not to `https://github.com/...`.
- **Code blocks only when the section is about syntax, commands, or templates.** Inline backticks for short identifiers. Avoid ASCII tables for things that read better as prose.
- **Bullets must be at least one full sentence each.** Two-word bullets are usually a sign that the text should be prose.

## Style Anchor: `core/rules/token-efficiency.md`

This file already exists in the repo and is the reference for tone, density, and section shape. New rule files (`maintainability.md`, `model-routing.md`, etc.) should look and feel like siblings of this one. Specifically:

- Roughly the same word count range (400–700 words for a rule file).
- Six sections is a reasonable default; adjust to fit content.
- Each section opens with one or two sentences of prose context, then either continues as prose or moves into a short bulleted list.
- The rule list itself is bullet-form with one-sentence rules.
- The closing section ("Verification" in `token-efficiency.md`) refers the reader to where evidence lives, not to a tool or vendor.

If you produce a file that reads materially differently in voice, expect the review pass to either ask for revisions or rewrite the prose for consistency.

## Project-Specific Vocabulary

Use these terms consistently:

- **core layer** — files under `core/` containing tool-neutral, durable knowledge.
- **adapter** — files under `adapters/<tool>/` exposing core knowledge in a specific tool's format. Adapters reference `core/` rather than duplicating it.
- **prework** — preparation work done before code change: codemap drafts, idea triage, summarization, classification, risk extraction. The prework tier is where local models add value.
- **finish** — the cloud-model step that produces final output: code changes, full-document drafting, cross-document consistency, final review.
- **strong fit / weak fit** — task classes where a particular execution tier (local vs cloud) is or isn't appropriate. See `core/rules/model-routing.md` once it exists.
- **measurement** — empirical before/after numbers (tokens, dollars, wall-clock) backing a workflow claim. Lives in `docs/measurement/`. Never assert a savings claim without referencing measurement.
- **scheduled task** — a captured idea that has been triaged, prepared, and queued for execution at a chosen time window. Lives in `core/scheduling/queue/`.
- **maintainability impact** — a short note attached to any code-changing workflow describing its effect on architecture fit, coupling, naming, testability, error handling, and change cost.

## Anti-Patterns to Avoid

If you find yourself writing any of these, stop and rewrite:

- "AI-powered" — empty modifier.
- "Seamlessly integrates" — claim without evidence.
- "Best-in-class" — marketing voice.
- "10x" anything without a measurement reference.
- "We believe..." — we are not a we; the project speaks in instructions.
- "In conclusion" or "To summarize" — close the file when the content ends, not with a wrap-up.

## What Each Brief Adds On Top

The shared context above is the floor. Each `brief-<tool>.md` adds:

- The specific files that tool owns.
- Per-file system prompt and section structure.
- Per-file word count target.
- Per-file acceptance criteria.
- Branch and PR conventions specific to that tool's workflow.

If anything in a brief contradicts this shared context, the brief wins — but flag the contradiction in the PR description so we know to reconcile.
