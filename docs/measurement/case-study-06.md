# Case Study 06: Summarization — A New Failure Mode at Larger Context

**Run date:** 2026-04-27
**Project:** project-a (a .NET 8 Avalonia desktop app, ~v0.0.7 internal POC)
**Workflow:** `scripts/sprint1/summarize-doc.py` (one-shot probe)
**Tools:** Qwen 3.5 9B at MLX 4-bit running locally in LM Studio on Apple Silicon (16-24 GB unified memory)
**Task class tested:** **Summarization of long documents** — the fourth strong-fit row from the routing matrix.

## Summary

Two runs on the same long document (~40 KB / 10,700 tokens of architecture documentation), with different LM Studio context sizes and output budgets. Both runs failed to produce clean visible output — but **for opposite reasons**. Run 1 (16k context, 2k output cap) leaked reasoning into the visible content channel and truncated mid-section. Run 2 (32k context, 8k output cap) channeled all output to `reasoning_content` and left visible content empty. The script's fallback ("if content is empty, use reasoning") rescued the data; a usable summary in Dutch had to be extracted by reading through the model's planning prose.

The honest finding: **`/no_think` does not control where reasoning lands; context size does.** At smaller context, reasoning has nowhere to go and leaks into visible output. At larger context, the model uses `reasoning_content` aggressively and may leave visible content empty. Both behaviors fail the task as written — the user gets either a polluted output or a "where's my answer?" output. The summary content itself was high quality in both runs; the packaging was the failure.

This makes summarization the third **conditionally strong-fit** row of the matrix, with a different condition than idea-triage (which needed rich context) or codemap-drafts (which needed sufficient max_tokens). Summarization needs **post-processing that extracts the summary from wherever the model put it**, plus a stricter prompt structure that forces the model to commit to one channel.

## What Was Tested

A real, useful task on a real project: summarize a 40,766-character technical architecture document into a structured ~500-word summary with H2 section headers mirroring the source. Summary shape: structured (not executive prose, not bulleted list).

Two runs on the same prompt, different context/budget:

- Run 1: LM Studio context 16k, `--max-tokens 2000`
- Run 2: LM Studio context 32k, `--max-tokens 8000`

The intent was to repeat case-study-05's "budget too tight vs sufficient" experiment on a different task class (summarization vs catalog drafting). What we found instead was a completely different failure mode at the larger configuration.

## Setup

| Field | Value |
|-------|-------|
| Local model | Qwen 3.5 9B at MLX 4-bit |
| System prompt | `/no_think` + summarizer role + length target + output rules |
| User message | Document path header + the full 40,766-char document |
| Temperature | 0.2 |
| Target output | ~500 words, structured shape |

## Run 1: 16k Context, 2k Output Cap

| Metric | Value |
|--------|-------|
| Wall-clock | 202.6 s |
| Prompt tokens | 12,085 |
| Completion tokens | 2,000 (cap hit) |
| Reasoning chars (channel) | 8,013 |
| Output chars (visible) | 8,013 |
| Actual words in output | 1,034 (target was 500) |
| Outcome | Reasoning leaked into visible content; output truncated mid-section |

The visible output started with `Thinking Process:` and walked through the model's analysis (`1. Analyze the Request:`, `2. Analyze the Source Document:`, `3. Drafting the Summary:`). A complete first-draft summary was embedded in the planning prose at lines 49-62 — well-structured, in Dutch, all sections covered. Then the model started a "Refining for Length" expansion pass and ran out of budget mid-section.

This is the same failure mode as case-study-05 Run 1: budget too tight, reasoning leaks into visible output. Confirmed across task classes.

## Run 2: 32k Context, 8k Output Cap

| Metric | Value |
|--------|-------|
| Wall-clock | 299.1 s (+47% over Run 1) |
| Prompt tokens | 12,085 |
| Completion tokens | 4,299 (under 8k cap) |
| Reasoning chars (channel) | 17,445 |
| Output chars (visible content) | 0 (empty — all output went to reasoning channel) |
| Actual words extracted from reasoning | 2,289 |
| Outcome | Visible content empty; script fallback used reasoning_content as output |

This was the surprise. With the larger context, the model used the `reasoning_content` channel for the entire response and emitted nothing in the visible `content` channel. The probe script's defensive fallback (`if content is empty, use reasoning_content`) rescued the data — but the user got 17,445 characters of "thinking out loud" instead of a clean summary.

Inside the reasoning, the model produced **two complete summary drafts**: one initial draft at ~400 words, then an explicit "Revised Draft" at ~500 words with a polished one-line takeaway ("De Excel IS de opslag." — *the Excel IS the storage*). Both drafts were structurally correct, in Dutch, with H2 headers mirroring the source. The triage step (~10 minutes) consisted of locating draft 2 in the reasoning text, fixing one source-numbering inconsistency (the source itself had two `## 8.` sections), and saving as the project's actual `docs/Architectuur_samenvatting.md`.

## The Two Failure Modes Compared

The opposite failure modes between Run 1 and Run 2 are the case study's most actionable finding.

| Aspect | Run 1 (16k context, 2k cap) | Run 2 (32k context, 8k cap) |
|--------|-----------------------------|-----------------------------|
| Where the reasoning landed | Visible output channel | Reasoning channel only |
| What the user sees | Polluted output with embedded summary | Empty visible content |
| Output truncation | Yes (cap hit) | No (cap not hit) |
| Recovery via script fallback | Not needed; output was already in `content` | Required; script's `if content is empty use reasoning` rule fired |
| Content quality once extracted | First draft visible, complete | Two drafts visible, second one polished |
| Triage time | ~10 min (extract from polluted prose) | ~10 min (extract from reasoning) |

`/no_think` was identical in both runs. The model's behavior diverged based on context size, not the directive. **The directive is a hint, not a guarantee.**

## What This Adds To The Pattern

Cross-case-study, the local tier's reasoning behavior now shows three regimes for this hardware tier (Apple Silicon at 16-24 GB, Qwen 3.5 9B):

1. **Tight budget (e.g., 4k cap on rich-output task or 2k on long-input summarization):** reasoning leaks into visible content, output truncates. Failure mode: pollution + truncation.
2. **Generous budget at smaller context (e.g., 8k cap at 16k context on case-study-05's 12-file catalog):** reasoning channels properly to `reasoning_content`, visible content is clean and complete. Success.
3. **Generous budget at larger context (case-study-06 Run 2: 8k cap at 32k context on a 40KB summarization):** reasoning channels but visible content stays empty. The model invests all output in "thinking" and never commits to a final answer. Failure mode: missing answer.

The catalog-drafting task (case-study-05) sat in regime 2 with its 8k-at-16k configuration. The summarization task (case-study-06) sat in regime 3 even at the same budget. The single variable that changed: input size (8KB interface bundle vs 40KB document) and the corresponding context bump (16k → 32k).

The provisional rule of thumb: **`max_tokens` should be set just high enough to keep reasoning channeled, but `lm_studio_context` should be set just high enough for the prompt — not larger.** Larger contexts invite the model to think more, not to think more efficiently.

## Quality of the Underlying Content

Despite the packaging failures, the actual summary quality was high in both runs:

- **Language preserved:** both runs produced summaries in Dutch (matching the source).
- **Structure preserved:** H2 headers mirrored the source's section structure faithfully.
- **No invented content:** every section header that appeared in the summary mapped to a section in the source. No facts, decisions, or claims were invented.
- **Length target:** Run 1's first draft was ~400 words (close to target). Run 2's polished second draft was ~500 words (on target). Run 2's actual visible-output word count of 2,289 is the cumulative reasoning + drafts + planning, not a single summary.
- **Takeaway sentence:** Run 2's polished draft ended with "De Excel IS de opslag." — a strong one-liner that captures the document's single most important architectural decision.

The model is genuinely competent at this task. The cost is the packaging — getting that competent output to land cleanly in visible content.

## Strong-Fit / Weak-Fit Matrix Update

Five of ten rows now empirically backed:

| Task class | Fit | Why | Evidence |
|------------|-----|-----|----------|
| **Summarization of long documents** | **Conditionally strong** | Content quality high (correct language, structure, takeaway). Packaging unreliable: at smaller context, reasoning leaks into output; at larger context, all output goes to reasoning channel. Recovery requires post-processing that extracts the summary from wherever it lands. | **Measured in `docs/measurement/case-study-06.md` (this document).** |
| Codemap drafts from file lists | Conditionally strong | Needs sufficient `--max-tokens`; reasoning consumes 50-70% of budget. | Measured in case-study-05. |
| Idea triage / classification | Conditionally strong | Needs rich context; spot-check on edge cases. | Measured in case-study-04. |
| Idea expansion: rough capture → structured task brief | Strong | Hero-workflow centerpiece. | Measured in case-study-03. |
| Risk extraction from existing prose | Strong | Pattern-matching task. | Theoretical; not yet measured. |
| Batch / overnight prework | Strong | Wall-clock cost is zero. | Implicit from CS-03/04/05/06. |
| Full-document drafting from rich brief | Weak | Reasoning overhead + wall-clock cost. | Measured in case-study-01. |
| Adapter templates | Weak | Tool-specific knowledge. | Theoretical; not yet measured. |
| Cross-document consistency checks | Weak | Wall-clock penalty too high. | Theoretical; not yet measured. |
| Time-critical authoring | Weak | User is waiting. | Implicit from case-study-01. |

Three of four measured strong-fit rows landed as **conditionally strong** with task-class-specific conditions. Idea expansion remains the only unconditionally strong row. The pattern: structure-extraction tasks succeed when the model's "thinking room" matches the task's actual reasoning need; over- or under-providing it produces different failure modes.

## Findings

### 1. /no_think is a hint, not a control

Across cases-studies 03, 04, 05, and 06, `/no_think` reduced reasoning but never eliminated it. Where reasoning lands depends on context size. This belongs in the routing rules and the LM Studio adapter docs.

### 2. Larger context does not improve summarization output

The 32k context Run 2 produced worse visible output than the 16k Run 1. The 16k run at least put the summary in visible content (polluted with planning, but extractable). The 32k run produced empty visible content. Setting LM Studio's context "as large as fits" is the wrong instinct.

### 3. Probe scripts need post-processing for summarization

The `summarize-doc.py` script's fallback (use reasoning_content when content is empty) saved the data but produced an unwieldy 17,445-char output. v0.2 fix: detect when reasoning has been used as output, parse out the last "Revised Draft" or final structured block, and write only that to the markdown file. Mirror the count-recomputation pattern from `triage-files.py` and the de-duplication pattern slated for `draft-catalog.py`.

### 4. The model produces multiple drafts during reasoning

Run 2's reasoning channel contained two full summary drafts. The model used the reasoning phase to draft, self-review, refine, and re-draft. This is actually high-quality cognitive behavior — the model is doing exactly what a human writer does. The cost is that this all stays "internal" unless the script extracts the final draft.

### 5. Quality is task-class consistent; packaging is task-class divergent

Across all four conditionally-strong tasks measured, the underlying content quality has been high (zero or near-zero hallucinations, correct language, correct structure, integration of project context). The conditions that vary are about packaging: max_tokens too low (CS-04, CS-05 Run 1, CS-06 Run 1), context too large (CS-06 Run 2), missing context files (CS-04). Once packaging is solved, the content is genuinely useful.

### 6. Wall-clock for summarization scales sublinearly with context

Run 1: 202.6s at 16k context. Run 2: 299.1s at 32k context. 2x context produced only 1.5x wall-clock, not 2x. The model's per-output-token speed actually held roughly constant; the difference came from total output volume, not from context-related slowdown.

### 7. Useful summary extracted, real project value delivered

Despite the packaging failures, project-a now has its first AI-drafted architecture summary as `docs/Architectuur_samenvatting.md`. The summary captures 11 sections faithfully, ends with a strong takeaway, and would not have existed without this run. The local-tier value proposition holds even when the packaging needs human triage — *as long as the human triage is fast*. ~10 minutes of extraction beats ~60 minutes of writing the summary from scratch.

## What This Does Not Prove

One document on one project on one model. Specifically:

- Other document types (specifications, policies, RFCs, post-mortems) were not tested.
- Other source languages (English, mixed) were not tested.
- Other summary shapes (executive prose, bulleted) were not tested in this case study; only structured.
- Other models (smaller 7B, larger 14B-32B) may behave differently, especially regarding the visible-content-vs-reasoning split. A model with stricter `/no_think` compliance would behave differently.
- LM Studio version-specific behavior was not investigated. The `/no_think` interaction with context size may be specific to this LM Studio + Qwen 3.5 9B combination.

## Reproducibility

An independent reproducer needs:

- A real project with a long technical document (~30-50 KB).
- The SustainDev v0.1.4+ release with `scripts/sprint1/summarize-doc.py`.
- LM Studio with Qwen 3.5 9B (MLX 4-bit) loaded.
- Apple Silicon at 16-24 GB unified memory or equivalent.
- ~10 minutes for the run plus ~10-15 minutes for triage.

To reproduce the dual-run experiment specifically: run once with context=16k + max_tokens=2000, then bump to context=32k + max_tokens=8000 and re-run. Order-of-magnitude reproducibility for the two failure modes (visible-content pollution at smaller config; empty-content fallback at larger config) is plausible.

## v0.2 Backlog Updated

Five new evidence-backed priorities, layered on the case-study-05 backlog:

1. **`summarize-doc.py` post-processing.** Detect when `reasoning_content` was used as fallback (output_chars == reasoning_chars), parse the model's "Revised Draft" or final structured block, write only that to the markdown file. Closes finding #3.
2. **Document the three reasoning regimes** in `core/rules/model-routing.md` and `adapters/lm-studio/usage.md`. The "max_tokens just high enough; context just large enough for prompt" rule of thumb closes finding #1 and #2.
3. **Stricter `/no_think` enforcement options.** Investigate alternatives: explicit "do not output reasoning anywhere" framing in the system prompt, post-processing that strips a "Thinking Process:" preamble if present, or a wrapper that sends a follow-up "now produce only the final answer" call after the initial response.
4. **Multi-draft extraction utility.** When the model produces multiple drafts during reasoning, extract the LAST one. Useful across summarize-doc, draft-catalog, and any future structured-output script.
5. **case-study-07 candidate: risk extraction.** Different task class, similar shape (long input → structured output). Test whether the regime-3 failure (empty visible content) repeats for risk extraction or is specific to summarization.

## What Got Confirmed

The local-prework tier still works at this hardware tier — the underlying model is competent, signature accuracy is high, content quality is high. What changes case-study to case-study is the *packaging* of that competence, and the packaging is genuinely fragile in ways that need script-side defenses. Five of ten matrix rows now have empirical backing. Three of four measured strong-fit rows are conditional. The matrix is honest about that.
