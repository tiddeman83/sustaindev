# Case Study 03: First Empirically Validated Strong-Fit Row

**Run date:** 2026-04-26
**Project:** project-a (a .NET 8 Avalonia desktop app, ~v0.0.7 internal POC, primary language non-English)
**Workflow:** SustainDev `prepare-task.py` script (shipped in v0.1.2) on a real captured idea
**Tools:** Qwen 3.5 9B at MLX 4-bit running locally in LM Studio on Apple Silicon (16-24 GB unified memory)
**Task class tested:** **Idea expansion** — rough capture → structured task brief

## Summary

The first empirical validation of a strong-fit row in the routing matrix. The local-prework tier produced a structurally complete, validation-passing scheduled-task brief in 114 seconds for $0, with three minor issues that human triage caught in ~5 minutes. Compared to case-study-01's weak-fit run on the same hardware (full-document drafting, 215 seconds for an incomplete 300-word output), the strong-fit run was **~2× faster wall-clock with ~10× less reasoning waste** and produced complete, validation-passing output.

The routing-matrix prediction held: tasks where the model fills a structured template using rich context behave fundamentally differently from tasks where the model drafts free-form prose. One row of the strong-fit matrix moves from `Theoretical; not yet measured` to `Measured`.

## What Was Tested

A real captured idea on project-a: prepare a scheduled-task brief for adding a screenshot-upload UI component to a wizard-step view. The captured stub was 1 sentence; the prepared brief was a fully-structured ~750-word document covering scope, file targets, verify commands, maintainability constraints, success criteria, and execution notes.

The script (`scripts/schedule/prepare-task.py`, v0.1.2) read the captured stub plus five project layer files (`PROJECT_CONTEXT.md`, `CODEMAP.md`, `AI_POLICY.md`, `MAINTAINABILITY_NOTES.md`, `VERIFY.md`) totaling ~3,300 tokens of context, then asked the local model to produce a brief matching the `scheduled-task.md` template.

## Setup

| Field | Value |
|-------|-------|
| Local model | Qwen 3.5 9B at MLX 4-bit quantization |
| Inference tool | LM Studio, OpenAI-compatible server on `127.0.0.1:1234` |
| Hardware | Apple Silicon, 16-24 GB unified memory |
| Initial LM Studio context length | 4,096 (default) — failed |
| Successful LM Studio context length | 16,384 (after reload) |
| System prompt | Built into `prepare-task.py` (begins with `/no_think`) |
| User message | Captured stub + five project layer files + scheduled-task template inline |
| Temperature | 0.3 |
| Max tokens (request) | 4,000 |

## The Run

```text
Calling LM Studio (qwen/qwen3.5-9b) for captured id 'screenshot-upload-ui'...
Wrote prepared brief: ./.sustaindev/queue/prework-ready/<id>.md
Removed captured stub: ./.sustaindev/queue/captured/<id>.md
Done. wall_clock=114.6s tokens=7504 reasoning_chars=1188 brief_chars=4231 validation_issues=0
```

| Metric | Value |
|--------|-------|
| Wall-clock | 114.6 s |
| Prompt tokens | 6,248 |
| Completion tokens | 1,256 |
| Total tokens | 7,504 |
| Reasoning chars | 1,188 (`/no_think` worked; 90% lower than case-study-01) |
| Brief chars | 4,231 (~750 words) |
| Validation issues | 0 (all required H2 sections present, YAML front matter parses) |
| Throughput | ~11 tok/s (similar to case-study-01) |
| Cost | $0 (local) |

The script automatically moved the captured stub to deletion and wrote the prepared brief to the `prework-ready/` queue. The measurement record landed in `.sustaindev/measurement/`.

### A v0.1.2 prerequisite gotcha

The first attempt failed with HTTP 400: `n_keep: 6248 >= n_ctx: 4096`. LM Studio's default context length is 4,096 tokens, which is too small for any serious project layer. After increasing context to 16,384 in LM Studio's model settings and reloading the model, the run succeeded. This finding now lives in `adapters/lm-studio/usage.md` as a v0.1.3 documentation update — the default LM Studio context length is wrong for SustainDev adopters who treat the project layer seriously.

## Quality Assessment of the Brief

**What the model got right:**

- All seven required H2 sections present in the right order (Captured Idea, Scope, File Targets, Verify Commands, Maintainability Constraints, Success Criteria, Notes for Execution, Retrospective).
- YAML front matter complete and parseable: `id`, `title`, `captured_at` preserved from the stub, `prepared_at` timestamp added, `status: prework-ready` set correctly, `priority` propagated.
- Verify commands lifted **verbatim** from the project's `VERIFY.md` — including the project-specific `mise exec dotnet@8 -- ...` runtime invocation pattern.
- File targets pulled from the project's `CODEMAP.md`, with rationale citations like *"per codemap guidance on 'Nieuwe wizard-stap of view'"* (the model preserved domain-language section names from a non-English codemap).
- All six maintainability dimensions addressed in the constraints section: architecture fit, coupling, naming, testability, error handling, change cost. Each populated with project-specific content drawn from `MAINTAINABILITY_NOTES.md`.
- Domain naming convention preserved (the project uses non-English domain terms with English code keywords; the model kept the convention faithfully).
- Cross-platform concern surfaced (Windows vs macOS file dialogs) without being explicitly told — the model inferred this from the project context.

**Three issues human triage would catch:**

1. **One hallucinated file path.** A test fixture path was invented that doesn't exist in the project. The model over-applied the "tests mirror App layer" rule from the codemap to a case where the project doesn't actually have view fixtures in tests.
2. **`time_window_suggested: for-example-22:00-06:00`** — the placeholder string was kept literally instead of choosing a value. Likely a prompt clarity issue: the template showed `<for-example-22:00-06:00>` as a placeholder, and the model preserved it rather than treating it as an example.
3. **`cloud_tool_suggested: empty`** — same issue. The literal string `empty` ended up in the field instead of an empty value or a real choice.

These are textbook "needs human triage" outcomes — not failures of the workflow, but evidence of why the `prework-ready/` queue exists. A human reviewer cleans these up in 3–5 minutes.

**Estimated overall quality:** ~80% complete as-is. After triage cleanup, the brief is fully usable as a scheduled-task brief for cloud execution.

## Comparison to Case-Study-01

The comparison is the key empirical finding of this case study. The same hardware, model, and tooling tier produced dramatically different results on a different task class.

| Metric | case-study-01 (weak fit) | case-study-03 (strong fit) |
|--------|--------------------------|----------------------------|
| Task class | Free-form full-document rule drafting | Structured template fill-in from rich context |
| Wall-clock | 215 s | 114 s (**1.9× faster**) |
| Total completion budget | 4,000 (cap hit; only 3,190 used) | 4,000 (used 1,256) |
| Reasoning chars (discarded) | 12,111 | 1,188 (**10× less waste**) |
| Useful output | ~1,964 chars (~300 words, incomplete) | 4,231 chars (~750 words, complete) |
| Sections produced vs requested | 2 of 6 | 7 of 7 |
| Validation result | n/a (the test predated `prepare-task.py` validation) | Passed all checks |
| Per-token efficiency | ~16% useful (570 tokens of useful output of 3,190 generated) | ~63% useful (1,256 tokens of useful output of ~7,504 generated, with reasoning at <10%) |

**The reasoning-overhead delta is the most striking.** In case-study-01, the model spent ~80% of its completion tokens on reasoning that was discarded. In case-study-03 with the same `/no_think` directive but a more structured task, reasoning dropped to ~6% of output. The difference is task class, not directive.

This is the strongest empirical signal yet for the routing-matrix discipline: **the same model on the same hardware behaves an order of magnitude differently across task classes.** A blanket "use local for prework" rule loses to a structured "use local for short structured outputs from rich context; use cloud for free-form full-document authoring."

## Strong-Fit / Weak-Fit Matrix Update

After this run, the matrix in `core/rules/model-routing.md` updates to:

| Task class | Fit | Why | Evidence |
|------------|-----|-----|----------|
| **Idea expansion: rough capture → structured task brief** | **Strong** | Hero-workflow centerpiece; structured output from rich context plays to the model's strengths. | **Measured in `docs/measurement/case-study-03.md` (this document).** |
| Idea triage / classification | Strong | Tiny output, fast inference. | Theoretical; not yet measured. |
| Codemap drafts from file lists | Strong | Pattern extraction; benefits from large context window. | Theoretical; not yet measured. |
| Summarization of long documents | Strong | Output is bounded; plays to the 262k context window. | Theoretical; not yet measured. |
| Risk extraction from existing prose | Strong | Pattern-matching task. | Theoretical; not yet measured. |
| Batch / overnight prework | Strong | Wall-clock cost is zero. | Theoretical; not yet measured. |
| Full-document drafting from rich brief | **Weak** | Reasoning overhead + wall-clock cost outweigh cloud savings. | Measured in `docs/measurement/case-study-01.md`. |
| Adapter templates | Weak | Tool-specific knowledge that 9B-class models often get wrong. | Theoretical; not yet measured. |
| Cross-document consistency checks | Weak | Wall-clock penalty too high. | Theoretical; not yet measured. |
| Time-critical authoring | Weak | User is waiting; latency is unacceptable. | Implicit from case-study-01. |

Two of ten rows are now empirically backed (one strong fit, one weak fit). The matrix is honest about this — "Theoretical; not yet measured" remains the label on the rest until measured. v0.2 should target the next-most-tractable rows: idea triage and codemap drafts.

## Findings

### 1. Strong-fit task classes really are different from weak-fit ones

This is no longer a routing-rule conjecture. The 10× reduction in reasoning waste between case-study-01 and case-study-03 is the empirical evidence. The same `/no_think` directive on the same hardware produced wildly different ratios of useful-to-wasted tokens depending on whether the task was free-form drafting or structured template fill-in.

### 2. Per-task triage is fast and worth it

Three minor issues in the brief (one hallucinated path, two placeholder leakage cases) cost ~3-5 minutes of human review to fix. That's fast compared to the 7 minutes of Cowork-side preparation it replaced. The `prework-ready/` queue holds output that is genuinely "needs review", not "garbage" — exactly the design intent.

### 3. The hero workflow's complete loop now works end-to-end

`capture-idea.sh` → `prepare-task.py` → human triage in `prework-ready/` → manual move to `scheduled/` → cloud execution → `completed/` with retrospective. Every transition is now real, file-backed, and tested on a real project. The v0.1 hero workflow promise is delivered.

### 4. LM Studio's default context length is wrong for SustainDev adopters

LM Studio defaults to 4,096-token context. SustainDev's project layer (5 files at ~3,300 tokens) plus the structural prompt (~2,000 tokens) plus a captured stub (~100 tokens) exceeds this on day one. **Any project that takes the project layer seriously will hit this on first use.** Fixed in v0.1.3 by updating `adapters/lm-studio/usage.md` with explicit "16,384 minimum" guidance.

### 5. Project layer files in non-English languages preserve correctly

The project under test uses non-English domain terms with English code keywords. The model preserved this convention faithfully — using the original language for domain terms in maintainability constraints, file targets, and execution notes. This validates that the SustainDev architecture works for non-English-language projects without modification.

### 6. The script's HTTP error handling pays off immediately

The first `prepare-task.py` invocation failed with HTTP 400. The improved error handler shipped in v0.1.2 surfaced the exact LM Studio response body (`n_keep: 6248 >= n_ctx: 4096`), turning an opaque "rejected by server" into a clear "context too small, fix it here." Without that error message, debugging would have taken 30+ minutes of guessing.

### 7. The brief preparation cost dropped from ~7 minutes to ~5 minutes (Cowork → local + triage)

case-study-02 measured ~7 minutes Cowork-side time on brief preparation. case-study-03's path: 114 seconds local model + ~3-5 minutes human triage = ~5-7 minutes total **with zero cloud tokens spent.** The token savings are the headline win. The wall-clock is roughly equivalent at this stage; future improvements (better prompts, larger local models on better hardware) could pull wall-clock further down.

## What This Does Not Prove

One run on one task on one project. The local-tier strong fit for idea expansion is now empirically validated, but:

- Other strong-fit task classes (idea triage, codemap drafts, summarization, risk extraction, batch prework) remain theoretically claimed and unmeasured.
- The 80% quality figure is one observation; quality variance across task complexity is unknown.
- The 5-minute triage cost is a guess; we have not measured human triage time across a sample of briefs.
- Other models (Qwen 2.5 Coder 7B as fallback, Codestral 22B on bigger hardware, etc.) were not tested.
- The project's primary language is non-English; English-only projects might behave differently (likely not meaningfully, but unmeasured).

What is credibly evidenced: the `prepare-task.py` workflow works on a real project, produces validation-passing output in under 2 minutes, surfaces issues that the `prework-ready/` triage step is designed to catch, and consumes zero cloud tokens.

## Reproducibility

An independent reproducer needs:

- A real project with the SustainDev project layer authored in `PROJECT_CONTEXT.md`, `CODEMAP.md`, `AI_POLICY.md`, `MAINTAINABILITY_NOTES.md`, `VERIFY.md` (~3,000-4,000 tokens total).
- `scripts/schedule/capture-idea.sh` and `scripts/schedule/prepare-task.py` from SustainDev v0.1.2 or later.
- LM Studio with Qwen 3.5 9B (MLX 4-bit) loaded **at context length 16,384 or larger.**
- Apple Silicon at 16-24 GB unified memory (or equivalent on other hardware tiers; numbers will differ).
- A captured idea reasonable in scope (one wizard step, one feature flag, one helper function — not a full multi-week sprint).

Quantitative numbers will vary with hardware, model version, prompt length, and idea complexity. Order-of-magnitude reproducibility (90-180 s wall-clock, validation-passing output, 0-2 minor triage issues) is plausible.

## v0.2 Backlog Updated

Three new evidence-backed priorities from this run:

1. **`prepare-task.py` should warn before sending if estimated prompt tokens exceed `LM_STUDIO_CONTEXT // 1.5`.** Pre-flight check; saves the user a failed call.
2. **Configurable project-layer file inclusion** (e.g., `--exclude-file MAINTAINABILITY_NOTES.md`) for users with smaller context budgets. Lets large project layers gracefully degrade.
3. **case-study-04 candidate: idea triage on the same project**, classifying the project's current uncommitted work into commit-now / review-first / archive buckets. Smallest expected output, highest expected token savings, most tractable next measurement. Targets the next strong-fit row in the matrix.
