# LM Studio Adapter

## Purpose

This adapter provides a reliable local-prework execution tier for development workflows. It routes specific, structured tasks to a local model running via LM Studio to conserve cloud tokens. It does not replace the cloud tier; instead, it serves as a specialized engine for tasks where wall-clock latency is acceptable and reasoning overhead is minimal. 

## Prerequisites

- LM Studio installed on your host machine.
- Supported hardware capabilities.
- The specifically recommended model downloaded and loaded.

## Recommended Model

The primary target is **Qwen 3.5 9B at MLX 4-bit quantization**, tailored for Apple Silicon at 16–24 GB of unified memory. Note that MLX quantization runs approximately 15–30% faster than GGUF on Apple Silicon and uses roughly 10% less memory, making it the superior format for this hardware class. Qwen 2.5 Coder 7B serves as a highly capable fallback for older Apple Silicon hardware (like the M1 with 8 GB of memory) or non-MLX setups. Codestral 22B stands as an excellent alternative for users equipped with discrete GPUs or 64GB+ unified memory.

## Setup

1. Download LM Studio directly from `https://lmstudio.ai`.
2. In LM Studio, search the catalog for and download the `qwen/qwen3.5-9b` MLX 4-bit variant.
3. Open the *Developer* tab within the LM Studio interface and enable the local server (which defaults to port 1234).
4. Confirm the server is reachable by running: `curl http://127.0.0.1:1234/v1/models`.

## Configuration

For reliable prework results, configure the local model appropriately. Set the temperature to 0.3 for a more deterministic, structured output. Set the context length to a generous but realistic value based on your hardware; while the Qwen model supports up to 262k natively, setting the context in LM Studio to a value like 32k is comfortable for 16GB systems without causing memory swapping. For Qwen 3.x models, always include the `/no_think` directive in the system prompt to explicitly suppress reasoning overhead on tasks that categorically do not benefit from chain-of-thought generation.

## What This Adapter Is Good For

- **Idea triage and classification:** The output is tiny, inference is extremely fast, and the cloud token savings become real at scale.
- **Codemap drafts from file lists:** The model effectively extracts patterns and benefits immensely from large context windows.
- **Summarization of long documents:** The task strictly bounds the output while taking full advantage of the 262k context window.
- **Risk extraction from existing prose:** The task relies heavily on pattern-matching where structure matters far more than nuanced prose quality.
- **Idea expansion:** Transforming a rough capture into a structured task brief works perfectly when latency is acceptable because the user has already stepped away.
- **Batch or overnight prework:** The wall-clock cost is functionally zero because execution happens asynchronously.

## What This Adapter Is Not Good For

- **Full-document drafting:** The reasoning overhead and severe wall-clock cost vastly outweigh any marginal cloud token savings.
- **Adapter templates:** Generating tool-specific adapters requires accurate technical knowledge that 9B class models frequently hallucinate or get entirely wrong.
- **Cross-document consistency checks:** The sheer wall-clock penalty is far too high for interactive, active development sessions.
- **Time-critical authoring:** When the user is actively waiting on the output, the accumulated latency is completely unacceptable. 

For empirical backing of these limitations, refer to the measurements detailed in `docs/measurement/case-study-01.md`.

## Integration with the Hero Workflow

The `idea-to-prepared-task` skill (`core/skills/idea-to-prepared-task/SKILL.md`) natively utilizes this adapter for the preparation step whenever the user explicitly opts in. The adapter remains strictly optional; users who prefer a purely cloud-only execution environment can skip the local tier entirely without breaking the hero workflow.

## Honest Limitations

Local-model quality varies significantly depending on the exact hardware running the inference. Token counts measured between LM Studio and cloud APIs utilize fundamentally different tokenizers and absolutely do not compare apples-to-apples. The reasoning-mode behavior built into Qwen 3.x models can consume significant portions of the token budget; utilizing the `/no_think` directive helps significantly but does not fully eliminate the underlying generation overhead. The 215-second wall-clock duration measured precisely in case-study-01 is highly realistic for this specific hardware tier on a roughly 500-word document generation task. Your actual mileage will naturally vary based heavily on task complexity, prompt structure, and system load.

## Troubleshooting

- **Connection refused:** Ensure you have fully enabled the local server inside LM Studio's Developer tab.
- **Model not found:** Verify that the loaded model id string matches exactly `qwen/qwen3.5-9b` in your script parameters.
- **Empty output:** Ensure the `/no_think` directive is correctly placed in the system prompt or raise your `max_tokens` limit substantially to accommodate hidden reasoning output.
- **Slow inference:** Switch your model file directly from GGUF to MLX quantization, which handles memory far more efficiently on Apple Silicon.
