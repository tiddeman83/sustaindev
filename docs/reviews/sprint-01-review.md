# Sprint 01 Review

**Date:** 2026-04-26
**Reviewer pair:** Cowork (Claude) + human reviewer
**Sprint outcome:** Pass — all 16 deliverables accepted, ready for v0.1.0 tag.

## Sprint Scope

Sprint 1 was implemented as a multi-tool coordination experiment. Three AI tools — Claude Code, Codex, and Antigravity (Gemini-powered) — were each given a self-contained brief from `sprint1-handoff/` covering a non-overlapping subset of v0.1's remaining deliverables. Cowork's role was reduced to (a) preparing the briefs, (b) reviewing returned work against `sprint1-handoff/review-criteria.md`, and (c) integrating the results into a clean main history.

This sprint is also the raw material for case-study-02: the multi-tool coordination model is itself a workflow worth measuring.

## Ownership And Outcome

| File | Owner | Outcome |
|------|-------|---------|
| core/rules/maintainability.md | Claude Code | Pass |
| core/templates/project-context.md | Claude Code | Pass |
| core/skills/idea-to-prepared-task/SKILL.md | Claude Code | Pass |
| adapters/claude-code/CLAUDE.md.template | Claude Code | Pass |
| adapters/codex/AGENTS.md.template | Codex | Pass |
| core/templates/codemap.md | Codex | Pass |
| core/scheduling/templates/scheduled-task.md | Codex | Pass |
| core/scheduling/queue/{captured,prework-ready,scheduled,completed}/.gitkeep | Codex | Pass |
| scripts/schedule/capture-idea.sh | Codex | Pass — functionally tested |
| scripts/schedule/list-queue.sh | Codex | Pass — functionally tested |
| core/principles/development-principles.md | Antigravity | Pass with style note |
| core/rules/model-routing.md | Antigravity | Pass with style note |
| adapters/lm-studio/usage.md | Antigravity | Pass with style note |
| adapters/lm-studio/prework-prompt.md | Antigravity | Pass with style note |
| docs/measurement/methodology.md | Antigravity | Pass with strong style note |
| docs/measurement/case-study-01.md | Antigravity | Pass with strong style note |

Total: 16/16 pass. Zero rejected files. Zero rewrites required.

## Tool-By-Tool Findings

### Claude Code

**Excelled at.** Structural fidelity to the brief. The hero `SKILL.md` followed the YAML front matter convention exactly, the maintainability rule condensed the original twelve dimensions to six with principled merges, the project-context template included a sanitized worked example without prompting, and `CLAUDE.md.template` came in at 56 lines — well within the 30-80 range and fully referential. Voice matched the style anchor (`core/rules/token-efficiency.md`) closely.

**Struggled with.** Nothing meaningful. All four deliverables passed without comment.

**Voice signature.** Calm, instructional, second-person consistently. Felt like a sibling of the cloud-authored anchor file.

### Codex

**Excelled at.** Engineering discipline. When Codex hit a blocker (no `main` branch, no `origin` remote) it refused to make a root commit that would have mixed ownerships and instead documented the situation in `docs/reviews/sprint-01-blockers.md` with a recommended fix. That's correct behavior under uncertainty. Both shell scripts passed `sh -n` syntax checks and worked end-to-end on first try (capture, idempotency via `-2` suffix, listing, status filter, priority filter, JSON output). The codemap template's "200-line cap or it's a directory listing, not a codemap" framing was a small but valuable addition not in the brief.

**Struggled with.** Cross-tool consistency — `AGENTS.md.template` omits the `<project>/` prefix that `CLAUDE.md.template` uses, presumably because Codex assumed `AGENTS.md` always sits at project root. Defensible, but creates a stylistic inconsistency between the two adapter templates. Not blocking.

**Voice signature.** Terse, precise, engineer-first. The shell scripts are particularly clean.

### Antigravity (Gemini-powered)

**Excelled at.** Faithful translation of structured input into structured output. The strong-fit / weak-fit matrix in `model-routing.md` reproduces every row from `case-study-01-data.md` accurately, with the "Theoretical / Measured" evidence column intact — no overclaiming. The `case-study-01.md` reproduces the run-1 and run-2 metrics tables exactly and preserves the conservative cloud-savings figure (~700 tokens) without inflating it. The "What This Does Not Prove" section is intact.

**Struggled with.** Voice. Across all six deliverables, prose drifts heavily into adverbial padding and intensifier stacking — "rigorously", "absolutely", "definitively", "explicitly", "perfectly", "strictly", "fundamentally", "meticulously evolve to strictly mandate". The methodology document and case-study-01 are the most affected; in places, sentences become hard to parse because every noun and verb collects two or three modifiers. Content is correct; prose obscures rather than illuminates. This is the dominant style finding of the sprint.

**Voice signature.** Cinematic-trailer adjacent. Reads as if every claim is being defended against an imagined critic. Useful as a thoroughness signal; problematic as the project's measurement voice.

## Cross-Cutting Observations

**Voice drift between tools is real and visible.** Claude Code, Codex, and Antigravity each produced internally consistent prose that reads as a different author. Style anchors (referencing `core/rules/token-efficiency.md` in every brief) reduced drift but did not eliminate it. For v0.2, the briefs should include 2-3 sentences of the anchor file as direct examples ("write like this") rather than relying on a reference link.

**Self-contained briefs worked.** No tool asked clarifying questions during execution. Antigravity used the Gemini-chat fallback path (per the PR description it noted) and the brief was structured well enough to support that mode.

**The shell scripts shipped on first attempt** — Codex's combination of POSIX discipline, explicit error codes, and `set -eu` paid off. The codemap and scheduled-task templates also shipped without iteration. The skills layer (`core/skills/idea-to-prepared-task/SKILL.md`) shipped without iteration.

**Prose-heavy files were the rework risk** — Antigravity's six files are the entire pool of style-noted deliverables. This suggests that prose review pass should be more rigorous in v0.2 if Antigravity continues to own measurement and routing docs.

## Multi-Tool Coordination Cost vs Single-Author Counterfactual

If Cowork had authored Sprint 1's 16 deliverables solo using Claude Sonnet 4.6, estimated cost would be ~30,000-50,000 cloud tokens and ~3-5 hours wall-clock. The actual multi-tool sprint distributed authorship across three tools and three providers, with Cowork's role reduced to brief-writing, review, and integration.

Honest accounting:

- Cowork brief preparation: ~12,000 tokens (estimated, not measured in case-study-02 yet).
- Per-tool execution: not measured in this sprint. Each tool's session was opaque to Cowork.
- Cowork review pass: ~6,000 tokens (16 file reads + commentary, this document).
- Cowork integration (git history reorganization): ~2,000 tokens.

**The sprint did not produce a measurement on whether the multi-tool model saved tokens or cost.** That is case-study-02's job — it requires running one or more comparable Sprint 1-equivalent tasks single-author and measuring honestly. Until then, the multi-tool coordination model is a hypothesis with positive qualitative signals (no rejections, no rewrites, audit trail preserved) but no quantitative evidence.

## Implications for v0.2

- Antigravity's voice problem is the single most actionable finding. v0.2 ownership for measurement and prose-heavy documents should either rotate to a different tool, or include a stricter style enforcement step in the brief (perhaps a "prose check" sub-pass).
- Codex's adapter omitted the `<project>/` prefix; for v0.2, brief should explicitly require alignment between `AGENTS.md.template` and `CLAUDE.md.template` so cross-tool examples don't diverge stylistically.
- The blocker-flagging behavior Codex demonstrated is exactly the right pattern. v0.2 briefs should explicitly invite this pattern in the "If something blocks you for more than 30 minutes" section — Codex was the only tool to use it productively this sprint.
- Briefs should embed style examples directly, not just reference the anchor. Three example sentences from `token-efficiency.md` pasted in each brief would have reduced Antigravity drift.

## Definition of Done

Sprint 1 is complete:

- All 16 ownership-table deliverables exist on `main`.
- Linear history: Sprint 0 → Antigravity → Claude Code → Codex commits, each attributable.
- Local CI checks pass (required-files, forbidden-names, SKILL.md schema, shell syntax, executability).
- `core/rules/token-efficiency.md` cloud-anchor unchanged.
- `docs/reviews/sprint-01-review.md` (this file) recorded.
- Ready for v0.1.0 tag and remote push.

## Open Items For v0.2

- Antigravity prose cleanup pass (every file the tool authored).
- AGENTS.md.template / CLAUDE.md.template stylistic reconciliation.
- case-study-02: measure the multi-tool coordination workflow itself against single-author cloud baseline.
- Empirical fill-in of the "Theoretical; not yet measured" rows in `core/rules/model-routing.md`'s strong-fit / weak-fit matrix. Idea triage and codemap-from-file-list are the most tractable next measurements.
- Warp and VS Code adapters per `docs/roadmap.md`.
