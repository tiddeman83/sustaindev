# Warp Adapter

A Warp Workflows package for the SustainDev scheduling scripts. Lets you run `capture-idea`, `prepare-task`, `list-queue`, and `triage-files` from Warp's command palette without typing the full paths.

## What this is

[Warp Workflows](https://docs.warp.dev/features/warp-workflows) are YAML-defined parameterized commands. Once installed, you trigger them from Warp via Cmd+Shift+R (the Workflow palette) or by typing the workflow name.

This adapter ships four workflows that wrap SustainDev's scheduling and probe scripts. Each workflow prompts for the arguments it needs and runs the underlying script with your inputs.

## Quick install

From the repo root:

```sh
./adapters/warp/install.sh
```

This copies the four workflow YAML files to `~/.warp/launch_configurations/` and reports which ones landed.

To use, open Warp, hit Cmd+Shift+R, search for `SustainDev`, pick a workflow, fill in the arguments, run.

## What each workflow does

| Workflow | What it runs | Common arguments |
|----------|--------------|-------------------|
| `SustainDev — Capture idea` | `capture-idea.sh` with priority + title | priority (low/medium/high), title (free text) |
| `SustainDev — List queue` | `list-queue.sh` with optional filters | status (captured/prework-ready/scheduled/completed), priority |
| `SustainDev — Prepare task` | `prepare-task.py` against a captured stub | captured-id, optional max-tokens override |
| `SustainDev — Triage files` | `triage-files.py` against `git status` | optional sample-rate, optional max-files override |

## Customization

The workflow YAMLs use a fixed assumption: SustainDev is checked out at `~/sustaindev`. If yours lives elsewhere, edit the `command` line in each YAML to point at your install path.

A v0.2.x improvement on the roadmap is environment variable resolution (`SUSTAINDEV_HOME`) so the YAMLs work regardless of install location.

## Limits

These workflows are thin wrappers. The probe scripts themselves are the value; Warp Workflows just put them one keypress away from anywhere in the terminal. The scripts have their own pre-flight checks, error messages, and post-processing — Warp Workflows don't add or hide anything.

If LM Studio isn't running or your model isn't loaded, you'll see the same error messages as if you ran the script directly. Warp doesn't intercept.

## See also

- [`adapters/warp/usage.md`](usage.md) — full setup, prerequisites, troubleshooting.
- [`adapters/lm-studio/usage.md`](../lm-studio/usage.md) — LM Studio side of the setup (required before the probe-script workflows are useful).
- [`docs/adoption/getting-started.md`](../../docs/adoption/getting-started.md) — the 30-minute first run, framed for terminal-first users.
