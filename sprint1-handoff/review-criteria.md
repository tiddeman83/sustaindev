# Review Criteria

What Cowork will check when each PR returns. Each item is either a hard pass/fail or a fixable issue. Hard fails block the merge; fixable issues are recorded as PR comments and the owning tool revises.

## Hard Fails (Block Merge)

- File created at the wrong path.
- Required section missing or out of required order.
- Word count outside the specified range by more than 25%.
- File contains invented statistics, percentages, or dollar figures not traceable to `case-study-01-data.md` or other measurement evidence in the repo.
- File contains any name listed in `.github/forbidden-names.txt` — CI catches this independently via `.github/workflows/validate.yml`.
- File contains credentials, API keys, internal URLs, or customer data.
- First-person voice ("I think", "we believe", "in our experience"). Imperative or second person required throughout.
- File contains a "Conclusion", "Summary", "FAQ", or "Common Pitfalls" section. These pad without adding signal.
- File depends on a tool not in the v0.1 scope (Antigravity, Warp, VS Code adapters are deferred to v0.2+ except for the LM Studio adapter being built in this sprint).
- CI fails on the PR (link checker, required-files check, private-name leak check).

## Fixable Issues (Comment Then Re-Push)

- Marketing voice: "AI-powered", "seamlessly", "best-in-class", "10x", "next-generation", etc. Replace with specific, evidence-backed phrasing.
- Bullet points shorter than one full sentence. Either expand to a sentence or convert to prose.
- Code blocks used for non-code content (e.g., wrapping prose in triple backticks).
- ASCII tables used for content that reads better as prose. Keep tables for tabular comparisons; otherwise prose.
- References to files via absolute path or URL instead of relative repo path.
- Heading hierarchy errors (skipping H2 → H4, multiple H1s).
- Inconsistent terminology vis-à-vis `context.md` ("prep" instead of "prework", "cache" used inconsistently for stable vs live data).
- Tone drift from `core/rules/token-efficiency.md` style anchor.
- Cross-file references that don't resolve (e.g., linking to a file the brief did not assign).

## File-Type Specific Checks

### Rule files (`core/rules/*.md`)

- Six sections is the canonical shape: Purpose / Core Rules / one or more topical sections / Verification. Adjust to fit content; do not add filler sections.
- The Purpose section is one short paragraph, under 100 words.
- The Verification section refers to where evidence lives (case studies, measurement docs), not to a tool or a vendor.
- Rule items are sentence-form, one per line, numbered or bulleted consistently.
- Total word count: 400–700 unless the brief specifies otherwise.

### Skill files (`core/skills/<name>/SKILL.md`)

- Required sections in this order: front matter (YAML), Trigger, Inputs, Workflow, Output, Verification, Maintainability Impact.
- Front matter includes `name`, `description`, optional `version`, optional `status: experimental` for v0.1 unless the brief says stable.
- Trigger is concrete: what the user does or says that should activate this skill.
- Workflow is numbered steps. Each step is one or two sentences. Numbered steps within a section restart at 1.
- Output includes the file path, format, and an example fragment when useful.
- Verification names the command or file the user checks to confirm the skill ran correctly.
- Maintainability Impact lists the dimensions touched (architecture fit, coupling, naming, testability, error handling, change cost). Skills that produce no code change can write "N/A — read-only skill".

### Adapter templates (`adapters/<tool>/*.template`)

- Files are named with `.template` suffix; tools generate working files from them.
- Reference `core/` paths rather than duplicating content. The template should be the *thinnest* glue layer.
- Length: 30–80 lines target. Anything longer is a sign of duplication that belongs back in `core/`.
- Include a comment block at the top stating: which tool this targets, what the user does to install it, and which `core/` files are referenced.

### Templates (`core/templates/*.md`)

- File is itself a fillable form. Includes placeholders in `<angle-brackets>` or `{{double-braces}}`, consistently.
- Top-level comment explains: what the template is for, when to use it, what files reference it.
- Includes one short worked example (3–6 lines) showing what filled-in content looks like.
- Avoids project-specific examples — templates are tool-neutral and project-neutral.

### Shell scripts (`scripts/**/*.sh`)

- POSIX-compliant; first line is `#!/bin/sh` or `#!/usr/bin/env bash` if bash-specific features are used.
- `set -eu` near the top.
- Comments explain *why*, not *what*, when the line isn't self-evident.
- No hardcoded user paths.
- Help text printed when run with `--help` or no arguments where applicable.
- Idempotent where possible (creating a queue file with the same id is a noop).

### Measurement docs (`docs/measurement/*.md`)

- Numbers cited are traceable to a raw data file (`scripts/sprint1/output/measurement.json`, etc.).
- Tables include units in the header.
- Counterfactual estimates are clearly labeled as estimates, not measurements.
- Conclusion section states what the data does and does not support, and lists what was not tested.

## What "Good" Looks Like

A PR with the following profile lands cleanly:

- All required files exist at the right paths.
- CI green.
- Each file's structure matches the brief.
- Voice matches the style anchor.
- No invented numbers; all cited data is traceable.
- Cross-file references resolve.
- The reviewer reads it once and either approves with no comments or leaves 1–3 small comments that the owning tool fixes in a single follow-up push.

## What "Acceptable but Needs Revision" Looks Like

- Structure correct, but prose drifts from the style anchor (clichés, marketing voice, soft claims).
- One or two sections under or over the word target by 30–50%.
- Bullet items inconsistently formatted within a single list.
- Reasonable but inconsistent terminology choices.

These are the bulk of expected feedback. The owning tool revises and re-pushes.

## What "Reject and Rewrite" Looks Like

- File fundamentally misunderstands the brief (wrong purpose, wrong audience, wrong format).
- File hallucinates content (invented features, fictional measurement numbers, references to files that do not exist).
- File leaks private data, secrets, or includes deprecated terminology.
- Multiple structural sections missing.

If a file is rejected, the reviewer documents why in the PR and the owning tool starts over with a corrected brief. This should be rare; if it happens twice for the same tool, the brief itself is at fault and Cowork rewrites the brief before the next attempt.
