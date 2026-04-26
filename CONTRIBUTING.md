# Contributing to SustainDev

SustainDev is a portable, tool-neutral layer for AI-assisted development that reduces token waste and protects code maintainability across Codex, Claude Code, LM Studio, and MCP-enabled tools.

Contributions should help developers use AI tools with less repeated context gathering, lower token waste, better maintainability, and clearer workflows. This document explains what kinds of changes belong here and how to send them.

## What Belongs in This Repo

The repository is split into four layers. Where a contribution lives matters more than how big it is.

- `core/` — durable, tool-neutral knowledge: principles, rules, skills, agents, commands, templates, scheduling.
- `adapters/` — thin per-tool integration: how `core/` is exposed inside Codex, Claude Code, LM Studio, etc.
- `projects/` — sanitized examples of project-level adoption (project context, codemap, verify rules).
- `scripts/` — shell or Python helpers that automate parts of the workflow.

If a change is tool-specific, it goes in `adapters/`. If it is project-specific, it goes in `projects/` (sanitized). If it is reusable across tools and projects, it goes in `core/`.

## Good Contributions

- New or improved skills with a clear trigger, workflow, output, and verification.
- Tool adapters for Codex, Claude Code, Warp, Antigravity, VS Code, LM Studio, or MCP-enabled environments.
- MCP usage policies and templates.
- Scheduling and deferred-work improvements.
- Project context and codemap templates.
- Maintainability checklists.
- **Measurement reports**: real before/after numbers showing token or cost reduction on a concrete task. See `.github/ISSUE_TEMPLATE/measurement_report.md`.
- Sanitized real-world examples.

## Avoid

- Large generic prompts without a clear trigger or workflow.
- Duplicates of existing skills under a different name.
- Anything that depends on private project data, customer data, or secrets.
- Workflows that encourage unattended risky code changes without review gates.
- Tool-specific content that should belong in `core/`.
- Speculative tooling for ecosystems whose APIs are still in flux (mark as experimental if needed).

## Design Rules

Before opening a contribution, check that it follows these rules:

- Keep durable workflow logic in `core/`.
- Keep tool-specific behavior in `adapters/`.
- Keep project-specific knowledge in `projects/`.
- Prefer short reusable instructions over long prompt blocks.
- Include maintainability and verification expectations when code changes are involved.
- Treat local model output as draft prework unless reviewed.
- Use MCPs for external, dynamic, structured, or interactive context.
- Use codemaps and project files for stable, project-owned context.

## Suggested Contribution Flow

1. Open an issue describing the workflow, adapter, or improvement.
2. Explain the problem it solves and which tool or project type it affects.
3. Keep the first change small and focused on one layer.
4. Add or update documentation alongside the change.
5. Include an example or measurement when introducing a new pattern.
6. Open a pull request linked to the issue.

## Quality Bar

A contribution should answer:

- What problem does this solve?
- When should someone use it?
- What should trigger it?
- What output should it produce?
- How does it reduce token use, $ cost, or repeated work?
- How does it protect maintainability?
- What review or verification is required?

If a change introduces a new skill or workflow and there are no measurement numbers backing it, mark it as `status: experimental` in the front matter and explain how someone could verify the savings.

## Public Examples

Examples must be sanitized. Do not include:

- Private repository names unless they are already public.
- Credentials, tokens, keys, or internal URLs.
- Customer, student, medical, financial, or personal data.
- Proprietary business logic.
- Private prompts from paid products or closed systems unless you own the rights to share them.

## Naming

Use clear lowercase directory names with hyphens:

```text
core/skills/feature-delivery/
core/agents/maintainability-reviewer.md
adapters/lm-studio/
projects/example-web-app/
```

GitHub-recognized files (LICENSE, README, CONTRIBUTING, CODE_OF_CONDUCT) stay uppercase.

## Pull Request Checklist

- The change belongs in the right layer: `core/`, `adapters/`, `projects/`, `scripts/`, or `docs/`.
- The change is documented.
- The change avoids private data.
- The change does not duplicate an existing workflow.
- The change includes maintainability or verification guidance where relevant.
- The change keeps the system usable across multiple tools when possible.
- CI passes (link checker, required-files check, skill schema check).

## Reviewer Role

Sprint and PR reviews are model-neutral. A "strong-reviewer pair" means one capable reasoning model (Claude Opus, GPT-5, Gemini Pro, or equivalent) **plus** one human, with either able to skip if the other surfaces no blocking issues. Reviews are recorded as markdown in `docs/reviews/`.

No single model or provider is required. Contributors using local models for review are welcome to do so as long as the gating logic in `core/rules/model-routing.md` is respected.

## License

SustainDev is licensed under the Apache License, Version 2.0. By contributing, you agree that your contribution will be licensed under the same terms. See [LICENSE](LICENSE) for the full text.
