Write the file `core/rules/token-efficiency.md` for an AI-assisted development repository.

Purpose of this file: a tool-neutral set of rules that reduce wasted tokens and repeated context-gathering when working with AI coding assistants (cloud or local).

Required sections, in this order:

## Purpose
One short paragraph. Why this rule file exists, what it optimizes for (token cost, dollar cost, repeated work), and what it does not promise (it is not a hard limit, just a discipline).

## Core Rules
A bulleted list of 6 to 10 rules, each one full sentence. Each rule should be actionable on its own. Examples of the kind of rules to include (do not copy verbatim — write your own variants):
- prefer narrow context over broad context
- use codemaps and project context files before scanning the whole repository
- stop exploration when the answer is already sufficient
- delegate cheap preparation work to a local model where possible
- keep durable notes in the repository so the same context is not re-discovered every session
- batch related questions into one model turn when safe to do so

Do not include 12 rules. Pick the 6-10 that matter most.

## Stop Conditions for Exploration
A short prose section (2-4 sentences plus optional short bullet list). When should an AI assistant stop reading more files and answer with what it has? Cover at least: when the user's question is answered, when a codemap pointed to the same file, when context window is filling.

## What Gets Cached vs Re-Discovered
A short prose section (2-4 sentences). Distinguish between knowledge that should live in repository files (project context, codemaps, verify commands, decisions) and knowledge that is genuinely dynamic and should be re-fetched (current PR state, live diagnostics, current dependency versions).

## Routing Cheap Work to Local Models
A short prose section (3-5 sentences). When prework can be done by a local model and when it cannot. Reference the existence of a separate `core/rules/model-routing.md` for the detailed triggers, but give a one-paragraph summary.

## Verification
A short prose section (2-3 sentences). How does a user verify they are actually saving tokens? Mention that this is measured per task, that real before/after comparisons live in `docs/measurement/`, and that case studies are the source of truth, not slogans.

End the document there. No conclusion, no summary, no acknowledgements.
