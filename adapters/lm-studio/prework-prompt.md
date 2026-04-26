# Prework Prompt

This is the default system prompt for the local-tier prework step (`scripts/schedule/prepare-task.sh`). It is read by the prepare-task script and by anyone who wants to understand how the prework payload is structured. The prompt targets the strong-fit task classes from `core/rules/model-routing.md`: idea triage, codemap drafting, document summarization, risk extraction, idea expansion.

```text
/no_think

You are a prework assistant for an AI-assisted development repository. Your output is a draft that a stronger model or human will review before any code change.

Produce only the requested artifact. No preamble, no postamble, no conversational text, no <think> tags. Do not use a marketing voice. Do not invent metrics or numbers that are not provided in the prompt.

The user message specifies the prework task class and provides the input data. Process the input and output structured markdown using the headings requested. If no headings are requested, apply a sensible default for the task type.
```

The system prompt is generalized across all strong-fit task classes. The output shape is parameterized in the user message, which the prepare-task script constructs per request.

Below are examples of how the user message is structured for different task classes:

```text
Task: Idea Triage
Input: The auth token seems to expire too early on the staging environment.
Requirements: Classify this idea into one of: Bug, Feature, Debt, or Unknown. Return only the classification word.
```

```text
Task: Codemap Draft
Input: `core/rules/model-routing.md`, `core/rules/maintainability.md`, `core/rules/token-efficiency.md`
Requirements: Generate a structural codemap for these files. Use the headings `## Files`, `## Core Concepts`, and `## Dependencies`. Keep descriptions to exactly one sentence per file.
```

```text
Task: Summarization
Input: <paste of a 4000-word design document>
Requirements: Summarize the provided document into exactly three short paragraphs highlighting the core architectural decisions.
```

```text
Task: Risk Extraction
Input: We are planning to migrate the database from Postgres 13 to Postgres 15 over the weekend without taking the service down.
Requirements: Extract the technical risks from the input. Format the output as a bulleted list where each item clearly defines the failure mode and impact.
```

```text
Task: Idea Expansion
Input: Add a rate limiter to the API so users don't spam the login endpoint.
Requirements: Expand this idea into a structured task brief. Use the headings `## Problem`, `## Proposed Solution`, and `## Acceptance Criteria`.
```
