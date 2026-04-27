# Case Study 05: Codemap-Shape Drafting Is Conditionally Strong-Fit (Two Runs)

**Run date:** 2026-04-27
**Project:** project-a (a .NET 8 Avalonia desktop app, ~v0.0.7 internal POC)
**Workflow:** `scripts/sprint1/draft-catalog.py` (one-shot probe)
**Tools:** Qwen 3.5 9B at MLX 4-bit running locally in LM Studio on Apple Silicon (16-24 GB unified memory, 16k context)
**Task class tested:** **Codemap drafts from file lists** — the third strong-fit row from the routing matrix. Specifically: drafting a service catalog from interface source files.

## Summary

Two runs of the same task on the same hardware with the same prompt — only `--max-tokens` differed (4,000 vs 8,000). Run 1 hit the 4,000-token cap with reasoning leaking into visible output, producing 3 of 12 services and a partially-usable artifact. Run 2 with the larger budget produced **all 12 services in clean structurally-correct format with one duplicate row**. The catalog was triaged in ~10 minutes and saved as project-a's actual `SERVICE_CATALOG.md`.

The verdict: **conditionally strong-fit, like idea-triage, but conditional on a different variable.** Where idea-triage needed rich context to avoid undercalling review-first, codemap-shape drafting needs sufficient `max_tokens` budget to give reasoning and output room to coexist. Below the threshold (here, ~4k for 12 service files), reasoning leaks into visible output; above it (~8k), reasoning channels properly and the output is clean — at the cost of meaningful wall-clock and reasoning-token overhead.

## What Was Tested

A real, useful task on a real project: draft a service catalog from the project's interface files. Source: 12 `*Service*.cs` interface files under `src/`, totaling ~8,400 chars of source. Output: a markdown catalog matching the new `core/templates/service-catalog.md` template (per-service entries with file path, implementation path, DI scope, responsibility, public methods, depends-on, used-by, notes).

The dual-run experiment compared:

- Run 1: `--max-tokens 4000` (the script's previous default)
- Run 2: `--max-tokens 8000`

Same prompt, same input bundle, same model, same hardware. Single variable: output budget.

## Setup

| Field | Value |
|-------|-------|
| Local model | Qwen 3.5 9B at MLX 4-bit |
| LM Studio context length | 16,384 |
| System prompt | `/no_think` + bucket definitions + output rules + `.gitkeep` rule (v0.1.3) |
| User message | `PROJECT_CONTEXT.md` + `CODEMAP.md` + 12 interface files inline |
| Temperature | 0.2 |
| Max tokens (Run 1) | 4,000 |
| Max tokens (Run 2) | 8,000 |
| Filter | Interface files only (filename starts with `I` + uppercase second char), exclude tests/stubs/nulls |

## The Two Runs

### Run 1: 4,000-token cap

| Metric | Value |
|--------|-------|
| Wall-clock | 290.91 s |
| Prompt tokens | 4,933 |
| Completion tokens | 4,000 (cap hit) |
| Total tokens | 8,933 |
| Reasoning chars (channel) | 991 |
| Output chars | 15,097 |
| Throughput | ~14 tok/s |
| Services in catalog | 3 of 12 (truncated) |
| Reasoning leaked into visible output | Yes — extensive |

Run 1 stopped at the cap with reasoning visibly leaked into the output. Lines 14-148 of the markdown were the model's chain-of-thought ("I need to parse...", "Self-Correction on DI Scope...", "Wait, checking the instruction...") — not the catalog itself. The actual catalog content started at line 149 and produced 3 of 12 services before running out of budget. The artifact was unusable as a catalog but interesting as evidence.

### Run 2: 8,000-token cap

| Metric | Value |
|--------|-------|
| Wall-clock | 474.98 s |
| Prompt tokens | 4,933 |
| Completion tokens | 6,926 (under cap) |
| Total tokens | 11,859 |
| Reasoning chars (channel) | 18,887 |
| Output chars | 8,708 |
| Throughput | ~14 tok/s |
| Services in catalog | 12 of 12 |
| Reasoning leaked into visible output | None |

Run 2 produced a clean, complete catalog. Visible output contained no leaked planning. All 12 services appeared with correct file paths, correct method signatures, correct singleton DI scope (inferred from the project context), and notes that pulled relevant items from `MAINTAINABILITY_NOTES.md` (the input-cell write-skip rule on the data-IO service, the 26-validation-rule count, the file-picker method that case-study-03's hero-workflow execution introduced). One issue: one of the AI-suggestion service interfaces appeared twice with identical content — a single duplicate row.

## The Striking Finding: Reasoning Scales With Budget

Doubling the output budget did not just produce more output — it produced dramatically more reasoning:

| Metric | Run 1 (4k) | Run 2 (8k) | Change |
|--------|-----------|-----------|--------|
| Reasoning chars (channel) | 991 | 18,887 | **+1805%** |
| Output chars (visible) | 15,097 (with leaked reasoning) | 8,708 (clean) | -42% |
| Completion tokens | 4,000 | 6,926 | +73% |
| Wall-clock | 291 s | 475 s | +63% |

When the budget was tight, the model crammed reasoning into the visible output (because there was no room for it elsewhere). When the budget was generous, the model used the proper `reasoning_content` channel and used substantially more of it.

**The model used all the budget you gave it.** Whatever ceiling you set, the model thought up to it. `/no_think` reduced reasoning but did not suppress it; the model finds room for thinking somewhere — visible output if forced, the reasoning channel if given room. This pattern was implicit in earlier case studies (where reasoning waste varied from 80% in case-study-01 to 15% in case-study-03 to 50% in case-study-04) but case-study-05 makes it explicit: budget is a target, not a cap.

This has implications for sizing `--max-tokens` on every probe script. Setting it too low forces the model to leak reasoning into output. Setting it too high invites the model to over-think. The right value sits where reasoning channels properly but stays in proportion to the actual structured-output need.

## Catalog Quality (Run 2)

The 12 services produced were assessed against the actual interface files in the project. Findings:

**Method signatures: 12/12 correct.** Every method signature matched the source file exactly, including parameter types, return types, and optional parameters. The model parsed `Task<string?>`, `IEnumerable<T>`, `event Action?`, and properties (`{ get; }`) correctly without inventing or omitting members.

**Implementation paths: 0/12 correct.** All 12 entries said `(not in this bundle)` because only the interface files were sent. This is technically correct given the input — the model didn't hallucinate paths it couldn't verify. The triage step filled in the implementation paths from project knowledge. A v0.2 improvement: pass implementation files alongside interfaces so the model can fill these in.

**DI scope: 12/12 correct.** Singleton was inferred from `PROJECT_CONTEXT.md`'s explicit mention of `ServiceCollectionExtensions.the project's `Add*Services` DI extension()` registration as singleton. The model didn't hedge; it propagated the project-wide convention.

**Responsibility one-liners: 11/12 acceptable.** Each was under 25 words and described what the service does in routable terms. One was generic ("for AI integration"); the others were specific.

**Notes section: high quality.** Several notes pulled real content from `MAINTAINABILITY_NOTES.md`: the input-cell-only-write rule on the data-IO service, the 26-rule count on the validation service, the file-picker method on the file-dialog service that case-study-03 introduced. The model integrated context across files rather than treating each interface as standalone.

**Duplicate row: 1.** one of the AI-suggestion service interfaces appeared twice with identical content. Cause unknown — possibly a pause-and-restart in the generation, possibly a residual artifact of the reasoning-to-output transition. Trivial to detect and remove in post-processing; v0.2 backlog.

**No invented methods, no invented services, no invented file paths.** The 12 services correspond exactly to the 12 input files. The catalog stayed faithful to its source.

Estimated overall quality: **~95% usable as-is, recoverable to 100% with ~10 minutes of triage** (deduplication, implementation-path filling, two notes tightening, layer-grouping reorder).

## Comparison Across Three Local-Tier Strong-Fit Probes

The third matrix row joins idea-expansion (case-study-03) and idea-triage (case-study-04). Pattern is now visible across three task classes:

| Metric | Idea expansion (CS-03) | Idea triage (CS-04) | Catalog draft (CS-05 Run 2) |
|--------|------------------------|----------------------|------------------------------|
| Verdict | Strong fit | Conditionally strong | Conditionally strong |
| Wall-clock | 114 s | 271 s | 475 s |
| Total tokens | 7,504 | 7,333 | 11,859 |
| Reasoning chars | 1,188 | 7,588 | 18,887 |
| Reasoning ratio | 15% | 50% | 68% |
| Output usefulness | ~60% raw, ~95% triaged | ~89% strict | ~95% triaged |
| Hallucinations | 0 visible (1 architectural at exec) | 0 | 0 |
| Conditional on | Sufficient context | Rich context (RISKS.md needed) | Sufficient max_tokens budget |

The pattern: **structured-output tasks at this hardware tier produce zero hallucinations and high content quality, but reasoning overhead scales with task complexity.** Idea expansion (filling one structured template) was tightest at 15% reasoning. Idea triage (80 short rows) leaked to 50%. Catalog drafting (reading 12 files, producing 12 detailed sections) jumped to 68%. The local tier is honest — the model knows the answer; the cost is "thinking out loud" overhead that scales with how much is held in working memory.

## Strong-Fit / Weak-Fit Matrix Update

Four of ten rows now empirically backed:

| Task class | Fit | Why | Evidence |
|------------|-----|-----|----------|
| **Codemap drafts from file lists** | **Conditionally strong** | Zero hallucinations on 12 files, accurate signatures, correct DI scope, useful notes integration. Needs `--max-tokens` ≥ ~8k for 12 service files; reasoning consumes 50-70% of budget. | **Measured in `docs/measurement/case-study-05.md` (this document).** |
| Idea triage / classification | Conditionally strong | Fast, zero hallucinations. Needs RISKS.md + spot-check. | Measured in case-study-04. |
| Idea expansion: rough capture → structured task brief | Strong | Hero-workflow centerpiece. | Measured in case-study-03. |
| Summarization of long documents | Strong | Output bounded; benefits from large context. | Theoretical; not yet measured. |
| Risk extraction from existing prose | Strong | Pattern-matching task. | Theoretical; not yet measured. |
| Batch / overnight prework | Strong | Wall-clock cost is zero. | Implicit from CS-03/04/05. |
| Full-document drafting from rich brief | Weak | Reasoning overhead + wall-clock cost. | Measured in case-study-01. |
| Adapter templates | Weak | Tool-specific knowledge. | Theoretical; not yet measured. |
| Cross-document consistency checks | Weak | Wall-clock penalty too high. | Theoretical; not yet measured. |
| Time-critical authoring | Weak | User is waiting. | Implicit from case-study-01. |

The two strong-fit rows that ship cleanly (idea expansion) are tasks with fixed, bounded structured output. The two conditionally-strong rows (idea triage and codemap drafting) are tasks where output structure is bounded but per-item depth scales with input complexity.

## Findings

### 1. The model uses all the budget you give it

Doubling `--max-tokens` from 4,000 to 8,000 produced a 19× increase in reasoning tokens (991 → 18,887) and a 1.6× increase in wall-clock. Reasoning didn't just fit better; it expanded to use the available room. This pattern explains why earlier case studies showed varying reasoning ratios — they had different budgets relative to task complexity, not different model behaviors.

### 2. Below a threshold, reasoning leaks into visible output

When the output cap is too tight to hold both structured output AND reasoning, the model leaks reasoning into the visible response. This was Run 1's failure mode — the catalog truncated to 3 of 12 services because lines 14-148 were the model's planning text instead of catalog content. `/no_think` reduces but does not eliminate this; the directive shifts reasoning toward the proper channel when there's room, and toward visible output when there isn't.

### 3. Above the threshold, the visible output is clean and complete

Run 2 with 8k budget produced a properly structured 12-service catalog with no leaked planning. The reasoning went to the `reasoning_content` channel as designed and the visible markdown was usable as a draft. The threshold for this task with this hardware appears to be roughly 6,000-7,000 tokens; the script's previous default of 4,000 was below it.

### 4. The catalog content was high-fidelity

12 of 12 method signatures correct, 12 of 12 DI scopes correct, several notes that integrated context across `PROJECT_CONTEXT.md` and `MAINTAINABILITY_NOTES.md` rather than echoing surface details. Zero invented methods, zero invented services, zero invented file paths. The model is genuinely useful for code-structure summarization at this hardware tier, when given the budget to operate cleanly.

### 5. One duplicate row escaped post-processing

one of the AI-suggestion service interfaces appeared twice in Run 2's output. The script doesn't currently detect or merge duplicates. v0.2 backlog: add deduplication by service-name to `draft-catalog.py`'s post-processing, similar to the count recomputation added to `triage-files.py` in v0.1.3.

### 6. Implementation paths are missing because implementations weren't sent

The script's `find_interface_files` defaults to interfaces-only. The model correctly reported `(not in this bundle)` for all implementation paths rather than inventing them. To produce a complete catalog in one pass, future runs should send implementation files alongside (within budget). v0.2 improvement: a `--bundle-mode all|interfaces-only|interfaces-plus-tests` flag.

### 7. Wall-clock-per-output-token slowed at higher max_tokens

Throughput stayed at ~14 tok/s in both runs, but the larger budget meant Run 2 took 63% longer real time. For overnight or batch use this is fine; for interactive use, capping max_tokens at the smallest value that keeps reasoning channeled is the optimization.

### 8. Triage cost was meaningful but bounded

The catalog triage took ~10 minutes: deduplication (1 min), implementation-path fill (3 min), two notes tightenings (3 min), layer-grouping reorder (3 min). Faster than triage in case-study-03 (~15 min) because the structural quality of the input was higher. Catalog drafts may have a lower triage ceiling than brief drafts because the artifact format is more rigid.

## What This Does Not Prove

One project, one model, one hardware tier, one task variant within "codemap drafts from file lists." Specifically:

- Other source-code languages (TypeScript, Python, Go, Rust) were not tested. Languages with explicit type annotations may differ from those with inferred types.
- Larger interface bundles (50+ files) were not tested. The 8k cap held for 12 files; whether 16k holds for 50 files is unmeasured.
- Other models (smaller 7B, larger 14B-32B) were not tested. A 14B model may produce less reasoning per output token but slower wall-clock.
- The "codemap drafts from file lists" matrix row covers a broader class than just service catalogs. Other variants (route maps, dependency graphs, view→viewmodel maps) remain unmeasured.

What is credibly evidenced for this configuration: a 9B local model on Apple Silicon at 16-24 GB unified memory produces a structurally-clean, content-accurate service catalog from a 12-file interface bundle when given a sufficient (~8k) max_tokens budget, with one minor flaw (duplicate row) that post-processing can detect.

## Reproducibility

An independent reproducer needs:

- A real project with at least 8 service interface files (or analogous structural elements).
- The SustainDev v0.1.3+ release with `scripts/sprint1/draft-catalog.py`.
- LM Studio with Qwen 3.5 9B (MLX 4-bit) loaded at context length ≥ 16,384.
- Apple Silicon at 16-24 GB unified memory or equivalent.
- ~8 minutes for the run plus ~10-15 minutes for triage.

Quantitative numbers will vary with project size, source language, model version, and hardware. Order-of-magnitude reproducibility (8-10 min wall-clock at 8k budget, ~95% structural accuracy, zero hallucinations on signatures, 0-2 duplicate rows on a comparable bundle) is plausible.

## v0.2 Backlog Updated

Five new evidence-backed priorities, layered on top of the case-study-04 backlog:

1. **`draft-catalog.py` should default to `--max-tokens 8000` (or scale with prompt size).** The 4,000 default that shipped in v0.1.3 produced a truncated, leaked-reasoning result. New default: ~max(8000, max_tokens_estimated_from_prompt_complexity).
2. **Post-processing deduplication.** Detect repeated service entries by name and either merge or warn. Mirrors the count-recomputation pattern from `triage-files.py`.
3. **`--bundle-mode` flag.** Allow including implementations alongside interfaces (within budget) so implementation paths are filled. Default: interfaces-only for budget control.
4. **Document the "model uses all the budget" finding** in `core/rules/model-routing.md` or a new sidebar in `adapters/lm-studio/usage.md`. This is the single most actionable insight from this case study for future probe scripts.
5. **case-study-06 candidate: summarization of long documents.** The next strong-fit row to measure. Plays to Qwen's 262k context window strength. Use the project's largest documentation file as input; ask for a one-page summary. Measure whether reasoning overhead scales with input size or stays bounded.

## What Got Confirmed

The local-prework tier holds three concrete strong-fit-or-conditionally-strong-fit rows now: idea expansion, idea triage, and codemap drafts. Across all three, hallucination rates were low or zero. Across all three, the failure modes were budget-related or context-related rather than capability-related — the model knew the answer, the question was whether it had the room to express it cleanly. That's a routing-rule problem, not a model-capability problem, and the script-side fixes are bounded and shipping.

The matrix is real. Four of ten rows now have empirical backing. The pattern across them is consistent enough that the remaining six rows can be predicted with reasonable confidence — but predicted is not measured, and v0.2 should keep filling them in one case study at a time.
