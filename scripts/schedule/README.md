# Scripts: Schedule

Three scripts implementing the file-based scheduling workflow that backs the `idea-to-prepared-task` hero skill.

| Script | Purpose | Language |
|--------|---------|----------|
| `capture-idea.sh` | Capture a rough idea as a stub in `queue/captured/`. | POSIX shell |
| `prepare-task.py` | Turn a captured stub into a structured brief via local model. | Python 3 |
| `list-queue.sh` | Print a summary of all queued tasks across the four queue directories. | POSIX shell |

## Queue Layout

The scheduling system uses a four-stage queue. Default location is `core/scheduling/queue/` (when SustainDev is the project itself) or `.sustaindev/queue/` (when SustainDev is adopted by another project).

```text
queue/
  captured/         <- raw ideas, just-captured stubs
  prework-ready/    <- briefs prepared by prepare-task, awaiting human triage
  scheduled/        <- triaged briefs, queued for execution at chosen time
  completed/        <- executed tasks with retrospective notes
```

Each script auto-detects which root to use, or accepts an explicit `--queue-root` / argument.

## Quickstart

End-to-end loop for one idea:

```sh
# 1. Capture the idea
./scripts/schedule/capture-idea.sh "add csv export to report screen"
# -> writes queue/captured/2026-MM-DD-add-csv-export-to-report-screen.md

# 2. Prepare it (calls LM Studio at 127.0.0.1:1234 by default)
python3 scripts/schedule/prepare-task.py 2026-MM-DD-add-csv-export-to-report-screen
# -> reads PROJECT_CONTEXT.md, CODEMAP.md, AI_POLICY.md, MAINTAINABILITY_NOTES.md, VERIFY.md
# -> calls the local model
# -> writes queue/prework-ready/<id>.md
# -> removes the captured stub

# 3. Review and (optionally) move to scheduled/
mv queue/prework-ready/<id>.md queue/scheduled/<id>.md

# 4. List what's queued
./scripts/schedule/list-queue.sh
```

## prepare-task.py: Local-only by Design

The prepare step calls a local LM Studio instance by default. There is no cloud fallback — the design assumes you want the prework tier to actually be cheap. If LM Studio is unreachable, the script exits with a clear error pointing at `adapters/lm-studio/usage.md`.

### Prerequisites

- LM Studio installed.
- A model loaded (recommended: Qwen 3.5 9B at MLX 4-bit on Apple Silicon; Qwen 2.5 Coder 7B as a fallback). See `adapters/lm-studio/usage.md`.
- Local server enabled (Developer tab → port 1234).
- Python 3.9+ (preinstalled on macOS, standard on Linux distros).

### Common Patterns

**Dry-run** — see the constructed prompt without calling the model:

```sh
python3 scripts/schedule/prepare-task.py <captured-id> --dry-run
```

**Use a different loaded model:**

```sh
LM_STUDIO_MODEL="qwen/qwen2.5-coder-7b" python3 scripts/schedule/prepare-task.py <captured-id>
```

**Smaller token budget** for tighter outputs (and lower latency):

```sh
python3 scripts/schedule/prepare-task.py <captured-id> --max-tokens 2000
```

**Skip the human-review queue** and go straight to scheduled:

```sh
python3 scripts/schedule/prepare-task.py <captured-id> --output-status scheduled
```

**Explicit project + queue paths** (useful when invoking from elsewhere):

```sh
python3 scripts/schedule/prepare-task.py <captured-id> \
  --project-root /path/to/project \
  --queue-root /path/to/project/.sustaindev/queue
```

### What the Script Reads

When preparing a brief, the script attempts to read these files from the project root (warns and continues on missing files):

- `PROJECT_CONTEXT.md` — what the project is, tech stack, architecture.
- `CODEMAP.md` — file/module map; provides file-targets to the model.
- `AI_POLICY.md` — what AI tools may and may not touch.
- `MAINTAINABILITY_NOTES.md` — project-specific maintainability dimensions.
- `VERIFY.md` — build/test/run commands; provides verify-commands to the model.

Two intentional exclusions: `DECISIONS.md` and `RISKS.md` are not loaded by default (they tend to be longer and v0.2-era models have limited context). If your local model has the room, edit `PROJECT_LAYER_FILES` near the top of the script.

### What the Script Writes

- `<queue-root>/<output-status>/<captured-id>.md` — the prepared brief.
- `<queue-root>/../measurement/prepare-<captured-id>.json` — a measurement record (wall-clock, tokens, validation issues).

The captured stub is moved (deleted from `captured/`) by default. Pass `--keep-captured` to leave it in place.

### Validation

After receiving the model's response, the script validates that the output:

- Starts with `# Scheduled Task: `.
- Contains YAML front matter delimiters.
- Contains all the required H2 sections (Captured Idea, Scope, File Targets, Verify Commands, Maintainability Constraints, Success Criteria, Retrospective).

If validation fails, the brief is still written but warnings are printed and recorded in the measurement JSON. Treat a failed-validation brief as draft material that needs manual cleanup before it goes to a cloud tool for execution.

### Reasoning Mode (Qwen 3.x)

Qwen 3 / Qwen 3.5 default to a reasoning ("thinking") mode that fills `message.reasoning_content` or wraps content in `<think>…</think>` tags. The system prompt starts with `/no_think` to suppress this. The script also defensively strips `<think>` blocks and falls back to `reasoning_content` if `content` is empty. This is the same pattern used in `scripts/sprint1/run_prework.py`.

If you ever want chain-of-thought reasoning (rare, for harder briefs): edit `SYSTEM_PROMPT` in the script and raise `--max-tokens` to ~8000.

## Troubleshooting

**Connection refused** — LM Studio's local server is not running. Open Developer tab in LM Studio and enable the server.

**Model not found** — the loaded model id does not match `qwen/qwen3.5-9b`. Override with `LM_STUDIO_MODEL=...` or `--model ...` to match the id LM Studio exposes (run `curl http://127.0.0.1:1234/v1/models` to list).

**Empty output** — `/no_think` is missing or `--max-tokens` is too low. Default is 4000; raise to 6000-8000 for complex briefs.

**Slow inference** — switch from GGUF to MLX quantization on Apple Silicon. See `adapters/lm-studio/usage.md`.

**Validation issues on every run** — the model is producing output that doesn't follow the structure. Try lower temperature (`--temperature 0.1`), or fall back to a smaller / different model that follows instructions more rigidly.

## Why Python (not Shell)

The capture and list scripts are POSIX shell because they do simple file operations. `prepare-task` calls an HTTP API, parses JSON, handles multi-step error recovery (think tags, reasoning_content fallback, validation), and constructs a multi-document prompt. Doing that in shell would require curl + jq plus fragile string handling. Python gives us all this with zero external dependencies (urllib + stdlib only) on every modern macOS and Linux.

## Limits

- One captured stub at a time. Batch processing across multiple stubs is a v0.2 idea.
- No retry logic on transient LM Studio failures. If the call fails, re-run.
- No caching of project layer files between runs. The model re-reads each time.
- The validation is structural, not semantic. A brief with all the right sections but nonsense content will pass validation but is still nonsense; the human triage step in `prework-ready/` exists exactly to catch that.
