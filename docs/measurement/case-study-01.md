# Case Study 01: Local-Model Drafting of a Markdown Rule File

## Summary

Full-document markdown drafting on 16–24 GB Apple Silicon using Qwen 3.5 9B is a weak fit for the local-prework tier — reasoning overhead and wall-clock latency outweigh the cloud token savings. Smaller, structurally bounded tasks (idea triage, summarization, codemap generation) remain promising strong fits for local execution, pending measurement.

## What Was Tested

The first Sprint 1 measurement tested the local-model prework tier on one specific kind of work: drafting a full markdown rule document from a structured brief. The hypothesis: a 9B local model could produce a usable first draft that a cloud model finishes, saving cloud tokens at acceptable wall-clock cost.

The target was `core/rules/token-efficiency.md`, ~500–700 words, six sections. The rationale: structurally clear, themed to the project, a real Sprint 1 deliverable, with failure modes visible in prose quality.

## Setup

| Field | Value |
|-------|-------|
| Local model | Qwen 3.5 9B (MLX 4-bit, ~7.5 GB total memory) |
| Inference tool | LM Studio, OpenAI-compatible server on `127.0.0.1:1234` |
| Hardware | Apple Silicon, 16–24 GB unified memory |
| System prompt | `scripts/sprint1/system_prompt.md` (with `/no_think` directive) |
| User brief | `scripts/sprint1/user_brief.md` |
| Temperature | 0.3 |
| Max tokens (request) | 4000 |

## Run 1: Default Settings

In the first run, reasoning mode was active. The model spent the full 1500-token generation budget inside `<think>` blocks (filling the `reasoning_content` channel). The `message.content` payload returned empty. No usable draft.

| Metric | Value |
|--------|-------|
| Wall-clock | 121.49 s |
| Prompt tokens | 868 |
| Completion tokens | 1500 (hit cap exactly, all consumed by reasoning) |
| Visible draft | 0 chars |
| Outcome | Failed — empty output |

After this failure, the script was updated to handle the edge case: dump the raw JSON response, fall back to `reasoning_content` if `content` is empty, defensively strip `<think>` tags. Default `max_tokens` was raised to 4000.

## Run 2: With /no_think

The `/no_think` directive reduced reasoning mode but did not eliminate it. The model emitted 12,111 characters of `reasoning_content` (discarded by the script), then produced ~300 words of usable draft before hitting the raised budget cap.

| Metric | Value |
|--------|-------|
| Wall-clock | 215.19 s |
| Prompt tokens | 906 |
| Completion tokens | 3,190 |
| Reasoning content | 12,111 chars (~2,620 tokens, discarded) |
| Visible draft | 1,964 chars / ~300 words |
| Throughput | ~14.8 tok/s |
| Cost | $0 (local) |
| Outcome | Partial — 2 of 6 sections produced, document incomplete |

## Quality Assessment

The draft was structurally sound. H1 and H2 headings matched the brief. The output respected the project tone rules: no first person, no invented numbers, no FAQ section.

The "Core Rules" section was acceptable — nine sentence-form rules, mostly actionable. Prose was mediocre. Clichéd filler phrases populated the text, and conceptual boundaries occasionally blurred within paragraphs.

The document was incomplete. The final section cut off mid-sentence and three required sections were missing entirely. The cause is clear from the numbers: ~2,620 of the 3,190 completion tokens went to reasoning, leaving ~570 for the actual draft. ~570 tokens covers roughly two of the six requested sections.

## Cloud-from-Scratch Counterfactual

The same task executed end-to-end on Claude Sonnet 4.6 completes in ~30–45 seconds and produces a complete six-section document. Estimated cost: ~1,500 input tokens + ~1,500 output tokens. The cloud baseline was not run as part of this case study; the actual Sprint 1 deliverable was authored cloud-from-scratch by a reviewer.

| Approach | Wall-clock | Cloud tokens | Local tokens | Doc completeness |
|----------|-----------|--------------|--------------|------------------|
| Cloud-only (Sonnet 4.6, scratch) | ~30–45 s | ~3,000 (1.5k in + 1.5k out) | 0 | Complete |
| Local-prework + cloud-finish | 215 s + ~30 s = ~245 s | ~2,300 (1.5k in + 800 out for finish) | 4,096 | Complete (after finish) |

The conservative cloud-side savings from local prework on this task amount to roughly 700 cloud tokens. Whether that justifies ~200 extra wall-clock seconds depends on whether the user is waiting.

## Conclusions

1. **Full-document drafting is a weak fit for the local-prework tier on this hardware class.** The reasoning-mode overhead and the wall-clock cost outweigh the cloud token savings on a single interactive task.

2. **The savings only become real when the wall-clock cost is zero.** Pushing these tasks into batch, overnight, or queued execution windows is where the math works.

3. **The local tier remains valuable for bounded task classes.** Idea triage, codemap drafts from file lists, summarization of long documents, and risk extraction from existing prose have small expected outputs where reasoning overhead matters less.

4. **The routing rule should not be "use local for prework, cloud for finish" as a blanket.** It should be "use local for short structural outputs and batch work; use cloud for full-document authoring during live sessions."

## What This Does Not Prove

This case study tested one task class on one hardware tier with one model. The other strong-fit task classes (idea triage, codemap drafts, summarization) are claimed but not yet measured. Filling in those measurements is v0.2 work.

## Reproducibility

An independent reproducer needs:
- Mainstream Apple Silicon at 16–24 GB unified memory.
- LM Studio with the local server API enabled.
- Qwen 3.5 9B with MLX 4-bit quantization.
- The system prompt at `scripts/sprint1/system_prompt.md`.
- The user brief at `scripts/sprint1/user_brief.md`.
- Execution via `scripts/sprint1/run_prework.py` to ensure consistent handling of the `reasoning_content` field.
