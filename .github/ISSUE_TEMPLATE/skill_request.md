---
name: Skill request
about: Propose a new reusable workflow for core/skills/
title: "[skill] "
labels: skill, triage
assignees: ''
---

## Problem

What problem does this skill solve? Be specific. *"Speed up bug investigation"* is too vague. *"When investigating a bug in a multi-package monorepo, I currently re-scan the whole repo because I don't know which package owns the symptom"* is useful.

## Proposed Trigger

When should the skill activate? What does the user say or do?

## Proposed Workflow (rough)

1. Step one
2. Step two
3. ...

Keep it short. The actual SKILL.md will be tighter.

## Expected Output

What artifact does the skill produce? A markdown brief? A code change? A checklist?

## Verification

How does the user verify the skill did its job?

## Why This Belongs in `core/`

If this is tool-specific (Claude Code only, Cursor only, etc.), it should be an adapter contribution instead. Explain why it's tool-neutral.

## Maintainability Impact

If the skill produces code changes, what maintainability dimensions does it touch (architecture fit, coupling, naming, testability, error handling, change cost)?

## Token / Cost Reduction Hypothesis

How does this skill reduce repeated work, redundant context, or cloud-model usage compared to doing the task without it? A rough estimate is fine for the issue; a measurement comes in the PR.

## Existing Skills It Overlaps With

Did you check `core/skills/` for overlap? If yes, name the closest existing skill and explain the gap.
