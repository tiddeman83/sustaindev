# Build Plan: Durable AI Development System

> **Execution note:** This is the long-term *strategic* plan. The active *execution* plan is [`revised_sprints_v0.1.md`](revised_sprints_v0.1.md), which collapses the launch path to two sprints (foundation + hero workflow) followed by an incremental public roadmap (`docs/roadmap.md`). Where this document and the revised sprint plan disagree, the revised sprint plan wins for v0.1; this document remains the source of truth for the long-term direction.

## 1. Purpose

Build a personal AI development system that helps me develop consistently, efficiently, and with low token waste across Codex, Claude Code, Warp, Antigravity, VS Code, and MCP-enabled workflows.

The system must not be tied to a single model or editor. The durable parts should live in this repository, and each tool should receive only the thin adapter layer it needs.

Primary goals:

- Improve development consistency across projects.
- Reduce repeated context gathering and token usage.
- Preserve maintainability of the applications being built.
- Support multiple AI tools without duplicating instructions.
- Capture new ideas, prepare them while context is fresh, and schedule non-urgent AI work for better moments.
- Avoid exhausting compute, attention, and model capacity on work that can be deferred or prepared more intelligently.

## 2. Project Naming

The name should communicate efficiency, durability, and responsible use of AI/model resources. It should also be tool-neutral.

Name criteria:

- Tool-neutral: should not mention Claude, Codex, VS Code, or a single model provider.
- Durable: should still make sense if tools change.
- Practical: should sound like a working engineering system, not only a prompt collection.
- Efficient: should imply careful use of time, tokens, model capacity, and developer attention.
- Maintainable: should imply long-term application quality.
- Short enough for a repository name.

Selected name:

**SustainDev**

Why:

- Short and memorable.
- Communicates sustainable development habits.
- Covers efficiency, maintainability, and avoiding unnecessary resource use.
- Does not bind the project to Claude, Codex, or any one tool.
- Works well as a GitHub repository name: `sustaindev`.

Rejected alternatives retained for context:

- **SteadyStack**: strong for durable application work; less explicit about AI/model efficiency.
- **LeanLoop**: concise and process-oriented; good for iterative AI work, but less explicit about maintainability.
- **DurableLoop**: strong fit for repeated workflows and long-term quality; slightly abstract.
- **Efficient Engineering Kit**: very clear; better as a description than a repo name.
- **SustainStack**: good balance between sustainability and application architecture.
- **ConserveDev**: directly signals careful resource use; slightly less natural as a brand.
- **LowWasteDev**: very clear on efficiency; may sound too narrow.
- **SteadyAI Dev**: clear but more AI-branded than necessary.
- **EfficientDevOps**: clear, but sounds more infrastructure-specific than intended.
- **LeanDevKit**: good for efficiency, less strong on durability.
- **DurableDevFlow**: accurate, but a bit long.
- **SustainableAIWorkflows**: very clear, but too descriptive as a repo name.
- **ModelWiseDev**: good emphasis on careful model usage, less broad as a development system.
- **CalmDevOps**: captures non-exhaustive work, but sounds more cultural than practical.
- **SteadyDevKit**: good tone, but less explicit about efficiency.

Final repository name:

```text
sustaindev
```

Working description:

```text
A portable AI development system for efficient, maintainable, low-waste software work across Codex, Claude Code, Warp, Antigravity, VS Code, and MCP-enabled tools.
```

## 3. Repository Strategy

This repository is the source of truth for shared AI development workflows.

Core rule:

```text
Keep durable knowledge in the core layer. Generate or sync thin adapters into individual tools and projects.
```

Expected GitHub setup:

```text
Repository: sustaindev
Visibility: public from the beginning
Default branch: main
License: Apache-2.0 (decided)
Purpose: personal workflow infrastructure, project adapters, scheduling queue, reusable skills and agents
```

Initial local setup:

```text
git init
git branch -M main
```

Later GitHub setup:

```text
gh repo create sustaindev --public --source=. --remote=origin --push
```

If `gh` is not configured, create the repository manually on GitHub and add:

```text
git remote add origin git@github.com:<username>/sustaindev.git
git push -u origin main
```

## 4. Target Repository Structure

```text
sustaindev/
  README.md
  build_plan.md
  implementation_plan.md
  contribution.md
  code_of_conduct.md
  core/
    principles/
    rules/
    skills/
    agents/
    commands/
    workflows/
    checklists/
    templates/
    codemaps/
    mcp/
    scheduling/
    models/
  adapters/
    codex/
    claude-code/
    warp/
    antigravity/
    vscode/
    lm-studio/
  projects/
    _template/
    project-a/
    project-b/
  scripts/
    install/
    sync/
    validate/
    generate/
    schedule/
  docs/
    decisions/
    usage/
    maintenance/
```

## 5. Design Principles

These principles apply to every skill, agent, command, adapter, and project workflow.

1. Understand the local project before changing it.
2. Prefer narrow context over broad context.
3. Use codemaps and project context before scanning a whole repository.
4. Preserve project architecture unless there is a concrete reason to change it.
5. Treat maintainability as a required output of every workflow.
6. Make verification explicit before implementation starts.
7. Keep reusable instructions in `core/`, not scattered across tools.
8. Keep adapters thin and generated where possible.
9. Use MCPs for external, dynamic, structured, or interactive context.
10. Use local files and codemaps for stable project-owned context.
11. Capture new ideas separately from active implementation.
12. Prepare deferred work immediately while context is fresh.
13. Schedule non-urgent model-heavy work for better execution windows.
14. Require human review after unattended work.
15. Prefer fewer high-quality skills over many overlapping prompts.

## 6. Build Streams

The work should be split into clear streams so the system can grow without becoming difficult to maintain.

### Stream A: Repository Foundation

Purpose:

Create the durable base repository and make it safe to extend.

Deliverables:

- `README.md`
- `contribution.md`
- `code_of_conduct.md`
- `build_plan.md`
- `implementation_plan.md`
- `.gitignore`
- `core/principles/development-principles.md`
- `core/rules/base-engineering.md`
- `core/rules/token-efficiency.md`
- `core/rules/maintainability.md`
- `docs/decisions/0001-repository-architecture.md`

Acceptance criteria:

- Repository has a clear purpose and structure.
- The difference between `core/`, `adapters/`, `projects/`, and `scripts/` is documented.
- The repo can be pushed publicly to GitHub without including generated, private, or project-sensitive noise.
- The repo explains how outside users can contribute safely.

### Stream B: Core Skills

Purpose:

Create reusable workflows that are independent of any one AI tool.

Initial skills:

- `repo-onboarding`
- `feature-delivery`
- `bug-investigation`
- `maintainability-review`
- `low-token-debugging`
- `test-strategy`
- `idea-intake-and-scheduling`
- `unattended-prework`
- `project-retrospective`

Skill format:

```text
core/skills/<skill-name>/
  SKILL.md
  examples.md
  checklist.md
```

Acceptance criteria:

- Each skill has a clear trigger condition.
- Each skill has a compact workflow.
- Each skill includes verification expectations.
- Maintainability impact is included where code changes are involved.
- Skills avoid long generic prompting and instead reference shared rules.

### Stream C: Agents

Purpose:

Define scoped roles for delegation and review.

Initial agents:

- `planner-agent`
- `implementation-agent`
- `reviewer-agent`
- `maintainability-reviewer`
- `test-strategist`
- `mcp-context-agent`
- `scheduler-agent`
- `documentation-agent`

Agent format:

```text
core/agents/<agent-name>.md
```

Acceptance criteria:

- Each agent has one clear responsibility.
- Each agent states what it should not do.
- Agents reference relevant skills instead of duplicating them.
- Agents include expected output formats.

### Stream D: Commands And Workflows

Purpose:

Create thin command entry points for common work.

Initial commands:

- `plan-feature`
- `bugfix`
- `review-maintainability`
- `map-repo`
- `prepare-idea`
- `schedule-idea`
- `run-prework`
- `check-project-health`
- `compact-context`
- `sync-ai-configs`

Command format:

```text
core/commands/<command-name>.md
```

Acceptance criteria:

- Commands are short.
- Commands call skills and agents by name.
- Commands define expected inputs and outputs.
- Commands do not become long standalone prompts.

### Stream E: Maintainability System

Purpose:

Make maintainability a required part of every development workflow.

Deliverables:

- `core/checklists/maintainability-review.md`
- `core/rules/maintainability.md`
- `core/templates/maintainability-impact.md`
- Maintainability section in `feature-delivery`, `bug-investigation`, and `refactor` workflows.

Maintainability dimensions:

- Architecture fit.
- Coupling.
- Duplication.
- Naming.
- Testability.
- Error handling.
- Data flow.
- Dependencies.
- Migration risk.
- Documentation.
- Operational risk.
- Long-term change cost.

Acceptance criteria:

- Every implementation workflow asks for maintainability impact.
- Every review workflow can produce actionable maintainability findings.
- Project adapters can add project-specific maintainability rules.

### Stream F: Token Efficiency System

Purpose:

Reduce repeated context gathering and model waste.

Deliverables:

- `core/rules/token-efficiency.md`
- `core/workflows/context-compaction.md`
- `core/templates/project-context.md`
- `core/templates/codemap.md`
- `scripts/generate/project-codemap.sh`
- `scripts/validate/check-context-freshness.sh`

Mechanisms:

- Project codemaps.
- Short project context files.
- Verification command registry.
- Known-risk files.
- Decision logs.
- Stop conditions for exploration.
- Context compaction checkpoints.
- Model/tool routing rules.

Acceptance criteria:

- A model can start work by reading 2-4 compact files.
- Broad scans are treated as a fallback.
- Scheduled tasks include enough prework to avoid rediscovery.

### Stream G: MCP Strategy

Purpose:

Define when MCPs should be used and provide templates for MCP-enabled tools.

Deliverables:

- `core/mcp/mcp-policy.md`
- `core/mcp/github.md`
- `core/mcp/linear.md`
- `core/mcp/browser.md`
- `core/mcp/docs.md`
- `core/mcp/database.md`
- `core/mcp/calendar-and-tasks.md`
- `core/mcp/vscode.md`
- `core/mcp/antigravity.md`
- `adapters/vscode/mcp-config.example.json`
- `adapters/antigravity/mcp-config.example.json`

MCP policy:

```text
Use MCPs when context is external, dynamic, structured, or interactive.
Use local project files when context is stable, project-owned, and cheap to maintain.
```

Useful MCP categories:

- GitHub: PRs, issues, CI, review threads.
- Linear: backlog, issue status, project planning.
- Browser: localhost testing, screenshots, UI flows.
- Docs: current framework/API documentation.
- Database: schema inspection and safe read-only queries.
- Calendar/task tools: scheduled work and reminders.
- VS Code: diagnostics, active file, symbols, task runner.
- Antigravity: IDE context, active workspace, MCP-heavy workflows.

Acceptance criteria:

- MCP usage is deliberate and documented.
- MCPs do not replace codemaps for stable project knowledge.
- VS Code and Antigravity have clear MCP integration templates.

### Stream H: Scheduling And Deferred Work

Purpose:

Capture new ideas, prepare them while context is fresh, and schedule non-urgent work for better moments.

Scope:

Scheduling applies to new ideas and non-urgent work. It should not interrupt active implementation, urgent fixes, or production incidents.

Deliverables:

- `core/scheduling/policies/scheduling-policy.md`
- `core/scheduling/policies/model-routing-policy.md`
- `core/scheduling/calendars/preferred-windows.yaml`
- `core/scheduling/templates/scheduled-task.md`
- `core/scheduling/queue/captured/`
- `core/scheduling/queue/prework-ready/`
- `core/scheduling/queue/scheduled/`
- `core/scheduling/queue/completed/`
- `core/scheduling/logs/model-performance.md`
- `scripts/schedule/capture-idea.sh`
- `scripts/schedule/prepare-task.sh`
- `scripts/schedule/list-queue.sh`
- `scripts/schedule/mark-completed.sh`

Important constraint:

Most model providers do not expose reliable public model-load data. The scheduler should therefore start with practical signals:

- User-defined preferred work windows.
- Observed latency.
- Observed failure/rate-limit frequency.
- Task urgency.
- Task complexity.
- Required tool/model.
- Whether the task can run unattended.
- Whether prework is complete.

Local model consideration:

Local models, for example through LM Studio, should be considered a first-class execution tier for low-risk prework. The purpose is to reduce cloud model usage and preserve stronger cloud models for the parts that require deeper reasoning, code modification, or final review.

Good local model tasks:

- Summarize existing project context.
- Draft codemaps from selected file lists.
- Classify captured ideas.
- Expand rough ideas into structured task briefs.
- Extract candidate risks from existing docs.
- Draft verification checklists.
- Prepare first-pass documentation.
- Compare planned work against checklists.
- Identify files that may be relevant from filenames and short snippets.

Tasks that should stay with stronger cloud models or require human review:

- Complex architecture decisions.
- Multi-file code changes.
- Security-sensitive work.
- Data migrations.
- Production incidents.
- Final maintainability review for meaningful changes.
- Any task where the local model output would be trusted without verification.

Local model policy:

```text
Use local models for cheap, reversible, context-preparation work.
Use cloud models for high-risk reasoning, code changes, final review, and tasks requiring stronger reliability.
Never let a local model perform unattended code changes without a later cloud-model or human review gate.
```

Local model routing fields should be added to scheduled tasks:

```text
Local model eligible: yes/no
Suggested local model:
Local model task:
Cloud model handoff required: yes/no
Human review required: yes
```

Initial scheduling windows:

```yaml
timezone: Europe/Amsterdam

default_windows:
  low_priority:
    - "22:00-06:00"
  medium_priority:
    - "18:00-08:00"
  high_priority:
    - "now"

tools:
  local_lm_studio:
    preferred_windows:
      - "any"
    eligible_for:
      - "codemap drafts"
      - "idea triage"
      - "task brief drafts"
      - "documentation drafts"
      - "checklist passes"
  codex:
    preferred_windows:
      - "21:00-07:00"
  claude_code:
    preferred_windows:
      - "20:00-07:00"
  antigravity:
    preferred_windows:
      - "22:00-06:00"
  warp:
    preferred_windows:
      - "any"

rules:
  schedule_only_new_ideas: true
  require_prework_before_scheduled_execution: true
  require_human_review_after_unattended_work: true
  prefer_local_models_for_low_risk_prework: true
```

Scheduled task lifecycle:

```text
captured -> triaged -> prework-ready -> scheduled -> running -> needs-human-review -> completed -> archived
```

Acceptance criteria:

- New ideas can be captured without becoming immediate work.
- Each scheduled task includes a compact execution brief.
- Each task has maintainability and verification requirements.
- Deferred work can begin later without rereading the whole project.

### Stream I: Tool Adapters

Purpose:

Make the core system usable from Codex, Claude Code, Warp, Antigravity, and VS Code.

Deliverables:

```text
adapters/codex/
  AGENTS.md.template
  commands.md
  usage.md

adapters/claude-code/
  CLAUDE.md.template
  commands/
  agents/
  settings.local.example.json
  usage.md

adapters/warp/
  workflows/
  command-blocks.md
  usage.md

adapters/antigravity/
  project-context-template.md
  mcp-config.example.json
  workflows/
  usage.md

adapters/vscode/
  mcp-config.example.json
  tasks.json.template
  prompts/
  usage.md

adapters/lm-studio/
  local-model-policy.md
  prework-prompts/
  handoff-template.md
  usage.md
```

Acceptance criteria:

- Adapters reference `core/` instead of duplicating large content.
- Each adapter explains installation/sync.
- Tool-specific behavior is isolated in the adapter.
- Local model usage is limited to low-risk prework and produces handoff artifacts for stronger models or human review.

### Stream J: Project Adoption

Purpose:

Apply the system to real applications and extract reusable patterns.

Phase 6 project scope:

- `project-a`
- `project-b`

Project adapter format:

```text
projects/<project-name>/
  PROJECT_CONTEXT.md
  CODEMAP.md
  VERIFY.md
  AI_POLICY.md
  MAINTAINABILITY_NOTES.md
  MCP.md
  DECISIONS.md
  RISKS.md
```

Acceptance criteria:

- Each project can be understood from compact files before repo scanning.
- Existing `.claude` knowledge is extracted into tool-neutral project context.
- Each project has clear verification commands.
- Each project has maintainability rules tied to its stack and architecture.

### Stream K: Open Source Launch And Traction

Purpose:

Make SustainDev useful and understandable to other heavy AI-assisted developers as early as possible.

Deliverables:

- `README.md` with a clear problem statement, quickstart, and roadmap.
- `contribution.md` with contribution scope and quality expectations.
- `code_of_conduct.md`.
- Public GitHub repository.
- GitHub topics and description.
- First release tag after the usable core exists.
- Example project adapter using sanitized/demo content.
- Short launch post explaining the problem and design philosophy.
- Issue templates for skill ideas, tool adapters, and project adoption reports.

Positioning:

```text
SustainDev is a portable operating layer for efficient, maintainable AI-assisted software development across Codex, Claude Code, Warp, Antigravity, VS Code, local models, and MCP-enabled tools.
```

Fast traction strategy:

- Publish early with a strong README and clear build plan.
- Show real workflows rather than abstract prompt theory.
- Provide one immediately usable workflow: idea capture -> prework -> scheduled task.
- Provide one immediately usable project template.
- Include concrete examples for Codex and Claude Code first.
- Add LM Studio/local model prework as a differentiator.
- Keep the first public version small enough to understand in 10 minutes.
- Invite contributions around adapters, MCP templates, and project context patterns.
- Avoid exposing private project details; use sanitized examples for public docs.
- Track public roadmap items as GitHub issues.

Suggested GitHub topics:

```text
ai-development
developer-tools
codex
claude-code
mcp
lm-studio
local-llm
software-maintainability
prompt-engineering
agentic-workflows
```

Acceptance criteria:

- A new visitor understands the purpose in less than one minute.
- A heavy AI-coding user can copy one workflow and use it immediately.
- Contribution boundaries are clear.
- No private project data is required to understand the repository.
- The project has a public roadmap and first good issues.

## 7. Phase Plan

### Phase 1: Foundation

Goal:

Create the repository skeleton and first durable rules.

Tasks:

1. Initialize git repository.
2. Add `README.md`.
3. Add `.gitignore`.
4. Add `contribution.md`.
5. Add `code_of_conduct.md`.
6. Add `core/principles/development-principles.md`.
7. Add `core/rules/base-engineering.md`.
8. Add `core/rules/token-efficiency.md`.
9. Add `core/rules/maintainability.md`.
10. Add architecture decision record.

Exit criteria:

- The repository has a clear structure.
- The core principles are documented.
- The repo can be published publicly to GitHub.
- The repo has basic contribution and conduct guidance before public launch.

### Phase 2: Core Skills

Goal:

Create the first practical reusable workflows.

Tasks:

1. Create `repo-onboarding`.
2. Create `feature-delivery`.
3. Create `bug-investigation`.
4. Create `maintainability-review`.
5. Create `low-token-debugging`.
6. Create `idea-intake-and-scheduling`.
7. Create `unattended-prework`.

Exit criteria:

- Each skill has triggers, workflow, output format, and verification expectations.
- Skills reference shared rules and do not duplicate large instruction blocks.

### Phase 3: Agents And Commands

Goal:

Add scoped agent roles and thin command entry points.

Tasks:

1. Create planner, implementation, reviewer, maintainability, test, MCP, and scheduler agents.
2. Create command files for common flows.
3. Define output formats.
4. Add command-to-skill mapping.

Exit criteria:

- Agents are narrow and reusable.
- Commands are short and tool-neutral.

### Phase 4: MCP And Tool Adapters

Goal:

Define MCP usage and create first adapters.

Tasks:

1. Add MCP policy.
2. Add GitHub, Linear, Browser, Docs, Database, VS Code, Antigravity, and Calendar/task MCP notes.
3. Add Codex adapter.
4. Add Claude Code adapter.
5. Add Warp adapter.
6. Add VS Code adapter.
7. Add Antigravity adapter.
8. Add LM Studio/local model adapter notes.

Exit criteria:

- The system can be used from multiple tools.
- MCP usage is documented and limited to the right contexts.
- Local model prework is documented as a supported but review-gated execution path.

### Phase 5: Scheduling System

Goal:

Create a file-based scheduling system for deferred idea work.

Tasks:

1. Add scheduling policy.
2. Add queue folders.
3. Add scheduled task template.
4. Add preferred windows config.
5. Add model performance log.
6. Add capture, prepare, list, and complete scripts.
7. Add model routing policy with local model eligibility rules.

Exit criteria:

- New ideas can be captured.
- Deferred work can be prepared immediately.
- Scheduled work includes enough context for later unattended or semi-attended execution.
- Low-risk prework can be assigned to a local model without giving it authority to make final code changes.

### Phase 6: Project Adoption

Goal:

Apply the system to project-a and project-b.

Scope:

Only these two projects are included in Phase 6:

- `project-a`
- `project-b`

Tasks for project-a:

1. Read existing `.claude` context.
2. Extract tool-neutral project context into `projects/project-a/PROJECT_CONTEXT.md`.
3. Create `projects/project-a/CODEMAP.md`.
4. Create `projects/project-a/VERIFY.md`.
5. Create `projects/project-a/AI_POLICY.md`.
6. Create `projects/project-a/MAINTAINABILITY_NOTES.md`.
7. Create `projects/project-a/MCP.md`.
8. Capture known architecture decisions in `DECISIONS.md`.
9. Capture known risks in `RISKS.md`.

project-a maintainability focus (sanitized example — real specifics live in the private map):

- Respect framework MVVM boundaries.
- Centralize external-format mapping (e.g., spreadsheet cell mapping) in dedicated classes.
- Avoid hard-coded mapping addresses outside those classes.
- Preserve service interfaces.
- Keep UI services separate from core business logic.
- Add focused tests for service behavior and mapping changes.
- Run the project's verify command (defined in `projects/project-a/VERIFY.md`).

Tasks for project-b:

1. Inspect existing project structure.
2. Extract current `.claude` context if available.
3. Create `projects/project-b/PROJECT_CONTEXT.md`.
4. Create `projects/project-b/CODEMAP.md`.
5. Create `projects/project-b/VERIFY.md`.
6. Create `projects/project-b/AI_POLICY.md`.
7. Create `projects/project-b/MAINTAINABILITY_NOTES.md`.
8. Create `projects/project-b/MCP.md`.
9. Capture decisions and risks.

project-b maintainability focus:

- Identify frontend/backend boundaries before changing behavior.
- Document local dev commands.
- Keep generated assets or outputs out of source workflows unless required.
- Avoid mixing UI, domain logic, and persistence concerns.
- Add verification commands per app layer.
- Document deployment or build assumptions if discovered.

Exit criteria:

- Both projects have compact project context.
- Both projects have verification commands.
- Both projects have maintainability notes.
- Future Codex, Claude Code, Warp, Antigravity, or VS Code sessions can start from the project adapter files.

### Phase 7: Automation And Feedback Loops

Goal:

Make the system maintainable as it grows.

Tasks:

1. Add sync scripts for adapters.
2. Add validation scripts for skill format and broken references.
3. Add stale codemap checks.
4. Add retrospective workflow.
5. Add queue review workflow.
6. Add pattern promotion workflow.

Exit criteria:

- The system can detect stale context.
- Repeated project-specific lessons can become core skills.
- The repo stays useful without becoming too large.

## 8. Initial File Creation Order

Recommended order:

1. `README.md`
2. `.gitignore`
3. `contribution.md`
4. `code_of_conduct.md`
5. `core/principles/development-principles.md`
6. `core/rules/base-engineering.md`
7. `core/rules/token-efficiency.md`
8. `core/rules/maintainability.md`
9. `core/scheduling/policies/scheduling-policy.md`
10. `core/scheduling/templates/scheduled-task.md`
11. `core/templates/project-context.md`
12. `core/templates/codemap.md`
13. `projects/_template/`
14. `adapters/codex/`
15. `adapters/claude-code/`

## 9. First Milestone

Milestone name:

```text
M1: Usable Core
```

Milestone outcome:

The repository can explain itself, define the core operating rules, capture a new idea, prepare deferred work, and provide project context templates.

Milestone deliverables:

- Git repository initialized.
- GitHub repository name chosen.
- `README.md`.
- `build_plan.md`.
- `implementation_plan.md`.
- `contribution.md`.
- `code_of_conduct.md`.
- Core principles.
- Base engineering rules.
- Maintainability rules.
- Token efficiency rules.
- Scheduling policy.
- Scheduled task template.
- Project context template.
- Codemap template.

## 10. Open Decisions

Resolved during Sprint 0 (April 2026):

1. License: **Apache-2.0** (decided).
2. Project naming in public docs: **`project-a` and `project-b`**, with the real-name mapping in a gitignored `projects/.private-map.md`.
3. Reviewer role: **tool-neutral strong-reviewer pair** (capable reasoning model + human, either may be skipped if the other surfaces no blocking issues). No mandatory binding to one provider.
4. Repository name: **sustaindev** (no GitHub/npm/PyPI conflicts found).

Still open (will be revisited as Sprint 1 progresses):

1. Whether scheduling should stay file-based initially. Recommended: yes.
2. Whether Linear, GitHub Issues, or plain files should be the first backlog target. Recommended: plain files first.
3. Whether calendar integration is required in the first version. Recommended: no, add after file-based scheduling works.
4. Whether scripts should be POSIX shell, Python, or Node. Recommended: shell first for simple sync/list tasks, Python later for structured parsing.
5. Which local model runtime to target first. Recommended: LM Studio because it is user-facing and commonly exposes an OpenAI-compatible local API.

## 11. Risks

- Too many skills can become harder to maintain than the problems they solve.
- Tool adapters can drift if generated sync is not implemented.
- Scheduling can become fake precision if it pretends to know live model load.
- MCPs can increase context usage if used without clear boundaries.
- Project context files can become stale unless refresh workflows are built.
- Unattended work can produce risky changes unless scoped and reviewed.
- Local models can produce plausible but weak summaries; their output must be treated as draft prework until reviewed.
- Adding too many tool adapters too early can slow down the core system design.

## 12. Operating Rule

When in doubt, choose the option that makes future work easier to understand, cheaper to resume, and safer to verify.
