# LM Studio Adapter

## Purpose

This adapter provides the local-prework execution tier. It routes structured tasks to a local model running in LM Studio to reduce cloud token use. It does not replace the cloud tier; it handles tasks where wall-clock latency is acceptable and the output will be reviewed before any commit.

## Prerequisites

- LM Studio installed.
- Supported hardware (see Recommended Model below).
- The recommended model downloaded and loaded.

## Recommended Model

Lead choice: **Qwen 3.5 9B at MLX 4-bit quantization**, for Apple Silicon at 16–24 GB unified memory. MLX runs ~15–30% faster than GGUF on Apple Silicon and uses ~10% less memory, so prefer it on Mac hardware. Qwen 2.5 Coder 7B is a fallback for older Apple Silicon (M1 at 8 GB) or non-MLX setups. Codestral 22B is an alternative for users with discrete GPUs or 64 GB+ unified memory.

## Setup

1. Download LM Studio from `https://lmstudio.ai`.
2. In LM Studio, search for and download the `qwen/qwen3.5-9b` MLX 4-bit variant.
3. Open the *Developer* tab and enable the local server (default port 1234).
4. Confirm the server is reachable: `curl http://127.0.0.1:1234/v1/models`.

## Configuration

Set the temperature to 0.3 for more deterministic output. Set the context length to a value comfortable for your hardware; the Qwen model supports up to 262k natively, but 32k is a comfortable cap for 16 GB systems without memory swapping. For Qwen 3.x models, include `/no_think` in the system prompt to suppress reasoning overhead on tasks that don't benefit from chain-of-thought.

## What This Adapter Is Good For

- **Idea triage and classification.** Output is tiny, inference is fast, cloud savings compound at scale.
- **Codemap drafts from file lists.** Pattern extraction; the large context window helps.
- **Summarization of long documents.** Output is bounded, the 262k context window pays off.
- **Risk extraction from existing prose.** Pattern-matching task; structure matters more than prose quality.
- **Idea expansion.** Turning a rough capture into a structured task brief works when the user has stepped away.
- **Batch or overnight prework.** Wall-clock cost is effectively zero when execution is asynchronous.

## What This Adapter Is Not Good For

- **Full-document drafting.** Reasoning overhead and wall-clock cost outweigh the cloud token savings.
- **Adapter templates.** Tool-specific knowledge that 9B-class models often get wrong.
- **Cross-document consistency checks.** Wall-clock penalty too high for active sessions.
- **Time-critical authoring.** When the user is waiting, the latency is unacceptable.

Empirical backing for these limitations: `docs/measurement/case-study-01.md`.

## Integration with the Hero Workflow

The `idea-to-prepared-task` skill (`core/skills/idea-to-prepared-task/SKILL.md`) uses this adapter for the preparation step when the user opts in. The adapter is optional; cloud-only setups skip the local tier without breaking the hero workflow.

## Honest Limitations

Local-model quality varies with hardware. Token counts between LM Studio and cloud APIs use different tokenizers and don't compare apples-to-apples. Reasoning-mode behavior in Qwen 3.x can consume a large share of the token budget; `/no_think` helps but does not fully eliminate it. The 215-second wall-clock measured in case-study-01 is realistic for this hardware tier on a ~500-word document. Your mileage varies with task complexity, prompt structure, and system load.

## Troubleshooting

- **Connection refused:** enable the local server in LM Studio's Developer tab.
- **Model not found:** verify the loaded model id matches `qwen/qwen3.5-9b` in your script.
- **Empty output:** ensure `/no_think` is in the system prompt, or raise `max_tokens` to accommodate hidden reasoning output.
- **Slow inference:** switch from GGUF to MLX quantization on Apple Silicon.
