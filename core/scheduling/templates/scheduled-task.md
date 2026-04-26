# Scheduled Task: <id>

---
id: <id>
title: <task-title>
captured_at: <YYYY-MM-DDTHH:MM:SSZ>
prepared_at: <YYYY-MM-DDTHH:MM:SSZ-or-empty>
status: captured
priority: medium
execution_tier_suggested: local
cloud_tool_suggested: <claude-code-or-codex-or-empty>
time_window_suggested: <for-example-22:00-06:00>
---

## Captured Idea

<Write the original rough idea in one to three sentences, preserving the user's wording where possible. Do not refine scope here; this section records what was captured.>

## Scope

<Describe what this task changes and what it explicitly does not change. Keep the boundary narrow enough that a cloud tool or human can execute without rediscovering the project.>

## File Targets

- `<path-to-likely-file-or-directory>` because <why-this-path-is-relevant>.
- `<path-to-likely-test-file-or-directory>` because <what-verification-it-supports>.
- `<path-to-config-or-doc-file-if-needed>` because <why-it-may-change>.

## Verify Commands

- `<command-from-project-VERIFY.md>` confirms <what-it-proves>.
- `<optional-focused-command>` confirms <specific-risk-or-regression>.

Refer to `<project>/VERIFY.md` as the source of truth. If the command here disagrees with `VERIFY.md`, update the brief or the project verification file before execution.

## Maintainability Constraints

<Name the maintainability dimensions most at risk for this task: architecture fit, coupling, naming, testability, error handling, and change cost. State what must be preserved, such as an existing boundary, a shared validation path, or a public interface.>

## Success Criteria

- <Concrete pass/fail condition the executor can verify.>
- <Concrete behavior that must remain unchanged.>
- <Required test, lint, build, or manual check passes.>

## Notes for Execution

<Add context the executor needs but should not have to rediscover: assumptions, relevant decisions, known risks, or why a particular tool/model was suggested.>

## Retrospective

<Fill this after completion. Record what actually happened, what diverged from the brief, which verification ran, and what should be remembered next time.>

## Example (Filled In)

Example title: Scheduled Task: 2026-04-26-add-csv-export

---
id: 2026-04-26-add-csv-export
title: Add CSV export to report screen
captured_at: 2026-04-26T08:14:00Z
prepared_at: 2026-04-26T08:28:00Z
status: prework-ready
priority: medium
execution_tier_suggested: cloud
cloud_tool_suggested: codex
time_window_suggested: 22:00-06:00
---

## Captured Idea

Add a CSV export action to the report screen so users can download the visible table.

## Scope

Add export behavior for the existing report table only. Do not change filtering, stored report data, or authentication behavior.

## File Targets

- `src/reports/report-screen.tsx` because it owns the visible table actions.
- `src/reports/export.ts` because export formatting should stay outside the UI component.
- `tests/reports/export.test.ts` because CSV formatting needs focused coverage.

## Verify Commands

- `npm test -- reports` confirms the focused report tests pass.
- `npm run lint` confirms the UI and export helper follow project rules.

## Maintainability Constraints

Preserve architecture fit by keeping CSV formatting outside the component. Protect testability by making the formatter a pure helper. Avoid coupling export behavior to visual table markup.

## Success Criteria

- The report screen has one export action.
- The downloaded CSV contains the same visible columns as the table.
- Focused tests and lint pass.

## Notes for Execution

Use the existing button pattern from nearby report actions. Do not introduce a new CSV library unless the existing codebase already uses one.

## Retrospective

Filled after completion.
