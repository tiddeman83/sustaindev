# Cursor / Cline Adapter

A rules-export adapter that drops SustainDev's tool-neutral guidance into the formats [Cursor](https://cursor.com) and [Cline](https://cline.bot) read natively: a `.cursorrules` file and a `.clinerules` file at your project root.

## What this is

Cursor reads `.cursorrules` (or `.cursor/rules/*.mdc`) at workspace open and prepends it to every AI prompt. Cline reads `.clinerules` (or `.clinerules/*.md`) the same way. Neither tool has a way to point at "read these files in your other repo first" — the rules have to live in the project itself.

This adapter ships two templates that solve that problem without duplicating the SustainDev `core/` content. Each template tells the AI to read `core/principles/development-principles.md`, `core/rules/token-efficiency.md`, etc. from your SustainDev checkout, plus the project-layer files (`PROJECT_CONTEXT.md`, `CODEMAP.md`, `VERIFY.md`, ...) from the project itself. The durable knowledge stays in `core/`; only the pointer lives in the project root.

## Quick install

From your project root, with SustainDev checked out at `~/sustaindev`:

```sh
~/sustaindev/adapters/cursor-cline/install.sh
```

That installs both `.cursorrules` and `.clinerules`. Use `--cursor` or `--cline` to install just one. The installer **refuses to overwrite existing rules files** — if you already have one, it prints a merge instruction and exits.

After install:

1. Open `.cursorrules` (or `.clinerules`) and replace the `<placeholder>` values for your project.
2. Confirm the project layer exists (`PROJECT_CONTEXT.md`, `CODEMAP.md`, `VERIFY.md`, ...). Scaffold missing files from `core/templates/` if needed.
3. Restart the editor (or reload the Cline extension) so it picks up the new rules.

## Why both formats from one adapter?

Cursor's `.cursorrules` and Cline's `.clinerules` are nearly identical in shape: a markdown file at the project root that gets prepended to AI prompts. They differ in tooling: Cursor reads it natively as part of the editor; Cline reads it via the VS Code extension. Shipping two near-identical adapters would duplicate maintenance for almost no gain. The templates differ only in tool-specific notes (Cursor's `@`-references; Cline's auto-include behavior and approval gates).

## What this adapter is not

These templates are **pointers**, not prompts. They tell the AI where to find the durable rules, they don't restate them. That keeps `core/` as the single source of truth and avoids the "rule drift" that happens when the same content is copy-pasted into ten projects and then edited in nine of them.

## See also

- [`adapters/cursor-cline/usage.md`](usage.md) — full setup, format differences (`.cursorrules` vs `.cursor/rules/*.mdc`, `.clinerules` vs `.clinerules/`), and troubleshooting.
- [`docs/adoption/getting-started.md`](../../docs/adoption/getting-started.md) — first-30-minutes walkthrough including the project-layer scaffolding.
- [`adapters/codex/AGENTS.md.template`](../codex/AGENTS.md.template) and [`adapters/claude-code/CLAUDE.md.template`](../claude-code/CLAUDE.md.template) — the equivalent adapters for Codex and Claude Code, with the same content shape.
