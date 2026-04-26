# Token Efficiency

## Purpose

This rule set reduces wasted tokens, repeated context-gathering, and unnecessary model calls during AI-assisted development. The goal is to make every model turn pay for itself: fewer tokens spent, less rework, lower dollar cost, and less time lost to rediscovery between sessions. These are disciplines, not hard limits — apply them with judgment, and override them when the task genuinely calls for broader context.

## Core Rules

- Read the project context file and codemap before scanning the repository. They exist precisely to keep the model from re-deriving structure on every session.
- Use the codemap to locate the right files. Only fall back to broad search when the codemap is silent, stale, or the answer truly spans the whole repo.
- Stop reading more files the moment the question can be answered with high confidence. Continued reading after that point is waste, not thoroughness.
- Pass file paths and line ranges instead of whole files when the model only needs a slice. Quoting 30 lines out of 800 is usually enough.
- Batch related questions into a single model turn when the answers do not influence each other. Three independent lookups belong in one prompt, not three.
- Capture durable findings in repository files (codemap, decisions, risks, verify commands) so the next session does not rediscover them. Knowledge that lives only in chat history is knowledge that will be re-derived.
- Route cheap, structural prework (idea triage, codemap drafts, summarization, classification, risk extraction) to a local model when wall-clock latency is acceptable. Route reasoning, code change, and final-output authoring to the cloud.
- Treat full-repository scans and "read everything" prompts as a fallback, not a default. They're sometimes correct; they're rarely necessary.

## Stop Conditions for Exploration

The hardest discipline in token-efficient work is knowing when to stop reading. Exploration should end when the user's question can be answered with high confidence from what's already in context, when the codemap pointed to specific files and they have been read, when two consecutive files have failed to change the conclusion, or when the context window is filling and continued reading risks pushing earlier evidence out of scope. If a stop condition triggers before the planned exploration is done, prefer the early answer with a clear caveat over an exhaustive read that bloats the next turn.

## What Gets Cached vs Re-Discovered

Two categories of context behave differently and should be treated differently.

Cache in repository files: project structure, codemap, verify commands, architectural decisions, known risks, maintainability rules, framework conventions, build/test commands, MCP usage policies, and anything else that is stable across sessions. These belong in `core/templates/`, `projects/<name>/`, or the relevant `docs/decisions/` entry, not in chat scrollback.

Re-fetch live every time: pull request state, CI status, current dependency versions, runtime logs, current branch state, recent diffs, and any value that is meaningful only at the moment it is read. Caching these is worse than not caching them — a stale dependency version is a bug waiting to surface.

## Routing Cheap Work to Local Models

Local models (running through LM Studio or similar) are a useful prework tier when the task is structural, the wall-clock cost is acceptable, and the output will be reviewed by a stronger model or a human before any code change. Strong fits include idea triage and classification, drafting codemaps from file lists, expanding rough captures into structured task briefs, summarizing long documents into a few hundred words, extracting risks from existing prose, and any batch/overnight work where latency is irrelevant. Weak fits include full-document drafting from a rich brief (the local model's incomplete output costs more in cloud rework than it saves), adapter templates that require accurate tool-specific knowledge, cross-document consistency checks, and time-critical authoring during an active session. The detailed routing triggers live in `core/rules/model-routing.md`; this file just establishes that the routing decision is a token-efficiency lever, not just a cost lever.

## Verification

Token efficiency claims must be measured per task, not asserted. Real before/after numbers live in `docs/measurement/case-study-XX.md`, and case studies are the only credible evidence that a workflow saves what it claims to save. Treat slogans like "10x faster" or "90% cheaper" as marketing; treat measurement records with input tokens, output tokens, wall-clock, and dollar cost as evidence. When in doubt, run the same task twice — once with the workflow, once without — and record the numbers.
