# Sprint 1 Test: Local Model Draft

Smallest meaningful test of the local-model prework tier. Drafts `core/rules/token-efficiency.md` via Qwen 3.5 9B running in LM Studio, captures measurement data, then I (the cloud reviewer) review and finalize.

## Prerequisites

- LM Studio installed.
- Qwen 3.5 9B (MLX 4-bit recommended) loaded.
- Local server enabled, default `http://127.0.0.1:1234`.
- Python 3.9+ on your Mac (preinstalled on macOS).

## Run

From the repo root:

```bash
python3 scripts/sprint1/run_prework.py
```

If your loaded model has a different id than the default `qwen3.5-9b`, override it:

```bash
LM_STUDIO_MODEL="qwen/qwen3.5-9b" python3 scripts/sprint1/run_prework.py
```

(The script will list the loaded models on startup so you know what to pass.)

## Outputs

```text
scripts/sprint1/output/
  draft.md           <- the model's raw draft (cleaned: <think> stripped, reasoning fields handled)
  raw_response.json  <- full unmodified LM Studio response (for debugging)
  measurement.json   <- timing + token counts
  run.log            <- console log
```

## Note on Qwen 3.x Thinking Mode

Qwen 3 / Qwen 3.5 default to a reasoning ("thinking") mode that fills `message.reasoning_content` or wraps content in `<think>…</think>` tags. For drafting tasks like ours, that wastes tokens and often leaves `message.content` empty when the budget is hit during reasoning.

The system prompt starts with `/no_think` to tell the model to skip reasoning. The script also defensively strips `<think>` tags and falls back to `reasoning_content` if `content` is empty, so we never lose output.

If you ever want reasoning back (for harder tasks where chain-of-thought helps), remove the `/no_think` line from `system_prompt.md` and raise `LM_STUDIO_MAX_TOKENS` to ~8000.

## What Happens Next

Once the draft exists, I (Claude) will:

1. Read `output/draft.md` and `output/measurement.json`.
2. Review the draft for correctness, structure, and prose quality.
3. Write the final `core/rules/token-efficiency.md` (cloud-finalized version).
4. Add a corresponding cloud-token measurement to `docs/measurement/case-study-01.md` so we have the full before/after.

## Tunables

Set as environment variables before running:

| Variable | Default | What it does |
|----------|---------|--------------|
| `LM_STUDIO_URL` | `http://127.0.0.1:1234/v1/chat/completions` | LM Studio endpoint |
| `LM_STUDIO_MODEL` | `qwen/qwen3.5-9b` | Loaded model id (matches LM Studio's namespaced id) |
| `LM_STUDIO_TEMPERATURE` | `0.3` | Lower = more deterministic |
| `LM_STUDIO_MAX_TOKENS` | `4000` | Cap on completion length (generous: leaves room even if reasoning leaks in) |
| `LM_STUDIO_TIMEOUT` | `600` | Request timeout in seconds |

## If It Fails

- **Connection refused:** LM Studio's local server isn't running. In LM Studio, open *Developer* → enable *Local Server* on port 1234.
- **Model not found:** override `LM_STUDIO_MODEL` to match the id LM Studio prints when listing loaded models. The script logs this on startup.
- **Timeout:** the model is too slow on this hardware for the chosen `MAX_TOKENS`. Lower `LM_STUDIO_MAX_TOKENS` to `800` or pick a smaller model.
- **Empty / nonsense draft:** Qwen 3.5 9B is multimodal — make sure you loaded the text/instruct variant, not a vision-only build.
