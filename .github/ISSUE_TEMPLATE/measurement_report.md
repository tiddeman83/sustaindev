---
name: Measurement report
about: Share real before/after numbers from using a SustainDev workflow
title: "[measurement] "
labels: measurement, evidence
assignees: ''
---

## Workflow Used

Which SustainDev workflow / skill / adapter did you use? Link to the relevant file.

## Task Description

Describe the task you performed. Be specific enough that someone else could attempt the same task on a similar codebase. Sanitize any private details.

## Tool Setup

- Cloud model used (e.g., Claude Opus 4.6, GPT-5, Gemini Pro)
- Cloud tool used (e.g., Claude Code, Codex CLI, Cursor, Continue.dev)
- Local model used, if any (e.g., Qwen 2.5 Coder 14B via LM Studio)
- Hardware for local model, if relevant (e.g., M2 Pro 32GB, RTX 4090, etc.)

## Baseline (Without SustainDev)

How would you have done this task before adopting SustainDev? Describe the comparable session.

- Total cloud tokens (input + output)
- Approximate dollar cost
- Wall-clock time
- Number of model turns

## With SustainDev

The same task, run through the SustainDev workflow.

- Local-model tokens (if applicable)
- Cloud tokens (input + output)
- Approximate dollar cost
- Wall-clock time
- Number of cloud-model turns

## Quality Comparison

Was the output quality the same, better, or worse compared to the baseline? How did you check?

## What Worked

What went well? What surprised you?

## What Didn't Work

What was awkward, broken, or required workarounds? This is the most useful section for improving the workflow.

## Reproducibility Notes

Anything someone else would need to know to reproduce these numbers? Tokenizer used to count, settings, prompt variations, etc.

## Sanitization Confirmation

- [ ] No customer data in this report
- [ ] No credentials, tokens, or secrets in this report
- [ ] No private business logic that I don't have rights to share
- [ ] The task description is reproducible without my private codebase
