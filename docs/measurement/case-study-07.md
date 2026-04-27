# Case Study 07: Risk Extraction — The First Unconditional Strong-Fit Since Idea Expansion

**Run date:** 2026-04-27
**Project:** project-a (a .NET 8 Avalonia desktop app, ~v0.0.7 internal POC)
**Workflow:** `scripts/sprint1/extract-risks.py` (one-shot probe, first to use `scripts/lib/postprocess` from v0.1.6)
**Tools:** Qwen 3.5 9B at MLX 4-bit running locally in LM Studio on Apple Silicon (16-24 GB unified memory)
**Task class tested:** **Risk extraction from existing prose** — the fifth strong-fit row from the routing matrix.

## Summary

Risk extraction is the cleanest local-tier run of the v0.1.x series. The model read a small mixed-prose document (~3 KB / 800 tokens) listing known issues with severity tags in Dutch, and produced a structurally-correct markdown table with severity-mapped, language-preserved entries — in 193 seconds, with no defensive intervention needed from the v0.1.6 post-processing module. Arithmetic was correct on the first try (claimed `total=6`, actually 6 rows), severity tags were mapped accurately across languages (Dutch "Laag"/"Informatief" → script's `laag`/`info` scale), and resolved issues from a separate section of the source were correctly excluded from the active list.

This is the **second unconditional strong-fit row** in the matrix (after idea expansion in case-study-03). Six rows are now empirically backed; three are conditional, two are unconditional, one is weak fit. A pattern emerges: the unconditional strong-fit rows are characterized by **small bounded inputs producing small bounded structured outputs from project-aware context**. When all three conditions hold, the model packages cleanly without intervention.

## What Was Tested

A real, useful task on a real project: extract a structured risk catalog from a known-issues document. The source mixed open issues, resolved issues (in separate sections by version), severity tags in Dutch ("Laag", "Informatief"), and free-prose descriptions plus mitigation notes.

Expected output: a markdown table with columns `ID | Title | Severity | Description | Mitigation`, severity normalized to a configurable scale (here Dutch: `hoog,middel,laag,info`), with the model judging which scale value best matches each source severity tag.

## Setup

| Field | Value |
|-------|-------|
| Local model | Qwen 3.5 9B at MLX 4-bit |
| LM Studio context length | 16,384 |
| Source document | known-issues markdown, ~3 KB / 794 tokens |
| Target output | markdown table, max 30 rows, severity scale `hoog,middel,laag,info` |
| Temperature | 0.2 |
| Max tokens | 3,000 (default for the script; bounded structured output doesn't need 8k) |
| Probe script | `scripts/sprint1/extract-risks.py`, first probe authored against `scripts/lib/postprocess` |

## The Run

```text
Calling LM Studio (qwen/qwen3.5-9b) to extract risks from known-issues.md...
(prompt ~341 tokens)
Done. wall_clock=192.8s tokens=4210 input_chars=3018 reasoning_chars=8766 output_chars=1526
```

| Metric | Value |
|--------|-------|
| Wall-clock | 192.8 s |
| Prompt tokens | 1,298 |
| Completion tokens | 2,912 |
| Total tokens | 4,210 |
| Reasoning chars (channel) | 8,766 |
| Output chars (visible) | 1,526 |
| Reasoning ratio | ~85% |
| Fallback used | False (visible content channel had real content) |
| Postprocess notes | None (the v0.1.6 defensive code didn't fire) |
| Hallucinated facts | 0 |
| Severity-mapping errors | 0 |
| Arithmetic errors | 0 (counts line was correct) |

## Quality Assessment

**Coverage: exact.** The source had 6 active issues in its "Openstaand" section and additional resolved issues under "Opgelost in v0.0.7" and "Opgelost in v0.0.6". The model produced exactly 6 rows, matching the active issues. The resolved sections were correctly excluded — this requires document-structure understanding, not just naive line-by-line extraction.

**Severity mapping: clean across languages.** The source uses Dutch severity tags ("Laag", "Informatief"). The script asked for the scale `hoog,middel,laag,info`. The model correctly mapped: 5 source-`Laag` → output `laag`, 1 source-`Informatief` → output `info`. No hallucinated `hoog` or `middel` entries to inflate severity. The mapping is honest to the source.

**Title quality: faithful.** Each row's title preserves the source's phrasing ("Excel-template stijlcheck kan afwijken", "Recovery-bestand op Windows als verborgen bestand", etc.) — Dutch domain language preserved, abbreviations and technical terms intact.

**Description quality: condensed but accurate.** Each description is one or two sentences capturing the source's risk explanation. No invented technical details. The description for the recovery-files-on-Windows row correctly captures the punctuation-prefix nuance from the source. The description for the Avalonia 11 markdown converter correctly captures the attached-property-property-vs-direct-binding distinction.

**Mitigation handling: honest about absence.** Two rows had no mitigation in the source. The model correctly emitted `(geen mitigatie genoemd)` rather than inventing a mitigation. This was instructed in the prompt; the model honored the instruction.

**Counts line: correct.** `Counts: hoog=0, middel=0, laag=5, info=1 (total=6)`. The model's arithmetic matched the actual table. This is the first case study where the model's self-reported counts were verified to be correct without post-processing intervention.

**One judgment call:** the source uses ID format `KI-001` through `KI-009` ("Known Issue" prefix). The probe's prompt asked for `R-NN` format. The model went with the prompt's format (`R-01` through `R-06`). This is consistent compliance, not a flaw.

## What Made This Run Different

Comparing case-study-07 to the four prior measured strong-fit / conditionally-strong rows:

| Metric | CS-03 (idea expansion) | CS-04 (triage) | CS-05 R2 (catalog) | CS-06 R2 (summary) | CS-07 (risks) |
|--------|------------------------|----------------|---------------------|---------------------|----------------|
| Verdict | Strong | Conditional | Conditional | Conditional | **Strong** |
| Wall-clock | 114 s | 271 s | 475 s | 299 s | **193 s** |
| Reasoning ratio | 15% | 50% | 68% | ~50% | 85% |
| Fallback triggered? | No | No | No | Yes | No |
| Postprocess intervention? | n/a | Counts recomputed | Dedupe ran | Last-draft extracted | None |
| Arithmetic claim correct? | n/a | No (73 vs 80) | n/a | n/a | **Yes** |
| Hallucinations | 0 visible | 0 | 0 | 0 | 0 |
| Conditions for clean fit | None | Rich context (RISKS.md needed) | Sufficient max_tokens | Post-processing required | **None** |

The reasoning-ratio of 85% is the highest of any measured run — the model thought heavily for a relatively small output. But the per-output-token quality was the highest. **Reasoning was used productively, not as overflow.** That distinction matters.

## Why The v0.1.6 Module Was Idle

`postprocess_notes: []` and `fallback_used: false` mean the script imported the shared utilities but didn't call any of their defensive logic. This is the right behavior. Defensive code that fires when needed and stays out of the way when the model behaves cleanly is the design intent.

This validates the v0.1.6 consolidation: the post-processing pattern is *available* via `import postprocess` and *invoked conditionally* via if-guards. When the model emits clean output (as here), the user gets exactly what the model produced — no spurious modification, no silent edit. When the model misbehaves, the same code intervenes automatically.

The probe scripts now feel like surgical tools: tight on the happy path, robust on the unhappy path.

## What Risk Extraction Tells Us About The Pattern

Across seven case studies, the unconditional strong-fit rows share a profile:

1. **Bounded input.** The source document is small (case-study-03's captured stub: ~100 tokens; case-study-07's known-issues: ~800 tokens). The model holds the whole input comfortably in attention without needing to chunk or skip.
2. **Bounded structured output.** The output format is structured (a brief in case-study-03, a table in case-study-07) with a known schema and a known maximum size. The model knows when it's done.
3. **Rich project context.** Both runs had the project's PROJECT_CONTEXT.md and CODEMAP.md in scope (case-study-07 didn't load them explicitly but the document's prose contained enough project context). The model produces project-aware output, not generic LLM filler.

When all three hold, the model produces clean output the first time, the post-processing module stays idle, and triage time is low (~5 minutes for case-study-07: skim the table, confirm severities, decide whether to keep the model's R-NN IDs or revert to the source's KI-NNN format).

When any of the three breaks down (case-study-04: large input list breaks "bounded"; case-study-05: unbounded per-item depth breaks "bounded output"; case-study-06: very large input + unbounded depth break both), the row becomes conditionally strong. The conditions are predictable from the input/output shape.

## Strong-Fit / Weak-Fit Matrix Update

Six of ten rows now empirically backed:

| Task class | Fit | Why | Evidence |
|------------|-----|-----|----------|
| **Risk extraction from existing prose** | **Strong** | Bounded input, bounded structured output, project-aware context. Clean packaging on first try, no defensive intervention needed, arithmetic correct, severity mapping clean across languages. | **Measured in `docs/measurement/case-study-07.md` (this document).** |
| Idea expansion: rough capture → structured task brief | Strong | Hero-workflow centerpiece. | Measured in case-study-03. |
| Idea triage / classification | Conditionally strong | Needs rich context; spot-check on edge cases. | Measured in case-study-04. |
| Codemap drafts from file lists | Conditionally strong | Needs sufficient `--max-tokens`. | Measured in case-study-05. |
| Summarization of long documents | Conditionally strong | Packaging unreliable; recovery requires post-processing. | Measured in case-study-06. |
| Batch / overnight prework | Strong | Wall-clock cost is zero. | Implicit from CS-03/04/05/06/07. |
| Full-document drafting from rich brief | Weak | Reasoning overhead + wall-clock cost. | Measured in case-study-01. |
| Adapter templates | Weak | Tool-specific knowledge. | Theoretical; not yet measured. |
| Cross-document consistency checks | Weak | Wall-clock penalty too high. | Theoretical; not yet measured. |
| Time-critical authoring | Weak | User is waiting. | Implicit from case-study-01. |

Six of ten rows backed; two unconditional strong-fits, three conditional strong-fits, one weak. Three remaining theoretical rows.

## Findings

### 1. The v0.1.6 consolidation works as designed

The shared post-processing module was imported and available; its defensive functions stayed idle because the model packaged cleanly. This validates the consolidation pattern: defensive code that intervenes only when needed is the right shape. v0.1.6 turned out to be the right release for v0.1.x's architecture.

### 2. Cross-language severity mapping is clean

Dutch source severity tags ("Laag", "Informatief") were correctly mapped to the lowercase Dutch scale (`laag`, `info`). The model didn't try to translate to English or invent intermediate values. Severity scales in non-English projects work without modification — pass the right scale via `--severity-scale` and the model adapts.

### 3. Document structure understanding is functional

The source had separate sections for open and resolved issues. The model extracted only from "Openstaand" (open) and excluded "Opgelost in v0.0.7" / "Opgelost in v0.0.6" (resolved). This requires understanding markdown section structure, not just regex-matching for severity keywords. The model passed.

### 4. The reasoning-ratio is high but productive

85% reasoning vs 15% visible output is the highest reasoning ratio of any case study. But unlike case-study-04 (where 50% reasoning produced wrong arithmetic) or case-study-06 (where 50%+ reasoning produced empty visible content), the reasoning here resulted in clean accurate output. **Reasoning is not waste when the output it produces is right.** The "model uses all the budget" finding from case-study-05 still holds, but with a refinement: the budget can be used productively or unproductively.

### 5. Bounded input is the most reliable win condition

Risk extraction's input was 3 KB. Idea expansion's was even smaller. Both produced unconditional strong-fits. The conditional rows had larger or unbounded inputs (80 files, 12 service files, 40 KB document). When the input is small enough to hold comfortably in attention, the model's output quality jumps.

### 6. Triage time scales with output complexity, not input complexity

Case-study-07's output has 6 rows; triage took ~5 minutes (mostly to verify the severity mapping was honest and decide whether to keep R-NN or KI-NNN IDs). Case-study-04's output had 80 rows; triage took ~30+ minutes. The relationship is roughly linear in output rows, not in input size.

### 7. The probe-script template is now stable

`extract-risks.py` was the seventh probe script written from scratch using the v0.1.6 shared utilities. It's the cleanest of the seven — no special cases, no script-local defensive logic, just the standard pipeline (read input, build prompt, call model, post-process, write outputs). Future probe scripts can follow this template and ship in ~30 minutes of focused work.

## What This Does Not Prove

One short document (~3 KB) on one project on one model. Specifically:

- Larger source documents (>10 KB) with embedded risks were not tested. Whether risk extraction holds up when the source is, say, an entire RFC or design doc is unmeasured.
- Mixed-source extraction (multiple files in one prompt) was not tested.
- English-language sources were not tested.
- Other severity scales (numeric, custom) were not tested beyond the four-value ordinal scale.

What is credibly evidenced: at this hardware tier, with this model, on a small bounded prose document with explicit severity signals, risk extraction is an unconditional strong-fit task class. The probe script handles it cleanly, the post-processing module stays idle, and the output is usable as-is or with ~5 minutes of human triage.

## v0.2 Backlog Updated

Three priorities surfaced or clarified:

1. **Test risk extraction on a larger document.** RFC-sized inputs (10-30 KB) are the natural next test. If the unconditional fit holds, risk extraction becomes one of the most reliable local-tier tasks.
2. **Document the "unconditional strong-fit profile"** in `core/rules/model-routing.md` — bounded input + bounded structured output + project-aware context = clean fit. Future routing decisions can match new tasks against this profile.
3. **case-study-08 candidate: adapter templates.** The next theoretical weak-fit row to validate. Tests the prediction that tool-specific knowledge that 9B-class models often hallucinate produces unusable output. Confirming a weak-fit row is just as valuable as confirming a strong-fit row.

## What Got Confirmed

The v0.1.6 consolidation paid off on the first new probe written against it. Six of ten matrix rows now have empirical backing. The pattern across measured rows is consistent enough to predict the remaining four with reasonable confidence — but predicted is not measured, and v0.2 will continue filling in rows one at a time. The unconditional strong-fit profile (bounded input + bounded structured output + project-aware context) is a useful generalization for routing decisions on new task classes.
