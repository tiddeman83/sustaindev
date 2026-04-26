# Token Efficiency

## Purpose
This rule set minimizes wasted tokens and reduces the financial cost of using cloud-based AI models during development. It focuses on preventing repeated work, such as re-scanning known files or regenerating context that already exists in durable notes. These guidelines are not hard limits but serve as a discipline to ensure every model invocation provides maximum value without unnecessary overhead. Long-term maintainability of the project depends on keeping the context window clean and focused on current tasks rather than historical noise.

## Core Rules
*   Prefer narrow context windows over broad repository scans unless the specific scope is unknown.
*   Use codemaps and project context files before attempting to scan the entire codebase for information.
*   Stop exploration immediately when the answer to the user's question is already sufficient.
*   Delegate cheap preparation work, such as syntax highlighting or basic linting, to a local model where possible.
*   Keep durable notes in the repository so the same context is not re-discovered every session.
*   Batch related questions into one model turn when safe to do so rather than making separate calls.
*   Provide specific file paths and line numbers instead of relying on general search queries for known locations.
*   Summarize previous findings before asking the next question to maintain continuity without re-reading history.
*   Avoid requesting explanations for code that has already been reviewed or merged into the main branch.

## Stop Conditions for Exploration
An assistant must stop reading more files once the user's question is answered satisfactorily based on available information. If a codemap points directly to the relevant file, do not search beyond that specific location unless explicitly requested. Context window limits also dictate stopping when the buffer fills up, forcing a summary or truncation of older data.
*   Halt reading
