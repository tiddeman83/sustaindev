---
name: Adapter request
about: Propose a new tool adapter (Cursor, Cline, Continue.dev, IDE extension, etc.)
title: "[adapter] "
labels: adapter, triage
assignees: ''
---

## Tool

Which tool does this adapter target? Provide a link to the tool's documentation.

## Tool Status

- Stable / production-ready
- Beta with stable API
- Experimental / API likely to change

If the tool is experimental, this adapter will probably be marked experimental too.

## What the Adapter Exposes

Which parts of `core/` does this adapter export to the tool? (rules, skills, agents, commands, scheduling)

## Format

What format does the tool consume? `.cursorrules`, `AGENTS.md`, slash commands, MCP server, IDE extension config, etc.

## Sync Strategy

How does the adapter stay in sync with `core/`?

- Generated from a script
- Manually maintained with a checklist
- Symlinked

## Authentication / Configuration

Does the tool require credentials, API keys, or specific config? List required env vars or config files (do not include actual secrets).

## Existing Tool Conventions

What conventions does the tool already have? An adapter should respect them. Name the conventions you intend to follow.

## Why This Adapter, Why Now

Is there demand? A linked discussion or community request strengthens the case. A planned `v0.x` milestone is fine if the answer is "I personally need it."
