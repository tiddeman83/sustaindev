# SustainDev Implementation Plan (Superseded for v0.1)

> **This document is superseded for the v0.1 launch by [`revised_sprints_v0.1.md`](revised_sprints_v0.1.md).**
>
> The original 8-sprint plan below contradicted the build plan's stated principle of *publish early with a strong README*. The revised plan collapses the launch path to two sprints (Sprint 0: foundation; Sprint 1: hero workflow + minimum core) and moves the remaining work to a public, version-numbered roadmap (`docs/roadmap.md`).
>
> Specific changes:
>
> - The mandatory single-model sprint review replaced with a tool-neutral *strong-reviewer pair* (capable reasoning model + human, either may be skipped if the other surfaces no blocking issues). No mandatory binding to Anthropic, OpenAI, or any other provider.
> - License decided: Apache-2.0.
> - Private project names sanitized to `project-a` / `project-b`.
> - Maintainability dimensions condensed from 12 to 6 (architecture fit, coupling, naming, testability, error handling, change cost) — applied in `core/rules/maintainability.md` during Sprint 1.
> - Original Sprints 2–8 deferred to v0.2+ as roadmap items, available for community contribution from day one of the public repo.
>
> The content below is preserved for historical reference and because some of the per-sprint deliverable lists are still useful as input to the v0.2+ roadmap. Do not treat it as the active execution plan.
>
> ---

## 1. Purpose (Original)

This plan turns `build_plan.md` into an execution sequence. It defines how to build SustainDev in small sprints, how to divide work across Codex, Claude Code, a strong reviewer model, local models, and future MCP-enabled environments, and how every sprint is reviewed against the strategic plan.

SustainDev should be public and useful early. The first implementation goal is not to build every adapter, script, and workflow. The first goal is to create a coherent public core that heavy AI-assisted developers can understand, copy, and improve.

## 2. Execution Principles

1. Build public-first.
2. Keep the core small and coherent.
3. Make every sprint produce usable artifacts.
4. Keep strategic planning in `build_plan.md`.
5. Keep execution planning in `implementation_plan.md`.
6. Keep durable reusable workflows in `core/`.
7. Keep tool-specific behavior in `adapters/`.
8. Keep project-specific knowledge in `projects/`.
9. Use multiple models where they reduce bottlenecks, not where they create coordination overhead.
10. Require the strong-reviewer pair review at the end of every sprint.

## 3. Model And Tool Responsibilities

### Codex

Primary role:

- Repository implementation.
- File creation and edits.
- Script implementation.
- Consistency checks.
- Local validation.
- Git hygiene.

Codex should own:

- Repository structure.
- Markdown artifacts.
- Shell scripts.
- Validation scripts.
- Codex adapter.
- Cross-file consistency.
- Final integration after other models contribute drafts.

### Claude Code

Primary role:

- Parallel drafting of Claude-specific workflows.
- Claude Code agents and commands.
- Review of Claude usability.
- Working alongside Codex in separate branches or clearly scoped files.

Claude Code should own:

- `adapters/claude-code/`
- Claude Code command templates.
- Claude Code agent templates.
- Claude Code usage notes.
- Testing whether the repo is pleasant to use from Claude Code.

Claude Code should not own:

- The shared core architecture.
- Final repository integration.
- Sprint acceptance decisions.

### Strong-Reviewer Pair

Primary role:

- Mandatory sprint review against `build_plan.md` and `implementation_plan.md`.
- Architecture review.
- Maintainability review.
- Coherence review across models and tools.

the strong-reviewer pair should review every sprint for:

- Alignment with SustainDev goals.
- Maintainability of the repository itself.
- Avoiding prompt sprawl.
- Public usability.
- Whether tool adapters duplicate core content.
- Whether scheduling/local model rules remain safe.
- Whether the sprint is complete enough to merge or publish.

the strong-reviewer pair should produce:

```text
Sprint review:
- Decision: pass / pass with fixes / fail
- Alignment with build_plan.md:
- Maintainability findings:
- Token-efficiency findings:
- Public launch readiness:
- Required fixes before next sprint:
- Optional improvements:
```

### Local Models Through LM Studio

Primary role:

- Low-risk prework.
- Draft summaries.
- Draft codemaps from file lists.
- Draft issue/task descriptions.
- Checklist expansion.
- First-pass documentation cleanup.

Local models should not:

- Make final architecture decisions.
- Make unattended code changes.
- Approve sprint completion.
- Replace the strong-reviewer pair review.

### Antigravity And VS Code

Primary role:

- Future MCP-heavy workspace integration.
- Editor diagnostics.
- Active-file workflows.
- Local task execution.

These should be designed for in early adapters, but not fully implemented until the core is stable.

### Warp

Primary role:

- Terminal workflow recipes.
- Common command blocks.
- Setup and verification command documentation.

Warp should be added after core scripts and basic adapters exist.

## 4. Multi-Agent Working Model

Use multiple agents only when work can be split by ownership boundary.

Good parallel splits:

- Codex builds `core/` while Claude Code drafts `adapters/claude-code/`.
- Codex builds scheduling templates while a local model drafts example task briefs.
- Claude Code drafts Claude command files while Codex builds validation scripts.
- the strong-reviewer pair reviews completed sprint artifacts after integration.

Avoid parallel work when:

- Two agents need to edit the same file.
- The core architecture is still undecided.
- The task requires a single coherent voice.
- Review findings have not been resolved.

Branching recommendation:

```text
main
feature/sprint-01-foundation
feature/sprint-02-core-skills
feature/sprint-03-adapters
```

If Claude Code works in parallel, use scoped branches:

```text
claude/sprint-03-claude-adapter
codex/sprint-03-core-adapter-integration
```

Integration rule:

Codex integrates final changes into the sprint branch after reviewing diffs and resolving overlap.

## 5. Sprint Review Rule

Every sprint must end with a review by the strong-reviewer pair.

The sprint is not complete until:

- Deliverables are present.
- Files match the repository structure.
- Public-facing docs are understandable.
- No private project data is included.
- `build_plan.md` remains accurate or is intentionally updated.
- `implementation_plan.md` remains accurate or is intentionally updated.
- the strong-reviewer pair review is recorded.

Review record location:

```text
docs/reviews/sprint-XX-opus-review.md
```

Review gate:

```text
No sprint can start implementation of the next sprint until the previous sprint has an Opus review and required fixes are resolved.
```

## 6. Sprint 0: Public Repo Readiness

Goal:

Prepare the repository to be public, understandable, and safe before building the core system.

Owner:

- Codex

Support:

- Local model may draft README variants.
- Strong-reviewer pair reviews final sprint (model + human, either may be skipped if the other surfaces no blocking issues).

Deliverables:

- `README.md`
- `.gitignore`
- `license-decision.md` or selected `LICENSE`
- `contribution.md`
- `code_of_conduct.md`
- `build_plan.md`
- `implementation_plan.md`
- `docs/roadmap.md`
- `.github/ISSUE_TEMPLATE/skill_request.md`
- `.github/ISSUE_TEMPLATE/adapter_request.md`
- `.github/ISSUE_TEMPLATE/project_adoption.md`

Tasks:

1. Create a README with problem, positioning, quickstart, status, roadmap, and contribution path.
2. Add a `.gitignore` suitable for docs, scripts, local model output, and generated files.
3. ~~Decide license before broad public promotion.~~ Resolved: **Apache-2.0** (Sprint 0).
4. Add GitHub issue templates.
5. Add a public roadmap.
6. Review all files for private information.
7. Ask the strong-reviewer pair to review Sprint 0.

Acceptance criteria:

- A new visitor can understand SustainDev in one minute.
- The repo can be made public without exposing private data.
- The repo clearly says what is usable now and what is planned.
- Contribution boundaries are clear.

## 7. Sprint 1: Core Foundation

Goal:

Create the durable core structure and first shared rules.

Owner:

- Codex

Support:

- Claude Code may review how the core could map to Claude Code later.
- Strong-reviewer pair reviews final sprint (model + human, either may be skipped if the other surfaces no blocking issues).

Deliverables:

- `core/principles/development-principles.md`
- `core/rules/base-engineering.md`
- `core/rules/token-efficiency.md`
- `core/rules/maintainability.md`
- `core/rules/model-routing.md`
- `core/templates/project-context.md`
- `core/templates/codemap.md`
- `core/templates/maintainability-impact.md`
- `docs/decisions/0001-repository-architecture.md`

Tasks:

1. Create the `core/` folder structure.
2. Add development principles.
3. Add base engineering rules.
4. Add token efficiency rules.
5. Add maintainability rules.
6. Add model routing rules, including local model prework.
7. Add project context and codemap templates.
8. Add architecture decision record.
9. Run a consistency pass against `build_plan.md`.
10. Ask the strong-reviewer pair to review Sprint 1.

Acceptance criteria:

- The core rules are tool-neutral.
- Local model usage is described as draft prework only.
- Maintainability is present in every relevant rule.
- Templates are usable without reading the full build plan.

## 8. Sprint 2: First Skills

Goal:

Create the first workflows that make SustainDev useful.

Owner:

- Codex

Support:

- Local model may draft examples.
- Strong-reviewer pair reviews final sprint (model + human, either may be skipped if the other surfaces no blocking issues).

Deliverables:

- `core/skills/repo-onboarding/SKILL.md`
- `core/skills/feature-delivery/SKILL.md`
- `core/skills/bug-investigation/SKILL.md`
- `core/skills/maintainability-review/SKILL.md`
- `core/skills/low-token-debugging/SKILL.md`
- `core/skills/idea-intake-and-scheduling/SKILL.md`
- `core/skills/unattended-prework/SKILL.md`

Tasks:

1. Create a shared skill format.
2. Build each skill with trigger, purpose, workflow, output, and verification.
3. Keep skills short and reference shared rules.
4. Add examples only where they clarify usage.
5. Check for overlap between skills.
6. Ask the strong-reviewer pair to review Sprint 2.

Acceptance criteria:

- A user can run a basic idea capture and prework flow.
- A user can onboard a repo using the project context and codemap templates.
- Skills do not duplicate large sections of shared rules.

## 9. Sprint 3: Agents And Commands

Goal:

Add scoped roles and command entry points.

Owner:

- Codex

Support:

- Claude Code drafts Claude-style command equivalents in a scoped branch or separate files.
- Strong-reviewer pair reviews final sprint (model + human, either may be skipped if the other surfaces no blocking issues).

Deliverables:

- `core/agents/planner-agent.md`
- `core/agents/implementation-agent.md`
- `core/agents/reviewer-agent.md`
- `core/agents/maintainability-reviewer.md`
- `core/agents/test-strategist.md`
- `core/agents/mcp-context-agent.md`
- `core/agents/scheduler-agent.md`
- `core/commands/plan-feature.md`
- `core/commands/bugfix.md`
- `core/commands/review-maintainability.md`
- `core/commands/map-repo.md`
- `core/commands/prepare-idea.md`
- `core/commands/schedule-idea.md`
- `core/commands/run-prework.md`

Tasks:

1. Define agent responsibilities.
2. Define what each agent must not do.
3. Create thin commands that call skills and agents.
4. Add command output expectations.
5. Compare Claude Code drafts against core commands.
6. Ask the strong-reviewer pair to review Sprint 3.

Acceptance criteria:

- Agents are narrow enough to delegate safely.
- Commands are thin entry points.
- Claude Code can map commands without duplicating the core.

## 10. Sprint 4: Scheduling And Local Model Prework

Goal:

Build the first version of the deferred work system.

Owner:

- Codex

Support:

- Local model drafts sample task briefs.
- Claude Code reviews whether scheduled tasks are usable from Claude Code.
- Strong-reviewer pair reviews final sprint (model + human, either may be skipped if the other surfaces no blocking issues).

Deliverables:

- `core/scheduling/policies/scheduling-policy.md`
- `core/scheduling/policies/model-routing-policy.md`
- `core/scheduling/calendars/preferred-windows.yaml`
- `core/scheduling/templates/scheduled-task.md`
- `core/scheduling/queue/captured/.gitkeep`
- `core/scheduling/queue/prework-ready/.gitkeep`
- `core/scheduling/queue/scheduled/.gitkeep`
- `core/scheduling/queue/completed/.gitkeep`
- `core/scheduling/logs/model-performance.md`
- `scripts/schedule/capture-idea.sh`
- `scripts/schedule/list-queue.sh`

Tasks:

1. Define scheduling policy.
2. Define local model eligibility.
3. Create scheduled task template.
4. Create queue folders.
5. Add simple capture/list scripts.
6. Add an example scheduled task using sanitized content.
7. Ask the strong-reviewer pair to review Sprint 4.

Acceptance criteria:

- New ideas can be captured without becoming active work.
- Low-risk prework can be routed to a local model.
- Scheduled tasks include review gates.
- The system does not pretend to know exact live model load.

## 11. Sprint 5: Tool Adapters

Goal:

Make the core system usable from Codex and Claude Code first, with placeholders for Warp, Antigravity, VS Code, and LM Studio.

Owners:

- Codex owns Codex adapter and integration.
- Claude Code owns Claude Code adapter drafts.

Reviewer:

- Strong-reviewer pair reviews final sprint (model + human, either may be skipped if the other surfaces no blocking issues).

Deliverables:

- `adapters/codex/AGENTS.md.template`
- `adapters/codex/usage.md`
- `adapters/claude-code/CLAUDE.md.template`
- `adapters/claude-code/commands/`
- `adapters/claude-code/agents/`
- `adapters/claude-code/usage.md`
- `adapters/lm-studio/local-model-policy.md`
- `adapters/lm-studio/handoff-template.md`
- `adapters/warp/usage.md`
- `adapters/antigravity/usage.md`
- `adapters/vscode/usage.md`

Tasks:

1. Build Codex adapter.
2. Have Claude Code draft Claude Code adapter.
3. Add LM Studio handoff policy.
4. Add placeholder usage notes for Warp, Antigravity, and VS Code.
5. Ensure adapters reference core files rather than duplicating them.
6. Ask the strong-reviewer pair to review Sprint 5.

Acceptance criteria:

- Codex can use the repo instructions directly.
- Claude Code has usable adapter templates.
- Local model handoff is clear.
- Adapters stay thin.

## 12. Sprint 6: Project Adoption

Goal:

Apply SustainDev to the first two real projects.

Scope:

- `project-a`
- `project-b`

Owner:

- Codex

Support:

- Claude Code may inspect existing `.claude` material and suggest extraction.
- Local model may draft first-pass codemaps from selected file lists.
- Strong-reviewer pair reviews final sprint (model + human, either may be skipped if the other surfaces no blocking issues).

Deliverables:

- `projects/project-a/PROJECT_CONTEXT.md`
- `projects/project-a/CODEMAP.md`
- `projects/project-a/VERIFY.md`
- `projects/project-a/AI_POLICY.md`
- `projects/project-a/MAINTAINABILITY_NOTES.md`
- `projects/project-a/MCP.md`
- `projects/project-a/DECISIONS.md`
- `projects/project-a/RISKS.md`
- `projects/project-b/PROJECT_CONTEXT.md`
- `projects/project-b/CODEMAP.md`
- `projects/project-b/VERIFY.md`
- `projects/project-b/AI_POLICY.md`
- `projects/project-b/MAINTAINABILITY_NOTES.md`
- `projects/project-b/MCP.md`
- `projects/project-b/DECISIONS.md`
- `projects/project-b/RISKS.md`

Tasks:

1. Inspect existing project context.
2. Extract durable knowledge from `.claude` files where present.
3. Create compact project context files.
4. Create codemaps.
5. Define verification commands.
6. Define maintainability rules.
7. Sanitize anything that could become public.
8. Ask the strong-reviewer pair to review Sprint 6.

Acceptance criteria:

- Both project adapters are useful for future sessions.
- No private data is exposed.
- Verification commands are clear.
- Maintainability notes reflect each project stack.

## 13. Sprint 7: Validation And Sync

Goal:

Add lightweight automation to keep the repo maintainable.

Owner:

- Codex

Support:

- Strong-reviewer pair reviews final sprint (model + human, either may be skipped if the other surfaces no blocking issues).

Deliverables:

- `scripts/validate/check-links.sh`
- `scripts/validate/check-skill-format.sh`
- `scripts/validate/check-required-files.sh`
- `scripts/sync/sync-codex.sh`
- `scripts/sync/sync-claude-code.sh`
- `docs/maintenance/validation.md`

Tasks:

1. Add simple validation scripts.
2. Add required file checks.
3. Add adapter sync scripts where safe.
4. Document validation usage.
5. Ask the strong-reviewer pair to review Sprint 7.

Acceptance criteria:

- Missing required artifacts can be detected.
- Skills can be checked for basic structure.
- Adapter sync behavior is documented and conservative.

## 14. Sprint 8: Public Launch

Goal:

Publish a useful first public version.

Owner:

- Codex

Support:

- Claude Code tests Claude Code adapter.
- Strong-reviewer pair performs final launch review.

Deliverables:

- Public GitHub repository.
- `v0.1.0` release.
- GitHub topics.
- Public roadmap issues.
- First good issues.
- Launch note or short announcement draft.

Tasks:

1. Run all validation scripts.
2. Review public-facing docs.
3. Create GitHub repository as public.
4. Push `main`.
5. Add topics.
6. Create roadmap issues.
7. Tag `v0.1.0`.
8. Ask the strong-reviewer pair for final launch review.

Acceptance criteria:

- Repository is public.
- README explains the project quickly.
- At least one workflow is usable immediately.
- Contribution path is clear.
- No private data is exposed.

## 15. Sprint Review Checklist

Every sprint must answer:

- Did we build the promised deliverables?
- Did we update `build_plan.md` if the strategy changed?
- Did we update `implementation_plan.md` if execution changed?
- Did we keep core logic out of adapters?
- Did we preserve public usability?
- Did we avoid private project data?
- Did we reduce or at least not increase token waste?
- Did we protect application maintainability?
- Did the strong-reviewer pair review the sprint?
- Were required fixes completed?

## 16. Immediate Next Step

Start with Sprint 0.

First implementation tasks:

1. Create `README.md`.
2. Create `.gitignore`.
3. ~~Decide license.~~ Resolved: **Apache-2.0**.
4. Create `docs/roadmap.md`.
5. Create GitHub issue templates.
6. Run a public-safety review.
7. Send Sprint 0 package to the strong-reviewer pair for review.

## 17. Current Open Questions

1. Which license should SustainDev use? Recommended: MIT if broad reuse is desired.
2. Should the strong-reviewer pair reviews be stored manually as markdown files or linked from external conversations? Recommended: markdown files in `docs/reviews/`.
3. Should Claude Code work in the same repository branch or separate scoped branches? Recommended: separate scoped branches once implementation begins.
4. Should local model use be implemented in scripts or documented first? Recommended: documented first, scripted after the scheduling workflow proves useful.
