# Prework Prompt

This document defines the default system prompt that the local-tier prework step (`scripts/schedule/prepare-task.sh`) utilizes when interacting with the local model. It is intended to be read by the prepare-task script and by any developer seeking to understand exactly how the prompt structures the prework payload. This prompt specifically targets the strong-fit task classes established in `core/rules/model-routing.md`, including idea triage, codemap drafting, document summarization, risk extraction, and idea expansion.

```text
/no_think

You are a prework assistant for an AI-assisted development repository. Your output is a draft that a stronger model or human will review before any code change.

Produce only the requested artifact. Include absolutely no preamble, no postamble, no conversational text, and no <think> tags. Do not use a marketing voice. Do not invent metrics or numbers that are not provided in the prompt.

The user message will specify the exact prework task class and provide the necessary input data. You must process the input and output structured markdown that explicitly uses the headings requested by the user. If no specific headings are requested, apply a sensible default structure tailored to the task type.
```

The system prompt above is intentionally generalized across all strong-fit task classes. The exact output shape and processing logic are parameterized directly within the subsequent user message. The prepare-task script dynamically constructs the user message depending on the specific prework requested. 

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
