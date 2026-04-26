# Case Study 02: Multi-Tool Coordination on a Real Project Adoption

**Run date:** 2026-04-26
**Project:** project-a (a .NET 8 Avalonia desktop app, ~v0.0.7 internal POC)
**Workflow:** SustainDev `idea-to-prepared-task` hero workflow, applied end-to-end on a real engineering task
**Tools involved:** Cowork (Claude) for brief preparation and review, OpenAI Codex CLI for execution, the SustainDev project-layer files (`PROJECT_CONTEXT.md`, `CODEMAP.md`, `VERIFY.md`, `AI_POLICY.md`, `MAINTAINABILITY_NOTES.md`, `DECISIONS.md`, `RISKS.md`) as the durable context.

## Summary

The first dogfood of the SustainDev v0.1 hero workflow on a real internal project produced 11 new edge-case unit tests, fixed a pre-existing test-bug, and inadvertently surfaced 50+ files of uncommitted work that had been latent for weeks. The workflow took ~60 minutes end-to-end (~25 minutes Cowork + ~35 minutes Codex) and consumed an estimated 16,500–28,500 cloud tokens. The same task without the workflow's discipline would likely have produced redundant work (asking Codex to write tests that already existed, since the latest project plan listed the task as not-yet-started while it had actually been done in a prior sprint), missed the pre-existing test bug, and not surfaced the uncommitted-work problem.

The biggest finding is qualitative, not quantitative: the SustainDev workflow's "look at the existing state before delegating" discipline caught three latent issues (stale plan, uncommitted work, buggy assertion) in 30 seconds of file lookup. Without that discipline, all three would have shipped.

## What Was Tested

A real engineering task on a real project, picked from the project's existing backlog:

- **Task description:** Add edge-case unit tests to a markdown-to-Avalonia-inlines converter. The existing test file had 25 tests covering happy paths (plain text, bold, italic, bullets, multi-line) but lacked coverage for non-string input, unmatched markers, edge bullet cases, Windows line endings, consecutive empty lines, unicode in formatted text, and `ConvertBack` defensive cases.
- **Expected output:** ~10 new `[Fact]` tests, additive only, in the existing test file's style (Arrange-Act-Assert comments, FluentAssertions, section headers with box characters).
- **Constraint:** Do not modify the production converter; document observed behavior, not desired behavior; preserve existing tests.

## Setup

| Field | Value |
|-------|-------|
| Cloud reasoning tool (brief preparation, review) | Cowork (Claude) |
| Cloud reasoning tool (execution) | OpenAI Codex CLI |
| Local model | Not used for this run |
| Project layer | 7 SustainDev files (~3,920 words total) authored in the project's primary language |
| Existing CLAUDE.md | Migrated from monolithic 159 lines to 48-line thin adapter pointing at `PROJECT_CONTEXT.md` |
| Hero workflow stage used | `idea-to-prepared-task` from capture through completed |
| Verify command | `mise exec dotnet@8 -- dotnet build` + `dotnet test --filter`  |

## Phase Timing

| Phase | Wall-clock | Owner | Notes |
|-------|-----------|-------|-------|
| Capture idea | ~30 s | Cowork | Hand-written stub; `capture-idea.sh` not invoked because the script hardcodes `core/scheduling/queue/...` paths that conflict with project namespace. The dogfood uses `.sustaindev/queue/...` instead. v0.2 priority: configurable queue root. |
| Lookup existing state | ~2 min | Cowork | Read `CODEMAP.md`, located the existing test file, read the converter source. Caught two latent issues (next section). |
| Identify gap categories | ~5 min | Cowork | Reviewed 449 lines of existing tests against 95 lines of converter source. Identified 6 gap categories spanning 10 candidate tests. |
| Prepare brief | ~7 min | Cowork | ~1,200-word `scheduled-task` brief. The most expensive Cowork phase. v0.2 priority: `prepare-task.sh` to scaffold the brief from the captured stub + project layer files. |
| Hand to Codex | ~1 min | User | Pasted the prompt into Codex CLI on the user's Mac. |
| Codex execution (round 1) | within 35 min | Codex | Added 11 tests, hit a pre-existing test failure during verify, escalated cleanly without guessing. |
| Cowork diagnosis + authorize fix | ~5 min | Cowork | Walked through the regex behavior, confirmed the bug, sent a one-line authorization. |
| Codex execution (round 2) | within 35 min | Codex | Applied the fix, committed on a single branch with one squash-style commit, filled retrospective, moved brief to completed queue. |
| Cowork verify + measurement | ~5 min | Cowork | Diff inspection, retrospective read, branch-ancestry analysis (which surfaced the uncommitted-work finding). |
| **Cowork-side total** | **~25 min** | | Brief preparation + diagnosis + verification. |
| **Codex-side total** | **~35 min** | | Both rounds combined; reported by Codex. |
| **Combined wall-clock** | **~60 min** | | First-real-task dogfood, end-to-end. |

## Token Counts

Honest accounting of what we know and what we don't.

| Phase | Cowork tokens (estimated) | Codex tokens (reported) | Local model | Notes |
|-------|---------------------------|-------------------------|-------------|-------|
| Capture | ~0 | 0 | 0 | Hand-written stub. |
| Lookup | ~3,000 | 0 | 0 | Test file (449 lines) + converter (95 lines) + project layer files + the existing legacy CLAUDE.md. |
| Identify gaps | ~1,500 | 0 | 0 | Categorize gaps. |
| Prepare brief | ~2,500 | 0 | 0 | ~1,200-word brief produced. |
| Codex round 1 | 0 | not reported | 0 | Codex CLI does not expose token counts. Estimated 5,000–15,000 from observed work (read brief + 7 project files + test file + converter source, generated 11 tests). |
| Cowork diagnosis | ~2,000 | 0 | 0 | Read failing test context, walked through regex, wrote follow-up. |
| Codex round 2 | 0 | not reported | 0 | Estimated 1,000–3,000 (one-line edit + retrospective fill + git operations). |
| Cowork verify | ~1,500 | 0 | 0 | Diff inspection + retrospective read + branch ancestry. |
| **Cowork total** | **~10,500** | 0 | 0 | All Cowork numbers are estimates; the platform does not expose per-call counts to the agent. |
| **Codex total** | 0 | **not reported** | 0 | Estimated 6,000–18,000 based on observed work shape. |
| **Combined estimate** | | | | **~16,500 – 28,500 cloud tokens** total. The wide range reflects that Codex side is opaque. |

## Counterfactual: Without SustainDev

A naive "please add unit tests for the markdown-to-inlines converter" prompt to Codex would likely have produced a redundant batch (the existing 25 tests are on disk but stale plan listed the task as not-yet-started), with a merge conflict at commit. The pre-existing test bug would have stayed latent, and the 50+ uncommitted files would not have been surfaced. Estimated cost: ~10,000–20,000 cloud tokens, ~30 min wall-clock, low-confidence output.

The SustainDev path took longer (~60 min vs ~30 min) and slightly more tokens (~16,500–28,500 vs ~10,000–20,000) but produced demonstrably more durable value: 11 new tests, 1 pre-existing bug fixed, latent uncommitted work surfaced, clean retrospective trail, three evidence-backed v0.2 priorities. The honest framing is "more tokens for more durable output", not "fewer tokens on every run."

## Findings

### 1. The lookup discipline caught three latent issues in 30 seconds

Reading `CODEMAP.md` and the existing test file before writing the brief surfaced:

- The project's plan file listed the task as not-yet-started; the task was actually complete in a prior sprint (the existing 25 tests already existed).
- Those existing 25 tests were on disk only — never committed to any branch.
- One of the existing tests had a wrong count assertion that had been latent since it was written.

None of these would have been caught by sending Codex a naive "please write tests for X" prompt. The lookup phase took ~2 minutes; the avoided rework would have cost ~30 minutes plus merge friction.

### 2. `prepare-task.sh` is now empirical priority for v0.2

Brief preparation took ~7 minutes — the largest single Cowork-side cost in the workflow. The hero `SKILL.md` references a `prepare-task.sh` that takes a captured idea + project context + codemap and produces a structured brief, but the script was not in v0.1's deliverables. Hand-preparation worked but was the bottleneck. A working `prepare-task.sh` invoking a local model on the captured stub plus the project layer files would plausibly handle 60–70% of brief drafting, leaving Cowork to polish. This task class (idea expansion: rough capture → structured task brief) is exactly the strong-fit row in `core/rules/model-routing.md`.

### 3. The "do not modify existing tests" constraint was too rigid

The brief said `do NOT modify existing 25 tests`. Codex hit a pre-existing test with a wrong count assertion and escalated cleanly. That escalation was the right behavior, but the brief language was the wrong cause for it — a one-line typo fix is not the same as changing test behavior. The right wording for v0.2 brief templates: *"the behavior expressed by existing tests is sacred; trivial fixes to obvious bugs are permitted, must be explicitly noted in the retrospective."*

### 4. Codex's stop-at-ambiguity discipline is the most valuable agent behavior we observed

When the failing test surfaced, Codex did not guess, did not delete the failing test, did not modify the production converter to match the test, and did not push partial work. It stopped, reported the situation, and waited for an authorization. This is the agent calibration the SustainDev workflow assumes. The review pattern rewards it; ad-hoc "ship it anyway" pressure punishes it. v0.2 brief templates should encourage this behavior explicitly, and the `sprint*-review.md` should credit it when observed.

### 5. The project layer paid off immediately

`CODEMAP.md` pointed Codex at the test file's exact location. `MAINTAINABILITY_NOTES.md` informed the test-style conventions (Arrange-Act-Assert, FluentAssertions, section headers with box characters). `AI_POLICY.md` made clear which files were in scope. Without these files, Codex would have had to discover the conventions by scanning — costing extra tokens and introducing inconsistency risk. The cost to author these files (~3,920 words across 7 documents, ~90 minutes of Cowork time) is amortized across every future task on the project.

### 6. Migrating CLAUDE.md to a thin adapter worked

The original `CLAUDE.md` was 159 lines of dense session-log content mixed with project context. After migration, it is a 48-line thin adapter pointing at the SustainDev project files. Codex (and any future Claude Code session) reads the lean adapter first and follows pointers to the file relevant to the current task — instead of paging through historical session notes that are mostly irrelevant. Net: more total content (project layer files plus thin adapter) but split by concern, so the per-task read cost is lower.

### 7. The `"****"` regex finding is a real surprise documented as a test

The brief expected `"****"` to be plain text because the bold regex requires at least one captured character. Codex implemented the test, ran it, and found the actual converter behavior is different: the italic regex falls through and matches `"*"` as italic content, leaving a trailing plain `"*"`. Codex documented the observed behavior per the brief's policy ("document observed, not desired"). The new test now locks in this edge case, so future regex changes can't silently break the fallback. This is exactly what edge-case test gap-fill is supposed to do.

### 8. Brief preparation is the most expensive phase for the cloud reasoning tier

~7 minutes of Cowork time (~2,500 tokens estimated) went into the brief. Everything downstream (Codex's execution, the diagnosis round, the verify) was cheaper per minute. That makes brief preparation the right place to invest more tooling: a `prepare-task.sh` that does 60–70% of the structural work (file targets, verify commands, scope from `MAINTAINABILITY_NOTES`) saves the most expensive minutes. v0.2 should ship this.

### 9. The hero workflow lifecycle worked end-to-end

`captured/` → `scheduled/` → `completed/` lifecycle, each transition tracked with timestamps in front matter, retrospective filled in at completion, brief moved to `completed/` as the final step. No gaps in the lifecycle. The structure held under real use.

### 10. The dogfood surfaced a much larger uncommitted-work problem

Investigating why the test file showed up as 615 added lines on Codex's commit (rather than ~166 lines for the additions only) revealed that the file had never been committed at all — the 25 existing tests lived on disk only. Following that thread further revealed >50 uncommitted source files in the project: most of the .NET Models, Services, ViewModels, Views, Converters, and the AI infrastructure scaffolding from a previous sprint were never committed to any branch. The SustainDev workflow did not directly fix this, but its discipline (run the verify suite, track the diff, follow the branch ancestry) made the issue visible. Without it, the latent uncommitted state could have remained hidden until a hardware loss made it irrecoverable. This is a separate cleanup task for the project owner, but the dogfood's contribution is making the problem visible.

## What This Does Not Prove

One task class (edge-case test gap-fill) on one project (a .NET 8 Avalonia desktop app) using one cloud executor (Codex CLI). The local-prework tier was not used. The eight other strong-fit task classes from the routing matrix remain untested. Other cloud executors and other project types were not tested.

Credibly evidenced: the hero workflow's lifecycle works on a real task, the project layer reduces discovery cost, the lookup-before-delegate discipline catches latent issues, and brief preparation is the workflow's biggest single cost.

## Reproducibility

An independent reproducer needs: a real project with at least 5 source files + a test suite + a project plan; the SustainDev v0.1.1 release; a cloud-reasoning tool for brief preparation; a separate cloud-execution tool; ~60 min of focused time. Quantitative numbers vary with hardware, latency, model version, and project size. Order-of-magnitude reproducibility (Cowork ~20–40 min, Codex ~20–60 min, combined ~40–100 min for a 10-test gap-fill) is plausible.

## Sanitization Note

Project-specific names, technical specifics, and internal terminology are masked as `project-a` per the SustainDev sanitization convention. The findings are reported faithfully; only identifiers are abstracted. The real-name mapping is in `projects/.private-map.md` (gitignored).

## v0.2 Backlog Surfaced

Five priority items, evidence-backed by this run:

1. `prepare-task.sh` that uses a local model + project layer files to scaffold 60–70% of a brief from a captured stub. Targets the workflow's largest single cost.
2. Brief-template language softening: trivial fixes to existing tests/files permitted with retrospective notation.
3. Configurable queue root in the scheduling scripts so project-side adoption avoids namespace conflicts with the project's own `core/`.
4. Empirical fill-in of additional matrix rows — case-study-03 onward should target idea triage, codemap drafts, or summarization on the same project.
5. Document the agent-discipline-credit pattern (stop-at-ambiguity rewarded by review structure) as guidance for tools integrated with SustainDev.
