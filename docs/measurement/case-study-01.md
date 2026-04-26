# Case Study 01: Local-Model Drafting of a Markdown Rule File

## Summary

Full-document markdown drafting on 16–24 GB Apple Silicon using the Qwen 3.5 9B model is a weak fit for the local-prework tier due to significant reasoning overhead and unacceptable wall-clock latency. However, smaller, structurally bounded tasks like idea triage, document summarization, and codemap generation remain highly promising strong fits for local execution, pending measurement.

## What Was Tested

The primary measurement task during Sprint 1 tested the local-model prework tier against a highly specific kind of work: drafting a complete markdown rule document derived strictly from a structured brief. The working hypothesis suggested that a 9B local model could successfully produce a usable first draft that a cloud model would finish, saving expensive cloud tokens at an acceptable wall-clock cost.

The target output file was `core/rules/token-efficiency.md`, defined as a ~500–700 word document containing six sections. The rationale for selecting this task was clear: it is structurally well-defined, themed to the project, a genuine Sprint 1 deliverable, and its failure modes remain highly visible within the generated prose quality.

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

During the initial execution, reasoning mode remained fully active without suppression. The model immediately exhausted its entire 1500-token generation budget generating content exclusively inside `<think>` blocks, filling the internal `reasoning_content` channel. Consequently, the standard `message.content` payload returned completely empty. The execution failed, yielding zero usable draft output.

| Metric | Value |
|--------|-------|
| Wall-clock | 121.49 s |
| Prompt tokens | 868 |
| Completion tokens | 1500 (hit cap exactly, all consumed by reasoning) |
| Visible draft | 0 chars |
| Outcome | Failed — empty output |

Following this failure, the testing script received updates to handle this edge case: dumping the raw JSON response, falling back to the `reasoning_content` channel if the standard content field remained empty, and defensively stripping `<think>` tags. The default `max_tokens` limit was aggressively raised to 4000 to accommodate the severe reasoning bloat.

## Run 2: With /no_think

Applying the `/no_think` directive successfully reduced the pervasive reasoning mode behavior, though it failed to eliminate it entirely. The model still emitted 12,111 characters of internal `reasoning_content` (which the script subsequently discarded), but then transitioned to producing roughly 300 words of highly usable draft material before slamming into the raised budget cap.

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

The generated draft proved structurally sound. The heavily enforced H1 and H2 headings perfectly matched the requirements laid out in the brief. The generated output correctly respected the strict project tone rules, omitting first-person perspectives, avoiding invented numbers, and steering clear of prohibited FAQ structures. 

The generated "Core Rules" section proved fundamentally acceptable, containing nine explicit sentence-form rules that were overwhelmingly actionable. The prose itself, however, proved noticeably mediocre. Distinctly clichéd filler phrases populated the text, and crucial conceptual boundaries occasionally blurred within single paragraphs.

Critically, the document remained structurally incomplete. The final section halted abruptly mid-sentence, explicitly missing three required sections. The underlying cause of this incompleteness was glaringly obvious: approximately 2,620 of the 3,190 completion tokens went entirely to hidden reasoning, leaving a meager ~570 tokens allocated for the actual draft. This reduced budget barely covered roughly two of the six requested sections.

## Cloud-from-Scratch Counterfactual

Executing the exact same task end-to-end utilizing Claude Sonnet 4.6 completed rapidly in approximately 30–45 seconds and successfully produced a complete, structurally perfect six-section document. The estimated cost for this pure cloud execution lands precisely at roughly 1,500 input tokens and 1,500 output tokens. Note that the cloud baseline was not run distinctly as part of this exact case study; the actual Sprint 1 deliverable was authored identically in a cloud-from-scratch mode by a reviewer.

| Approach | Wall-clock | Cloud tokens | Local tokens | Doc completeness |
|----------|-----------|--------------|--------------|------------------|
| Cloud-only (Sonnet 4.6, scratch) | ~30–45 s | ~3,000 (1.5k in + 1.5k out) | 0 | Complete |
| Local-prework + cloud-finish | 215 s + ~30 s = ~245 s | ~2,300 (1.5k in + 800 out for finish) | 4,096 | Complete (after finish) |

The explicitly conservative cloud-side savings derived strictly from running the local prework on this specific task amounts to roughly 700 cloud tokens. Whether that strictly marginal cost reduction justifies absorbing approximately 200 extra wall-clock seconds depends overwhelmingly on whether the active user is waiting on the execution loop.

## Conclusions

1. **Full-document drafting is a distinctly weak fit for the local-prework tier on this hardware class.** The overwhelming reasoning-mode overhead, severely compounded by the extreme wall-clock cost, definitively outweighs the minor cloud token savings when executed for a single interactive task.

2. **The token savings firmly become real only when the wall-clock cost drops to zero.** Pushing these heavy structural generation tasks into offline batch, overnight, or tightly queued execution windows is exactly where the core economic math undeniably works.

3. **The local tier rigorously remains highly valuable for strictly constrained task classes.** Tasks encompassing idea triage, drafting tightly scoped codemaps directly from file lists, precise summarization of incredibly long documents, and explicit risk extraction from existing prose heavily rely on small expected outputs where underlying reasoning overhead fundamentally matters significantly less.

4. **The definitive model-routing decision must absolutely avoid standardizing "use local for prework, cloud for finish" as an immovable blanket rule.** Instead, it must meticulously evolve to strictly mandate "use local strictly for highly structural short outputs and batch work; strictly use the cloud tier for any full-document authoring occurring during live, active development sessions."

## What This Does Not Prove

This precise case study rigorously tested one highly specific task class executing on exactly one standardized hardware tier utilizing exactly one targeted model variant. Distinctly separate, highly claimed strong-fit task classes (such as specific idea triage workflows, structural codemap drafts, or explicit document summarization) remain highly plausible but strictly unmeasured. Gathering empirical measurement for those specific use cases remains an explicit focus designated strictly for v0.2 development work. 

## Reproducibility

An independent reproducer aiming to rigorously verify these exact metrics strictly requires:
- Mainstream Apple Silicon hardware featuring 16–24 GB unified memory.
- A functional LM Studio installation capable of hosting the local server API.
- The specifically targeted Qwen 3.5 9B model leveraging explicit MLX 4-bit quantization.
- The precise system prompt stored locally at `scripts/sprint1/system_prompt.md`.
- The corresponding user brief located distinctly at `scripts/sprint1/user_brief.md`.
- Execution running exclusively through the `scripts/sprint1/run_prework.py` utility script to guarantee identical handling of the `reasoning_content` field.
