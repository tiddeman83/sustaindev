# Frequently Asked Questions

Anticipated questions from someone who has read [`docs/measurement/v0.1.x-lessons.md`](../measurement/v0.1.x-lessons.md) and is deciding whether to adopt SustainDev. Or who tried [`docs/adoption/getting-started.md`](getting-started.md) and hit something this doc covers.

If your question isn't here: open an issue. Adding to the FAQ from real adopter questions is a high-value contribution.

---

## Setup and hardware

### Q. I'm on Windows. Does this work?

The Python probe scripts work on Windows. The shell scripts (`capture-idea.sh`, `list-queue.sh`) are POSIX — they run on WSL or Git Bash but not on plain `cmd.exe`. The hero workflow's `idea-to-prepared-task` skill assumes the shell wrappers; if you're Windows-only, invoke the Python equivalents directly:

```sh
# Instead of capture-idea.sh, write the captured stub by hand following
# the format in core/scheduling/templates/scheduled-task.md.
# Then run prepare-task.py directly.
python scripts/schedule/prepare-task.py <captured-id>
```

A Windows-native shell-script port is on the v0.2 backlog but not yet built.

### Q. I only have 8 GB of RAM. Can I still use this?

Yes, but with constraints. Use Qwen 2.5 Coder 7B (Q4_K_M GGUF) instead of Qwen 3.5 9B. Set context to 8k, not 16k. Expect slower inference and tighter prompt budgets — you may need to drop one or two project layer files via `--exclude-file` to fit.

The v0.1.x case studies were measured on 16-24 GB. At 8 GB, you're in unmeasured territory but the pattern should still hold.

### Q. I want to use a different local model. Will it work?

Probably, with caveats. The probe scripts speak the OpenAI-compatible chat completions API; any local server that exposes that interface works (Ollama, llama.cpp's HTTP server, etc.). Pass the model id via `LM_STUDIO_MODEL=<id>` and the endpoint via `LM_STUDIO_URL=<url>`.

What changes:

- The `/no_think` directive only works on Qwen 3.x. Other models will probably ignore it. You may see different reasoning-leakage patterns.
- Smaller models (1B-3B) tend to fail the structured-output requirement more often. Plan for more post-processing intervention.
- Larger models (32B+) may have lower reasoning ratios and produce cleaner first-attempt output. Wall-clock will be longer per token.

The matrix in `core/rules/model-routing.md` was measured against Qwen 3.5 9B specifically. Treat its predictions as model-specific until you re-measure on yours.

### Q. Does this work with cloud models?

The probe scripts call any OpenAI-compatible endpoint. You can point them at Anthropic / OpenAI / etc. instead of a local server.

But the *value proposition* is local-tier prework: cheap, structured, draft-quality work where wall-clock latency is acceptable. If you route prework to the cloud, you're paying for tokens the local tier handles for free. The router separates local-prework from cloud-finish on purpose.

If you don't have suitable local hardware: the cloud-tier hero workflow (Cowork or Claude Code preparing a brief, then Codex executing it) is documented in case-study-02. That's a complete fallback.

---

## Model behavior

### Q. Why does the model leak reasoning into the output?

Qwen 3.x has a built-in reasoning mode. The `/no_think` directive in the system prompt asks the model to skip reasoning, but it's a hint, not a hard control. Where reasoning lands depends on context size and output budget:

- **Tight budget**: reasoning has nowhere to go and leaks into visible output as "Thinking Process:" preambles.
- **Generous budget at moderate context**: reasoning channels properly to the `reasoning_content` field; visible output is clean.
- **Generous budget at large context**: model invests all output in reasoning_content; visible output is empty.

This is documented in detail in case-study-05 + case-study-06 and summarized in [`v0.1.x-lessons.md` "The Three Reasoning Regimes"](../measurement/v0.1.x-lessons.md). The probe scripts in v0.1.6+ defend against all three modes via `scripts/lib/postprocess.py`.

### Q. What max_tokens should I set?

Just high enough to keep reasoning channeled. Not as high as possible.

Rules of thumb derived from v0.1.x:

- Idea triage of ~50 files: **3,000-4,000** is enough.
- Catalog drafting of ~10 service interfaces: **8,000**.
- Summarization of a 40 KB doc: **8,000-12,000** (and bump LM Studio context to 32k).
- Risk extraction from a 3 KB doc: **3,000**.

The probe scripts have sensible defaults; override only when you understand what you're trading.

### Q. The model gave me wrong arithmetic in the counts line. Is this a bug?

No, it's the model. Counting its own output drifts under load. The probe scripts in v0.1.3+ recompute counts in post-processing — `triage-files.py` will show "verified by post-processing" on its counts line. If you see counts that don't match the actual table rows, you're either on an older version or your script bypassed the post-processor.

### Q. Should I trust the model's hallucinated facts?

The model generally doesn't hallucinate **structural** facts (file paths, method signatures, severity tags from the source). It can hallucinate **semantic** facts (a wrong test fixture path inferred from "tests mirror App layer"; a generic explanation of a service that doesn't quite match the actual code).

Treat the output as a draft. The synthesis doc's "What Worked, What Didn't" section names what's safe vs what isn't.

---

## When does this work / when does it not?

### Q. Which tasks are unconditionally strong-fit?

As of v0.1.7, two:

1. **Idea expansion** (rough capture → structured task brief). case-study-03.
2. **Risk extraction from prose** (small bounded source → structured table). case-study-07.

The shared profile: bounded input + bounded structured output + project-aware context.

### Q. Which tasks are conditionally strong-fit?

Three, each with task-class-specific conditions:

1. **Idea triage / classification** — needs `RISKS.md` and `MAINTAINABILITY_NOTES.md` in context, plus human spot-check on edge cases.
2. **Codemap drafts from file lists** — needs sufficient `--max-tokens` (~8k for ~12 service files); reasoning consumes 50-70% of budget.
3. **Summarization of long documents** — needs post-processing to extract the artifact from wherever the model put it.

Don't use these without the conditions met. With the conditions met, they work.

### Q. What's the weak-fit case I should avoid?

Full-document drafting from a rich brief. The model's reasoning overhead and wall-clock cost make it cheaper to use a cloud model for this. case-study-01 measured this directly. Use the cloud tier for any task that produces a complete document from scratch.

### Q. Why is the matrix only 6 of 10 measured?

We ran out of session time. The remaining four rows (adapter templates, cross-document consistency checks, time-critical authoring, batch/overnight prework) are predicted from the pattern of the measured rows but not yet validated. v0.2 will fill them in. If you have a project where you can test one of these, sharing the measurement report is high-value.

---

## Failure modes

### Q. The first time I ran a probe, output came back empty. What happened?

Three possibilities:

1. **`/no_think` failed and reasoning ate the whole budget.** Raise `--max-tokens` and re-run. Common at first attempts.
2. **Model returned content in `reasoning_content` instead of `content`.** v0.1.6+ scripts handle this via fallback; check the JSON measurement file's `fallback_used` field. If it's `true`, the script rescued the data.
3. **You hit `n_keep > n_ctx`.** Pre-flight check in v0.1.2+ catches this; if you're seeing it from the model side, your LM Studio context is too small. Bump it and reload the model.

### Q. The model classified an obvious file completely wrong. Now what?

Two choices:

1. **Manual override.** Open the markdown output, change the classification yourself. The point is the human-readable artifact, not blind trust in the model.
2. **Adjust the system prompt.** If you see a systematic failure (the model always puts `.gitkeep` files in `build-artifact`, say), edit the script's system prompt to add a rule for that case. v0.1.3 added the `.gitkeep` rule for this reason.

### Q. The probe takes 10+ minutes. Is something broken?

Probably not, but check:

- Activity Monitor: is the model swapping pages to disk? You may have less RAM than the model needs. Try a smaller model.
- LM Studio: is GPU acceleration enabled (Apple Silicon → Metal backend)? Performance settings under the model.
- Throughput: roughly 14-30 tokens per second on M-series at MLX 4-bit is normal. Less than 10 tok/s usually means swapping.

### Q. I see post-processing notes I don't understand in the output JSON. What do they mean?

The probe scripts log every defensive intervention they made. Common ones:

- `"visible content was empty; using reasoning_content as fallback"` — the model emitted everything in the wrong channel; the script rescued it.
- `"extracted last draft from 14000-char text (now 800 chars)"` — the model produced multiple drafts during reasoning; the script kept only the last one.
- `"removed 1 duplicate section(s): ['IFooService']"` — the model emitted the same section twice; the script kept only the first occurrence.
- `"stripped planning preamble before first H1"` — the model led with "Thinking Process:" prose; the script jumped to the actual artifact.

These are working as designed. The notes exist so you can see what the script changed and decide whether to trust the change.

---

## Writing your own probe

### Q. How do I write a new probe script?

Start from `scripts/sprint1/extract-risks.py` — it's the cleanest template (the first probe written against the v0.1.6 shared utilities). Copy it; adapt the system prompt, the input gathering, and the output structure for your task class. Most of the boilerplate stays the same.

Pattern:

1. `argparse` for CLI.
2. Pre-flight token check against `--lm-studio-context`.
3. Build the prompt: read project layer files, read input, format user message.
4. Call LM Studio (the `call_lm_studio` function is roughly identical across probes).
5. `extract_content` to get content + reasoning, with fallback.
6. Run through the post-processing pipeline from `scripts/lib/postprocess`.
7. Write markdown + JSON to `.sustaindev/measurement/`.

A new probe takes ~30 minutes of focused work.

### Q. How do I add my own post-processing utility?

Add it to `scripts/lib/postprocess.py`. Use the existing utilities as templates:

- Pure functions, no global state.
- Stdlib only (no external deps).
- Type-annotated.
- One docstring per function explaining what it defends against and citing the case study where the failure mode surfaced.

Submit a PR. Bonus points: include a short test exercising the function in isolation.

### Q. Should I write a test suite for my probe?

For v0.1.x there's no formal test framework. The probes themselves are tested by their `--dry-run` mode (which validates the prompt construction) and by the case studies that ran them. If you're shipping a probe to others, consider writing pytest assertions against `scripts/lib/postprocess` since that's the reusable surface.

A v0.2 priority is a proper test suite for the shared utilities.

---

## Comparison and alternatives

### Q. How is this different from Cursor / Continue.dev / Aider / Cline / Claude Code rules?

Those are tool-bound prompt repositories — rules and skills that live inside one editor or one CLI. SustainDev is the cross-tool layer above them: durable knowledge in `core/`, thin per-tool adapters in `adapters/`, plus a measurement layer (`docs/measurement/`) that documents what actually works.

Specifically, SustainDev gives you:

- **An explicit local-model prework tier** with objective routing rules.
- **Maintainability as a required output** of every workflow.
- **A measurement methodology** so claims are evidence-backed.

If you only use one AI tool and you're happy with its native rules system, you may not need SustainDev. If you bounce between Cursor, Claude Code, Codex, and a local model, the cross-tool layer is the value.

See [`docs/positioning.md`](../positioning.md) for a fair, specific comparison against named alternatives.

### Q. Is this just a prompt collection?

No. The case studies measure actual model behavior on actual projects, the probe scripts ship as reusable infrastructure, and the routing matrix is empirically backed for 6 of 10 task classes. The repository's value is in the *measurement engine* and the *script-side defensive patterns*, not in the prompts themselves.

You could lift the prompts. You'd reinvent the post-processing pattern.

### Q. Why should I trust this?

You shouldn't, blindly. The case studies are designed for skeptical reading: each one has a "What This Does Not Prove" section, raw measurement JSON, and reproducibility notes. If you don't trust a finding, you can rerun the probe on your project and check.

What v0.1.x earned: 7 case studies, 6 of 10 matrix rows backed, defensive code that handles real failure modes. That's evidence; it's not certainty. Use it as a starting point for your own measurements.

---

## Getting unstuck

### Q. None of this worked for me. What now?

Open an issue. Include:

- Your hardware (chip, RAM, OS).
- Your LM Studio version and loaded model id.
- Your `.sustaindev/measurement/<probe>-<timestamp>.json` (the measurement record has the configuration + outcome).
- A description of what you expected vs what happened.

The measurement records are designed to be the audit trail; they have everything the maintainer needs to debug.

### Q. I want to skip all this and just use a cloud model.

Reasonable. The hero workflow's prepare-task step has been validated against cloud reasoning models too — point `LM_STUDIO_URL` at any OpenAI-compatible endpoint and pass the right model id. You'll spend cloud tokens on prework that the local tier handles free, but the workflow itself works.

The reason to use the local tier is the cost ratio over time, not the per-task experience. If you only run probes occasionally, cloud-only is fine.

### Q. I want to contribute. Where do I start?

Three high-value contributions:

1. **A measurement report from your own project.** Use [`.github/ISSUE_TEMPLATE/measurement_report.md`](../../.github/ISSUE_TEMPLATE/measurement_report.md). The community measurement repository is the most valuable thing the project can grow.
2. **A new probe script.** Pick a strong-fit row that's still theoretical (`adapter templates`, `cross-document consistency`, `batch / overnight prework`) and write the probe + run it + write up the case study.
3. **An adapter port.** Warp / VS Code / Cursor / Cline rules export — original v0.2 roadmap items. Each one expands the project's reach.

`CONTRIBUTING.md` has the quality bar and the per-layer ownership rules.
