# Cursor / Cline Adapter Usage

Full setup, format options, and troubleshooting for the SustainDev rules-export adapter.

## Prerequisites

- Either Cursor or Cline (or both) installed.
- SustainDev cloned somewhere on your filesystem. The templates default to `~/sustaindev` for the core path; if your checkout lives elsewhere, edit the references in your installed `.cursorrules` / `.clinerules` after install.
- The SustainDev project layer set up in your target project: `PROJECT_CONTEXT.md`, `CODEMAP.md`, `VERIFY.md`, `AI_POLICY.md`, `MAINTAINABILITY_NOTES.md`, `DECISIONS.md`, `RISKS.md`. See [`docs/adoption/getting-started.md`](../../docs/adoption/getting-started.md) for the layer setup.

## Install

From your project root:

```sh
# both (default)
~/sustaindev/adapters/cursor-cline/install.sh

# cursor only
~/sustaindev/adapters/cursor-cline/install.sh --cursor

# cline only
~/sustaindev/adapters/cursor-cline/install.sh --cline

# install into a different directory
~/sustaindev/adapters/cursor-cline/install.sh --target /path/to/project
```

The installer copies the templates into the target directory and **refuses to overwrite an existing rules file**. If you already have a `.cursorrules` or `.clinerules`, the installer prints a manual-merge instruction and exits with status 3.

After install, open the file(s) and replace the `<project-name>`, one-line description, and project-paragraph placeholders.

## Format choices

### Cursor: `.cursorrules` vs `.cursor/rules/*.mdc`

Cursor reads two formats. The classic `.cursorrules` is a single markdown file at the project root. The newer `.cursor/rules/` directory holds one or more `.mdc` files, each with optional YAML frontmatter (`description`, `globs`, `alwaysApply`).

This adapter ships the classic `.cursorrules` form because it is the most widely supported and works in all current Cursor versions. If you prefer the directory format, run:

```sh
mkdir -p .cursor/rules
mv .cursorrules .cursor/rules/sustaindev.mdc
```

then open `.cursor/rules/sustaindev.mdc` and prepend YAML frontmatter:

```yaml
---
description: SustainDev development principles and project layer
globs: ["**/*"]
alwaysApply: true
---
```

The body content does not change. `alwaysApply: true` reproduces the classic `.cursorrules` always-on behavior.

### Cline: `.clinerules` vs `.clinerules/`

Cline likewise supports both a single file (`.clinerules`) and a directory (`.clinerules/`) where each file becomes a separate rule. This adapter installs the single-file form. To switch to the directory form:

```sh
mkdir -p .clinerules
mv .clinerules .clinerules/sustaindev.md  # if your shell allows the same name
# or simply
mkdir -p .clinerules.d
mv .clinerules .clinerules.d/sustaindev.md
mv .clinerules.d .clinerules
```

The body content does not change. The directory form is useful when you want SustainDev rules alongside other project-specific rule files without merging them into one file.

## Customizing the templates

Both templates have placeholders that must be filled in before they are useful:

- `<project-name>` — your project's name (top-level heading and references).
- `<One-line description ...>` — a single sentence explaining what the project is.
- `<One paragraph expanding ...>` — three to five sentences on purpose, problem, and constraints.

Beyond the placeholders, you may want to:

- **Pin specific verification commands** — the template points at `VERIFY.md`. If you want a frequently-run command directly visible in the rules, add a "Common Commands" section above "Verification Commands".
- **Restrict the AI to specific files for some tasks** — add a "Scope Constraints" section listing globs the AI should not touch without explicit permission. This complements `AI_POLICY.md` rather than replacing it.
- **Reference a specific skill** — if your project uses a project-specific skill (e.g. `.claude/skills/<name>/SKILL.md`), add it under "Skills Available".

## Verifying the rules are loaded

### Cursor

Open the project, start a new chat, and ask: *"What rules are loaded for this workspace?"* Cursor should reference the `.cursorrules` file and the `Read Before Acting` list. If it does not, check:

- Is `.cursorrules` at the project root (not in a subdirectory)?
- Did Cursor's workspace open at the right folder? Cursor's rules-loading is workspace-rooted; opening a parent directory will load that directory's rules instead.
- Cursor's settings: Settings → Rules. Confirm "Use .cursorrules" is enabled.

### Cline

Open the VS Code command palette (Cmd/Ctrl+Shift+P) and run "Cline: Show System Prompt". The system prompt should include the contents of `.clinerules`. If it does not:

- Confirm `.clinerules` is at the project root.
- Cline reads rules at session start. After editing `.clinerules`, start a new Cline task or reload the extension host (Cmd/Ctrl+Shift+P → "Developer: Reload Window").

## Common adjustments

### Permanent SustainDev path

The templates reference `core/principles/...`, `core/rules/...`, etc. These paths assume the project's AI tools can resolve them. Two ways to make this work:

1. **Symlink** `core/` into your project: `ln -s ~/sustaindev/core ./core`. The AI then reads from a path inside your project root. Add `core` to your `.gitignore` so the symlink isn't tracked.
2. **Absolute paths** in the rules. Edit the installed `.cursorrules` / `.clinerules` and replace `core/` with the absolute path: `/home/you/sustaindev/core/`. The AI receives a literal path; whether it resolves depends on the AI's filesystem access.

The symlink approach is portable across all editors and tools; the absolute-path approach works for tools without filesystem-relative resolution.

### Multi-project setup

If you work in many projects and don't want to install the rules in each one by hand, write a small wrapper:

```sh
# ~/.local/bin/sustaindev-init
#!/bin/sh
set -eu
~/sustaindev/adapters/cursor-cline/install.sh "$@"
ln -sf "$HOME/sustaindev/core" "$(pwd)/core"
echo "SustainDev initialized in $(pwd)"
```

Then run `sustaindev-init` from each new project root.

## Troubleshooting

**"The AI ignores the rules."**

- Confirm the rules file is at the project root, named exactly `.cursorrules` or `.clinerules` (no extension, no trailing whitespace in the filename).
- For Cursor: check that you opened the project's root directory as the workspace, not a parent directory.
- For Cline: reload the VS Code window after editing the rules; Cline caches the system prompt across sessions in some versions.
- If the AI claims the rules are loaded but still ignores them, the rules may be too long for the AI's effective attention budget. Trim project-specific sections or move them into `PROJECT_CONTEXT.md`, which the rules already point at.

**"The AI reads `core/principles/development-principles.md` and reports it can't find the file."**

The AI's filesystem access doesn't include your SustainDev checkout. Pick a fix:

- Symlink `core/` into the project (see above).
- Edit the rules to use absolute paths to the SustainDev checkout.
- Copy the `core/` directory into the project (less ideal — it duplicates content and risks drift).

**"I have an existing `.cursorrules` and the installer refuses to overwrite it."**

That's by design. The installer's manual-merge instruction tells you what to do: open both files side by side, copy the SustainDev sections into your existing file, save. If you actually want to replace your file outright, delete it first (`rm .cursorrules`) then re-run the installer.

**"The templates use `<placeholder>` syntax. Will the AI see those literally?"**

Yes — until you replace them. The installer does not auto-fill placeholders; that's a deliberate human-in-the-loop step. After install, open the file and write the actual project name, description, and paragraph. AIs reading raw `<placeholder>` text will sometimes ask you to fill it in, sometimes invent values; either way, you don't want that in your rules.

**MCP integration?**

Neither Cursor nor Cline read MCP servers as a source for rules content. The rules file is the rules file. If you want to surface SustainDev's `core/` content via MCP for Cline (which supports MCP servers), look at the `mcp-builder` skill in `core/skills/` — but the rules file itself is a separate concern, and shipping both side by side is fine.

## What this adapter is not

These templates are **thin pointers**. They tell the AI where to find SustainDev's rules; they don't restate them. The durable rules stay in `core/` — there is one source of truth and many projects pointing at it. If you find yourself editing the rules-file body to add general (cross-project) advice, that advice belongs in `core/rules/` instead, where every adapter benefits.

## What's coming in v0.2.x

- An optional `--symlink` flag that installs the rules and symlinks `core/` in one step.
- A schema check (run from the validate workflow) that confirms each installed rules file references the same canonical list of `core/` files.
- A small Cursor extension that surfaces `core/` content as context in the chat sidebar without requiring the symlink.

If you'd find any of these compelling: open an issue with your use case.
