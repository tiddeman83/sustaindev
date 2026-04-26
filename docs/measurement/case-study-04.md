# Case Study 04: Idea Triage Is Conditionally Strong-Fit

**Run date:** 2026-04-26
**Project:** project-a (a .NET 8 Avalonia desktop app, ~v0.0.7 internal POC)
**Workflow:** `scripts/sprint1/triage-files.py` (overnight idea-triage probe)
**Tools:** Qwen 3.5 9B at MLX 4-bit running locally in LM Studio on Apple Silicon (16-24 GB unified memory, 16k context)
**Task class tested:** **Idea triage / classification** — the second strong-fit row from the routing matrix in `core/rules/model-routing.md`

## Summary

The local-prework tier classified 80 untracked-or-modified files into four buckets (commit-now, review-first, archive, build-artifact) in **271 seconds (3.4 s/file)** with **zero hallucinations**: every input file appeared exactly once in the output, no invented files, no merged rows. Strict classification accuracy was **~89%** (71 of 80 correct). Two systematic errors surfaced: (1) the model failed to flag any file for human review despite the project having clearly-marked high-risk files in `RISKS.md` — RISKS.md was not in the prompt context, and without it the model defaulted to confident "commit-now" classification; (2) all five "build-artifact" classifications confused transient queue contents with the `.gitkeep` files inside them, which are explicitly meant to be committed.

The verdict: idea-triage is **conditionally strong-fit**. Strong fit when rich context (including risks and maintainability notes) is provided and the human accepts that ~5–10% of classifications need spot-check correction. Not strong-fit when the prompt context is too lean or when downstream consumers trust the output without sampling. This is the third matrix row to receive empirical evidence; it's also the first row where the verdict comes with conditions rather than a clean pass.

## What Was Tested

The captured idea: classify the 80 untracked + modified files in the project's `git status` into buckets that map to commit hygiene. Bucket definitions in the prompt:

- **commit-now** — clearly belongs in the next commit; obvious value, low risk.
- **review-first** — touchpoints, scope ambiguity, or risk; needs human eyes before commit.
- **archive** — outdated, superseded, or no longer relevant.
- **build-artifact** — generated, regenerable, or vendored; should be gitignored.

The script (`scripts/sprint1/triage-files.py`, shipped post-v0.1.2) ran `git status --porcelain=v1`, took the first 80 entries (the project actually had 100; the script's `--max-files=80` default truncated), loaded `PROJECT_CONTEXT.md` and `CODEMAP.md` as context, and asked the local model to produce a markdown table with bucket + one-line rationale per file.

Notably, `RISKS.md` and `MAINTAINABILITY_NOTES.md` were **not** in the prompt context. The script's default loads only the two files we expected to be most useful for classification. This turned out to be a meaningful design error.

## Setup

| Field | Value |
|-------|-------|
| Local model | Qwen 3.5 9B at MLX 4-bit |
| LM Studio context length | 16,384 (after the lesson from case-study-03) |
| System prompt | `/no_think` + bucket definitions + output rules (markdown table + counts line) |
| User message | `PROJECT_CONTEXT.md` + `CODEMAP.md` + the 80-file list |
| Temperature | 0.2 |
| Max tokens | 4,000 |

## The Run

```text
WARNING: File count (100) exceeds --max-files (80); truncating to first 80.
Calling LM Studio (qwen/qwen3.5-9b) to triage 80 files...
Done. wall_clock=271.7s tokens=7333 files=80 reasoning_chars=7588 output_chars=8165
```

| Metric | Value |
|--------|-------|
| Wall-clock | 271.7 s |
| Per-file wall-clock | 3.4 s |
| Total tokens | 7,333 |
| Reasoning chars (discarded) | 7,588 (similar to case-study-03; `/no_think` reduced but did not eliminate) |
| Output chars | 8,165 (~1,400 words for a structured table) |
| Throughput | 27 tok/s |
| Cost | $0 |

## Quality Assessment

### Coverage: 80 / 80 inputs accounted for, exactly once

This is the first headline result. Comparing the input file list (sorted) against the file column of the output table (sorted) showed **zero diff** — no missing files, no hallucinated files, no duplicates. Every input file appeared exactly once with exactly one bucket and exactly one rationale. For an 80-row structured-output task on a 9B local model, this is meaningful: the model held coherence across the full 4,000-token completion.

### Classification accuracy: ~89% strict

Detailed accuracy by bucket:

| Bucket | Count | Estimated correct | Notes |
|--------|-------|-------------------|-------|
| commit-now | 65 | ~61 | Four files that should have been review-first per the project's RISKS.md were classified commit-now. |
| review-first | 0 | 0 | Should have been ~4-5. RISKS.md wasn't in the prompt context. |
| archive | 10 | 10 | All ten are clearly outdated planning docs, completed sprint task assignments, or explicitly superseded files. The model recognized "old plan/review/extraction" patterns reliably. |
| build-artifact | 5 | 0 | All five are project-internal queue-and-measurement directories. The model classified them as transient/regenerable — partially right about runtime contents, but the directory entries themselves (and the `.gitkeep` inside one) are intentionally tracked. |

Strict accuracy: **~71 / 80 = 88.75%**. Lenient (forgiving the build-artifact directory confusion as partial truth): **~76 / 80 = 95%**.

### The four missed review-first calls

The project's `RISKS.md` lists these files as Hoog ernst (high severity) risks:

- The project's canonical Excel-cell-mapping module — silent-fail risk if modified incorrectly.
- The project's Excel I/O service — same risk class plus a cell-color detection convention.
- A persistence service with non-trivial threading (semaphore-serialized writes) — race-condition risk if modified.
- The orchestrating ViewModel — codemap explicitly flags it as "touch only with clear reason."

All four were classified as **commit-now** with rationales like *"Active hot spot per codemap"* or *"Active validation service, hot spot per codemap."* The model correctly identified them as hot spots — and then moved them to commit-now anyway, because nothing in the prompt told it to flag hot spots for review.

The missing context was `RISKS.md`. The model couldn't know these files had elevated risk profiles because the prompt only included `PROJECT_CONTEXT.md` and `CODEMAP.md`.

### The five build-artifact misclassifications

All five rows pointed at queue-and-measurement directories that are part of the SustainDev workflow's runtime structure:

- A measurement output directory — the directory itself contains evidence files that should be committed.
- Four queue subdirectories (captured, prework-ready, scheduled, completed) — three were directory listings, one was a `.gitkeep` file inside one of them.

The model's rationale for each was "Generated [X] queue, should be gitignored." This is partially right about transient runtime contents but wrong about the directories and the `.gitkeep` file itself, which are explicitly meant to be committed (that's literally what `.gitkeep` is for).

The miss is interesting: the model didn't know the `.gitkeep` convention well enough to recognize it as the deliberate "track this empty directory" marker. It clustered the entries by parent directory name and applied a "should be gitignored" rationale uniformly.

### The arithmetic error in the counts line

The model output one summary line: `Counts: commit-now=56, review-first=0, archive=12, build-artifact=5 (total=73)`.

Actual counts: `commit-now=65, review-first=0, archive=10, build-artifact=5 (total=80)`.

The model could classify accurately but could not reliably aggregate its own classifications. This is a known limitation of LLMs (counting items is generally a token-by-token operation that drifts) but it has a concrete consequence: **downstream consumers must recompute the totals; do not trust the counts line.** A v0.2 fix is straightforward — `triage-files.py` should parse its own output and recompute the counts in post-processing, replacing the model's claim with the verified count.

## Comparison to Case-Studies 01 and 03

The third data point in the matrix lets us compare across task classes on the same hardware tier:

| Metric | case-study-01 (full doc draft) | case-study-03 (brief expansion) | case-study-04 (idea triage) |
|--------|-------------------------------|-------------------------------|-----------------------------|
| Task class verdict | Weak fit | Strong fit | **Conditionally strong fit** |
| Wall-clock | 215 s | 114 s | 271 s |
| Per-unit-of-output | 215 s / 1 doc (incomplete) | 114 s / 1 brief | 3.4 s / file (80 files) |
| Total tokens | 4,096 (cap hit) | 7,504 | 7,333 |
| Reasoning chars | 12,111 (80% waste) | 1,188 (15% waste) | 7,588 (50% waste) |
| Useful output | ~300 words (incomplete) | ~750 words (complete + valid) | 80 classifications + miscounted total |
| Hallucinations | n/a | 0 visible at output time; 1 architectural mismatch surfaced at exec time | 0 |
| Accuracy | n/a (incomplete) | ~60% usable; ~95% recoverable through triage + execution | ~89% strict; needs context expansion to reach higher |

Three observations from this comparison:

The reasoning-char ratio scales with output structure. Case-study-03 (filling a structured template from rich context) had the lowest waste at 15%. Case-study-04 (producing 80 short rows) sat at 50%. Case-study-01 (free-form drafting) was at 80%. Structured tasks with rich context maintain `/no_think` discipline best; less-structured or sparser-context tasks let reasoning leak more.

The throughput-vs-quality tradeoff is real. Case-study-04 produced a row every 3.4 seconds; case-study-03 produced one structured brief in 114 seconds. The fast cadence in -04 is a strong-fit signal — but the per-classification accuracy ceiling is lower than the per-brief accuracy ceiling because each row gets less of the model's attention.

The "no hallucinations" finding in case-study-04 is the strongest defense the local tier has shown so far. Across 80 classifications produced in one shot, the model didn't invent a single file, didn't merge or duplicate any, and didn't drift the structure. This is the property that makes idea-triage genuinely useful at scale — even if individual classifications need spot-check, the bookkeeping is reliable.

## Strong-Fit / Weak-Fit Matrix Update

Three of ten rows now empirically backed:

| Task class | Fit | Why | Evidence |
|------------|-----|-----|----------|
| **Idea triage / classification** | **Conditionally strong** | Fast (3.4 s/file), zero hallucinations, accurate on clear cases. Needs rich context (RISKS.md + MAINTAINABILITY_NOTES) and human spot-check on edge cases. | **Measured in `docs/measurement/case-study-04.md`.** |
| Idea expansion: rough capture → structured task brief | Strong | Hero-workflow centerpiece; structured output from rich context. | Measured in `docs/measurement/case-study-03.md`. |
| Codemap drafts from file lists | Strong | Pattern extraction; benefits from large context window. | Theoretical; not yet measured. |
| Summarization of long documents | Strong | Output is bounded; plays to the 262k context window. | Theoretical; not yet measured. |
| Risk extraction from existing prose | Strong | Pattern-matching task. | Theoretical; not yet measured. |
| Batch / overnight prework | Strong | Wall-clock cost is zero. | Implicit from this case study (the run was overnight-shaped). |
| Full-document drafting from rich brief | Weak | Reasoning overhead + wall-clock cost outweigh cloud savings. | Measured in `docs/measurement/case-study-01.md`. |
| Adapter templates | Weak | Tool-specific knowledge that 9B-class models often get wrong. | Theoretical; not yet measured. |
| Cross-document consistency checks | Weak | Wall-clock penalty too high. | Theoretical; not yet measured. |
| Time-critical authoring | Weak | User is waiting; latency is unacceptable. | Implicit from case-study-01. |

The conditional language on idea-triage is honest framing. Two of three measured rows are clean wins; one is a win with attached conditions.

## Findings

### 1. Zero hallucinations on 80 structured outputs

The strongest single finding. Local model held coherence across 80 rows with no missing files, no invented files, no duplicates. This is the property that makes idea-triage usable at scale.

### 2. Counting arithmetic is unreliable

The model's reported total (73) was wrong by 7 against the actual count of 80. Bucket sub-counts were also off (commit-now claimed 56, actual 65; archive claimed 12, actual 10). LLMs counting their own outputs is a known weakness; the lesson for `triage-files.py` is to recompute counts in post-processing rather than trusting the model's summary line.

### 3. Without RISKS.md, the model defaults to confident classification

Zero rows landed in `review-first`, despite the project having clearly-flagged high-risk files. The model identified some as "hot spots" in its rationale and then classified them as commit-now anyway. Without explicit guidance that hot-spot status implies review-first, the model's prior is "if it looks active, commit it." Adding `RISKS.md` (and arguably `MAINTAINABILITY_NOTES.md`) to the triage-script default context is a v0.2 fix.

### 4. The `.gitkeep` convention is not common knowledge for the model

All five `.sustaindev/queue/...` rows were classified build-artifact, including a literal `.gitkeep` file. The model didn't recognize the convention that `.gitkeep` files are explicitly committed to track empty directories. This is a calibration gap that could be closed with one extra rule in the system prompt: *"`.gitkeep` files are always commit-now. Directory listings ending in `/` should be classified by likely contents, not by directory name alone."*

### 5. Reasoning-overhead scales inversely with task structure

`/no_think` reduced reasoning across all three case studies but never eliminated it. Reasoning-char ratios: 80% (case-study-01, free-form), 15% (case-study-03, structured fill), 50% (case-study-04, structured but unbounded list). The lesson for v0.2: tasks with both structure AND bounded length (case-study-03) get the best `/no_think` compliance. Lists that grow with input length (case-study-04) leak more reasoning, possibly because the model "thinks ahead" about the next rows.

### 6. Classifying 80 files in 4.5 minutes is genuinely useful at scale

Even with the accuracy gaps, having a first pass that correctly handles ~89% of files and does it in under 5 minutes for $0 changes the economics of "should I commit this branch?" workflows. The remaining 11% (mostly review-first omissions and the queue-directory confusion) become the human's targeted review list rather than the entire 80-file diff.

### 7. The `--max-files` default at 80 was too low

The project had 100 files in git-status; 20 got truncated. The cap exists to control prompt size for small contexts, but at 16k context the model could have handled all 100. v0.2: scale `--max-files` against `LM_STUDIO_CONTEXT` automatically, or chunk transparently and merge results.

## What This Does Not Prove

One run on one project on one model and hardware tier. Idea-triage is now empirically validated as conditionally strong-fit for this configuration. But:

- Other model sizes (smaller 7B, larger 14B / 32B) were not tested. Smaller models may not hold coherence across 80 rows; larger ones may have higher accuracy but slower wall-clock.
- Other project structures were not tested. A project with cleaner separation between source and runtime artifacts may produce higher accuracy than this project's `.sustaindev/queue/*` directory pattern.
- Other prompt designs were not tested. Adding `RISKS.md` to the context, or adding the `.gitkeep` rule to the system prompt, would likely move the strict accuracy from ~89% to ~95% — but this remains untested.
- The accuracy assessment relied on the case-study author's judgment of what each file "should" have been classified as. A different reviewer might disagree on edge cases.

What is credibly evidenced: idea-triage produces zero hallucinations on a 9B local model with structured-output prompting, runs at usable speed for batch/overnight work, and reaches ~89% accuracy without rich context — meaningful but not yet ready to trust without spot-check.

## Reproducibility

An independent reproducer needs:

- A real project with at least 50 modified-or-untracked files in git-status and a `PROJECT_CONTEXT.md` + `CODEMAP.md` describing it.
- The SustainDev v0.1.2+ release.
- LM Studio with Qwen 3.5 9B (MLX 4-bit) loaded at context length ≥ 8,192 (16,384 recommended).
- Apple Silicon at 16-24 GB unified memory or equivalent.
- ~5 minutes for the run plus ~30 minutes for accuracy assessment.

Quantitative numbers will vary with project size, project layer richness, model version, and hardware. Order-of-magnitude reproducibility (3-5 s/file, ~85-95% strict accuracy, zero hallucinations on a comparable sample) is plausible.

## v0.2 Backlog Updated

Six new evidence-backed priorities, layered on top of the case-study-03 backlog:

1. **`triage-files.py` should load `RISKS.md` and `MAINTAINABILITY_NOTES.md` by default.** This run's accuracy gap on review-first calls was directly caused by their absence. A small change to the script's `PROJECT_LAYER_FILES` list.
2. **Recompute counts in post-processing.** The model's counts line is unreliable; the script should parse its own output and replace the line with verified counts. Closes finding #2.
3. **Add `.gitkeep` semantics to the system prompt.** One sentence ("`.gitkeep` files are always commit-now; directory listings should be classified by likely contents") would close finding #4.
4. **Scale `--max-files` against `LM_STUDIO_CONTEXT`.** At 16k context the script under-served by capping at 80; with proper sizing, batches of 200-300 are feasible.
5. **Spot-check sampling feature.** `triage-files.py --sample-rate 0.1` would mark a random 10% of classifications for human review attention. Closes the "I shouldn't trust the output blindly" gap with a structural fix.
6. **case-study-05 candidate: codemap drafts from file lists** on the same project. Tests another row of the matrix. Smallest expected complexity after triage; should run cleanly given the lessons from this case study.

## What Got Confirmed

The local-prework tier really does work for short structured outputs at scale. Three case studies in, the picture is consistent: free-form drafting struggles, structured fill-in succeeds, structured-list-output is conditional. The matrix is starting to be a real decision tool.
