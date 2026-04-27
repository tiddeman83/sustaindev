# Warp Adapter Usage

Full setup, prerequisites, and troubleshooting for the SustainDev Warp Workflows package.

## Prerequisites

- [Warp](https://www.warp.dev/) installed and running.
- SustainDev cloned somewhere on your filesystem. The default install assumes `~/sustaindev`; pass `WARP_WORKFLOWS_DIR` and edit the YAML commands if you keep it elsewhere.
- LM Studio installed and a model loaded for the probe-script workflows (`Prepare task`, `Triage files`). Schedule workflows (`Capture idea`, `List queue`) work without LM Studio — they only touch local files.
- The SustainDev project layer set up in your target project (PROJECT_CONTEXT.md, CODEMAP.md, etc.). See [`docs/adoption/getting-started.md`](../../docs/adoption/getting-started.md) for the layer setup.

## What gets installed

`./adapters/warp/install.sh` copies four YAML files into your Warp launch_configurations directory:

- `capture-idea.yaml` — schedule the queue's capture step
- `list-queue.yaml` — print queue contents
- `prepare-task.yaml` — local-model brief drafting from a captured stub
- `triage-files.yaml` — local-model file classification on `git status`

Default destination: `~/.warp/launch_configurations/` (current Warp versions). The installer falls back to `~/.warp/workflows/` if that's where Warp put your existing workflows. Override with `WARP_WORKFLOWS_DIR`.

The four files are visible in Warp's command palette (Cmd+Shift+R) under names starting with `SustainDev —`.

## Running a workflow

1. **Cmd+Shift+R** anywhere in Warp.
2. Type `SustainDev` to filter.
3. Pick the workflow.
4. Fill in the arguments. Each argument's description is visible in the right panel.
5. Hit Enter. Warp runs the underlying script in your current directory.

The probe-script workflows produce output to your terminal as the script runs. Output also lands in `.sustaindev/measurement/` per the script's normal behavior.

## Common adjustments

### Different SustainDev install location

The four YAMLs hardcode `~/sustaindev` as the install path. If yours differs:

```sh
sed -i '' 's|~/sustaindev|/path/to/your/install|g' ~/.warp/launch_configurations/SustainDev*.yaml
```

(BSD `sed` syntax for macOS; Linux drops the `''` after `-i`.)

A v0.2.x improvement on the roadmap is `${SUSTAINDEV_HOME:-~/sustaindev}` in the YAMLs to make this configurable via env var. Tracking issue welcome.

### LM Studio at a non-default port

The probe-script workflows inherit the script's defaults. If your LM Studio runs on a different port, set `LM_STUDIO_URL` in your shell before opening Warp:

```sh
export LM_STUDIO_URL=http://127.0.0.1:1235/v1/chat/completions
```

Add to `~/.zshrc` to persist.

### Different model or context

Set the env vars in your shell:

```sh
export LM_STUDIO_MODEL="qwen/qwen2.5-coder-7b"   # if you're using a fallback model
export LM_STUDIO_CONTEXT="32768"                  # if you raised LM Studio's context
```

The probe scripts pick these up automatically.

## Troubleshooting

**Cmd+Shift+R doesn't show SustainDev workflows.**

Possible causes:

- `install.sh` ran but Warp hasn't refreshed its workflow list. Quit Warp fully (Cmd+Q) and reopen.
- Workflows landed in the wrong directory. Check `~/.warp/launch_configurations/` and `~/.warp/workflows/` for `SustainDev*.yaml` files. Move to the directory Warp watches.
- YAML parse error. In Warp, check the developer console (Cmd+Option+I) for messages.

**Workflow runs but says "command not found".**

The script path in the YAML doesn't match where SustainDev is actually checked out. Edit the YAMLs (see "Different SustainDev install location" above).

**Workflow runs but the underlying script fails.**

This is not a Warp problem; it's the script's own validation. Run the same command directly in the terminal (without going through Warp) and you'll see the same error. Common script-level issues:

- LM Studio not running: connection refused.
- Project layer files missing: warnings about missing PROJECT_CONTEXT.md / CODEMAP.md (but the script proceeds with reduced context).
- Pre-flight context check failed: prompt exceeds your `--lm-studio-context`. Either raise LM Studio's context, lower `--max-tokens`, or pass `--exclude-file` to drop a project layer file.

See [`docs/adoption/faq.md`](../../docs/adoption/faq.md) for the full failure-mode catalog.

**The workflow prompts for an argument I left blank.**

Warp Workflows treat blank arguments as empty strings, which is fine for optional flags (the YAML's `extra_flags` argument default is `""`). If a required argument is blank (like `title` for capture-idea), the underlying script will exit with a clear error. Re-run with the argument filled in.

## What this adapter is not

These workflows are thin wrappers around the SustainDev scripts. They don't implement any new behavior. If a workflow does something unexpected, the cause is in the script (`scripts/schedule/*` or `scripts/sprint1/*`), not in the YAML.

The Warp-specific value is *discoverability* — the four most-used SustainDev commands are one keypress away from anywhere in your terminal. That's the entire promise.

## What's coming in v0.2.x

- `${SUSTAINDEV_HOME}` env var resolution in the YAMLs.
- Workflows for the catalog and risk-extraction probes (`draft-catalog.py`, `extract-risks.py`).
- A "first run" workflow that walks new users through the LM Studio setup interactively.
- Optional Warp Block-style output formatting for the verified counts line (so the bucket totals are visually distinct from the table).

If you'd find any of these compelling: open an issue with your use case.
