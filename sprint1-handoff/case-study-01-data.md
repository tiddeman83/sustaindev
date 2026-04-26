# Case Study 01: Pre-Digested Run Data

This file packages everything the case-study-01 author (Antigravity) needs to write `docs/measurement/case-study-01.md` without re-deriving the analysis. The raw artifacts referenced here live under `scripts/sprint1/output/`.

## What Was Tested

The first measurement task in Sprint 1 was a deliberate test of the local-model prework tier on a **specific kind of work**: drafting a full markdown rule document from a structured brief. The hypothesis: a 9B local model can produce a usable first draft that a cloud model finishes, saving cloud tokens at acceptable wall-clock cost.

The target file was `core/rules/token-efficiency.md`, ~500–700 words, six sections. The rationale for picking this task: structurally clear, themed to the project, real Sprint 1 deliverable, failure modes visible in prose quality.

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

## Two Runs Were Performed

### Run 1: Default Settings, No /no_think

Reasoning mode was active. The model spent its full 1500-token budget inside `<think>` blocks (or its `reasoning_content` channel). `message.content` returned empty. **No usable draft produced.**

| Metric | Value |
|--------|-------|
| Wall-clock | 121.49 s |
| Prompt tokens | 868 |
| Completion tokens | 1500 (hit cap exactly, all consumed by reasoning) |
| Visible draft | 0 chars |
| Outcome | Failed — empty output |

The script was updated to handle this case: dump the raw response, fall back to `reasoning_content` if `content` is empty, strip `<think>` tags defensively. Default `max_tokens` was raised to 4000.

### Run 2: With /no_think Directive, max_tokens=4000

Reasoning mode reduced but not eliminated. The model still emitted 12,111 chars of `reasoning_content` (discarded), then produced 300 words of usable draft before hitting the budget cap.

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

Raw artifacts:

- `scripts/sprint1/output/draft.md` — the 300-word partial draft.
- `scripts/sprint1/output/measurement.json` — machine-readable record.
- `scripts/sprint1/output/raw_response.json` — full unmodified LM Studio response, including reasoning_content.
- `scripts/sprint1/output/run.log` — console log.

## Quality Assessment of Run 2 Output

Reviewer (Cowork) read the draft and assessed:

**Structurally sound.** H1 + H2 headings match the brief. Output respects the no-first-person, no-invented-numbers, no-FAQ rules.

**Core Rules section is acceptable.** Nine sentence-form rules, mostly actionable. One rule ("avoid requesting explanations for code that has already been reviewed or merged") is mislabeled — it's a workflow nicety, not a token-efficiency rule.

**Prose is mediocre.** Phrases like "without unnecessary overhead" and "historical noise" are clichéd filler. One sentence in Purpose ("long-term maintainability of the project depends on keeping the context window clean and focused on current tasks rather than historical noise") muddles two distinct concepts.

**Document is incomplete.** Stop Conditions section cuts off mid-sentence at "Halt reading". Three full sections are missing: What Gets Cached vs Re-Discovered, Routing Cheap Work to Local Models, Verification.

The cause of incompleteness is clear: ~2,620 of the 3,190 completion tokens went to reasoning, leaving ~570 tokens for the draft. ~570 tokens covers roughly two of the six requested sections.

## Cloud-from-Scratch Counterfactual

The same task done end-to-end by Claude Sonnet 4.6 (no local prework) was completed in approximately 30–45 seconds and produced a complete six-section document. Estimated cost: ~1,500 input tokens + ~1,500 output tokens.

The reviewer wrote the actual final `core/rules/token-efficiency.md` from scratch in this mode and the file is present in the repo at that path.

| Approach | Wall-clock | Cloud tokens | Local tokens | Doc completeness |
|----------|-----------|--------------|--------------|------------------|
| Cloud-only (Sonnet 4.6, scratch) | ~30–45 s | ~3,000 (1.5k in + 1.5k out) | 0 | Complete |
| Local-prework + cloud-finish | 215 s + ~30 s = ~245 s | ~2,300 (1.5k in + 800 out for finish) | 4,096 | Complete (after finish) |

**Conservative cloud-side savings from local prework on this task: roughly 700 cloud tokens.** Whether that's worth ~200 extra wall-clock seconds depends entirely on whether the user is waiting.

## Conclusions Drawn From The Data

The case study writer should anchor their prose in these conclusions, but should also state them in their own voice:

1. **Full-document drafting is a weak fit for the local-prework tier on this hardware class.** The reasoning-mode overhead (even with `/no_think`) and the wall-clock cost outweigh the cloud token savings for a single task.

2. **The savings only become real when wall-clock cost is zero.** Batch / overnight / queued execution is where the math works.

3. **The local tier remains valuable for other task classes.** Idea triage, codemap drafts from file lists, summarization of long documents, classification, risk extraction from existing prose — these have small expected outputs (where reasoning overhead matters less), benefit from the 262k context window, and don't require the user to wait. These were not tested in this run; the case study should be honest about that.

4. **The model-routing decision should not be "use local for prework, cloud for finish" as a blanket rule.** It should be **"use local for short structured outputs and batch work; use cloud for full-document authoring during active sessions."**

5. **Hardware tier matters.** A workstation with a discrete GPU running a 14B–32B coder model would likely shift the answer for some of the weak-fit tasks. The current answer applies to mainstream Apple Silicon at 16–24 GB.

## What The Case Study Should NOT Claim

- Do not extrapolate to other model sizes without measurement.
- Do not claim percentage savings ("60% cheaper") — the cost difference on a single document is too small for percentages to be meaningful.
- Do not present this as a definitive verdict on local-model prework — it is one task class on one hardware tier.
- Do not bash Qwen 3.5 9B as a model. The model performed within expectations for its class. The lesson is about routing, not about the model.

## Suggested Structure for the Case Study Document

The Antigravity brief gives the full required structure for `docs/measurement/case-study-01.md`. This data file is the input; the brief is the output specification.
