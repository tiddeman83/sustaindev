# VS Code Adapter

A `.vscode/tasks.json` package for the SustainDev scheduling and probe scripts. Lets you run all six probes from VS Code's Command Palette (Ctrl/Cmd+Shift+P → `Tasks: Run Task`) without typing the full paths.

## What this is

[VS Code Tasks](https://code.visualstudio.com/Docs/editor/tasks) are JSON-defined parameterized commands that run in VS Code's integrated terminal. The user picks a task from the palette, fills in any `inputs` (free text, picklists, env-defaults), and the task executes.

This adapter ships a `tasks.json.template` with six tasks wrapping SustainDev's probes plus the queue scripts. Once installed into your project's `.vscode/`, the tasks appear in the palette under names starting with `SustainDev —`.

## Quick install

From your project root (not the SustainDev checkout):

```sh
~/sustaindev/adapters/vscode/install.sh
```

This copies `tasks.json.template` to `<your-project>/.vscode/tasks.json`. If you already have a `tasks.json`, the installer prints a merge instruction instead of overwriting.

## What each task does

| Task | What it runs | Inputs |
|------|--------------|--------|
| `SustainDev — Capture idea` | `capture-idea.sh` | priority (pickString: low/medium/high), title (promptString) |
| `SustainDev — List queue` | `list-queue.sh` | optional status filter, optional priority filter |
| `SustainDev — Prepare task (local model)` | `prepare-task.py` | captured-id (promptString), optional flags |
| `SustainDev — Triage files (local model)` | `triage-files.py` | optional flags |
| `SustainDev — Draft service catalog (local model)` | `draft-catalog.py` | optional flags (services-root, max-files) |
| `SustainDev — Extract risks (local model)` | `extract-risks.py` | doc-path (promptString), severity-scale (pickString) |

## Configuration

The `tasks.json.template` resolves the SustainDev install path via an `input` named `sustaindevHome` that defaults to `${env:HOME}/sustaindev`. On first run of any task, VS Code prompts you for the path; subsequent runs use the cached value within the session.

For permanent configuration, set the env var globally:

```sh
# In ~/.zshrc or ~/.bashrc:
export SUSTAINDEV_HOME=~/sustaindev
```

Then in `tasks.json` change the input default to `${env:SUSTAINDEV_HOME}` (the installer doesn't do this automatically because it depends on user shell config).

## Customization

The `tasks.json` is a regular VS Code config — edit it freely. Common tweaks:

- **Tighten the input set.** If you always use `--sample-rate 0.1` on triage, hardcode it in the task's `args` and remove the input.
- **Add presentation tweaks.** `"presentation": { "panel": "dedicated" }` opens each task in its own terminal pane.
- **Bind to a keybinding.** Add to `keybindings.json`: `{ "key": "cmd+alt+t", "command": "workbench.action.tasks.runTask", "args": "SustainDev — Triage files (local model)" }`.

## Limits

These tasks are thin wrappers. The probe scripts have their own pre-flight checks, error messages, and post-processing — VS Code Tasks don't add or hide anything. If LM Studio isn't running, you'll see the same error as if you ran the script directly in the terminal.

## See also

- [`adapters/vscode/usage.md`](usage.md) — full setup, prerequisites, troubleshooting.
- [`adapters/lm-studio/usage.md`](../lm-studio/usage.md) — LM Studio side of the setup.
- [`adapters/warp/`](../warp/) — equivalent for Warp's terminal Workflows.
- [`docs/adoption/getting-started.md`](../../docs/adoption/getting-started.md) — the 30-minute first run.
