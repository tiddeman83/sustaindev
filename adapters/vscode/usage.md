# VS Code Adapter Usage

Full setup, prerequisites, and troubleshooting for the SustainDev VS Code Tasks package.

## Prerequisites

- VS Code installed (or any editor that reads `.vscode/tasks.json` — Cursor and Cline both do).
- SustainDev cloned somewhere on your filesystem. The default install assumes `~/sustaindev`; the `sustaindevHome` input prompts on first run if elsewhere.
- LM Studio installed and a model loaded for the probe-script tasks (Prepare task, Triage files, Draft catalog, Extract risks). Schedule tasks (Capture idea, List queue) work without LM Studio — they only touch local files.
- The SustainDev project layer set up in your target project (PROJECT_CONTEXT.md, CODEMAP.md, etc.). See [`docs/adoption/getting-started.md`](../../docs/adoption/getting-started.md) for the layer setup.

## What gets installed

The installer copies `tasks.json.template` to `<your-project>/.vscode/tasks.json`. **It refuses to overwrite an existing tasks.json**; if you already have one, the installer prints a merge instruction.

The installed file defines six tasks plus ten input prompts.

## Running a task

1. **Cmd/Ctrl+Shift+P** in VS Code (or Cursor / Cline).
2. Type `Tasks: Run Task`. Hit Enter.
3. Pick a SustainDev task from the list.
4. Fill in the prompts as VS Code asks. The first prompt is always `sustaindevHome` — your install path. Enter once per session; VS Code remembers.
5. The task runs in the integrated terminal. Output streams there.

For the probe-script tasks, the underlying script writes its measurement output to `.sustaindev/measurement/` per the script's normal behavior.

## Common adjustments

### Permanent SustainDev path

Edit `.vscode/tasks.json` and change every `"default": "${env:HOME}/sustaindev"` to `"default": "${env:SUSTAINDEV_HOME}"`. Then set the env var globally:

```sh
# In ~/.zshrc or ~/.bashrc:
export SUSTAINDEV_HOME=~/sustaindev
```

VS Code reads env vars from your shell config when launched from the terminal. If you launch VS Code from the macOS Finder/Dock, you may need to add the env var to launchctl as well. Easier path: edit the default in tasks.json directly.

### Bind tasks to keyboard shortcuts

Add to your `keybindings.json`:

```json
[
  {
    "key": "cmd+alt+t",
    "command": "workbench.action.tasks.runTask",
    "args": "SustainDev — Triage files (local model)"
  },
  {
    "key": "cmd+alt+c",
    "command": "workbench.action.tasks.runTask",
    "args": "SustainDev — Capture idea"
  }
]
```

The `args` value must match the task's `label` exactly.

### Tighten the input set

The template uses generic `extra_flags` inputs for the probe scripts so users can pass any flag. If you always use the same flags, replace the input with hardcoded args:

```json
{
  "label": "SustainDev — Triage files (local model)",
  "type": "shell",
  "command": "python3",
  "args": [
    "${input:sustaindevHome}/scripts/sprint1/triage-files.py",
    "--sample-rate", "0.1"
  ]
}
```

Then remove the corresponding `triageExtraFlags` entry from `inputs`.

### Different LM Studio configuration

Set env vars in your shell before launching VS Code:

```sh
export LM_STUDIO_URL=http://127.0.0.1:1235/v1/chat/completions
export LM_STUDIO_MODEL=qwen/qwen2.5-coder-7b
export LM_STUDIO_CONTEXT=32768
```

The probe scripts pick these up automatically. The tasks pass them through unchanged.

## Troubleshooting

**Tasks: Run Task doesn't show SustainDev tasks.**

Possible causes:

- The installer ran but VS Code hasn't reloaded its task definitions. Cmd/Ctrl+Shift+P → `Developer: Reload Window`.
- The installer landed `tasks.json` somewhere unexpected. Check: open `.vscode/tasks.json` from the file explorer; confirm it has the SustainDev tasks.
- JSON parse error. VS Code shows JSON errors as red squigglies in the editor; open `tasks.json` and look for them.

**Task runs but says "command not found".**

The `sustaindevHome` input value doesn't match where SustainDev is checked out. On the first prompt, type the absolute path to your checkout (no `~` or `$HOME` shortcut here — VS Code passes the literal string to the shell).

**Task runs but the script fails.**

This is not a VS Code issue; it's the script's own validation. Open the same command in your terminal directly and you'll see the same error. See [`docs/adoption/faq.md`](../../docs/adoption/faq.md) for the failure-mode catalog.

**The `extra_flags` input only takes one flag at a time.**

VS Code's `promptString` input does pass the whole entered string as one argument when interpolated in `args`. To pass multiple flags, just type them with spaces:

```text
--max-files 200 --sample-rate 0.1
```

The shell receives the whole string as a single arg, but most flag parsers handle this fine because the script's argparse re-tokenizes.

If you hit edge cases (flags with spaces in values), wrap the call in `bash -c` or split the inputs into separate fields. v0.2.x will likely add a more structured input pattern.

**MCP integration?**

Some VS Code AI extensions (Continue.dev, Cline, etc.) support MCP servers. SustainDev doesn't ship an MCP server itself; its value is in the `core/` content + probe scripts + adapters. If your extension can read the `core/` files as context, point it at your SustainDev checkout. Specific extension configurations are out of scope for this adapter.

## What this adapter is not

These tasks are thin wrappers. They don't add new behavior; they make the existing tooling discoverable from VS Code's command palette. The Cursor and Cline editors both honor `tasks.json`, so this adapter works for them too with no modification.

## What's coming in v0.2.x

- `${env:SUSTAINDEV_HOME}` resolution by default (currently the default is `${env:HOME}/sustaindev`).
- A VS Code Extension that reads `core/` content directly and surfaces it as MCP context to compatible AI extensions.
- Snippets for the project-layer file templates (PROJECT_CONTEXT, CODEMAP, etc.).

If you'd find any of these compelling: open an issue with your use case.
