# Maintainability

## Purpose

Maintainability is a required output of every code-changing workflow, not an afterthought applied during review. This rule file defines the six dimensions that every code change must be evaluated against, and establishes the maintainability impact note as the mechanism for making that evaluation visible. It is a discipline, not a substitute for code review — the impact note feeds into review; it does not replace it.

## The Six Dimensions

- **Architecture fit.** The change works within the established layer boundaries and does not introduce cross-layer shortcuts that the existing design prohibits.
- **Coupling.** The change does not increase the number of callers, dependencies, or data-flow paths that must change together when a single concept changes.
- **Naming.** Identifiers, files, and modules introduced or renamed by the change correctly signal their purpose to a reader unfamiliar with the context.
- **Testability.** The code produced by the change can be exercised in isolation without requiring a full environment, shared state, or manual intervention.
- **Error handling.** Failure paths are explicit, errors surface at the right layer, and callers receive enough information to decide how to proceed.
- **Change cost.** The change does not make future modifications harder to reason about, harder to scope, or harder to reverse — duplication, migration risk, and operational surface are all contributors to this cost.

## Required Output: Maintainability Impact Note

Every code-changing workflow must produce a short maintainability impact note before the change is submitted for review. The note covers which dimensions were touched and how. It is not a comprehensive audit; it is a structured prompt that forces the author to consider each dimension before a reviewer encounters the diff.

Expected shape:

```
Maintainability Impact
Architecture fit:   No layer boundary crossed; change stays within the data-access module.
Coupling:           One new dependency added (cache client); isolated behind existing interface.
Naming:             Two functions renamed for clarity; no public API change.
Testability:        New logic is pure; no new shared state introduced.
Error handling:     Errors from the cache client are surfaced to the caller, not swallowed.
Change cost:        Removes one duplicated code path; migration risk low.
```

If a dimension is genuinely unaffected, write "Not affected." rather than omitting the line. Omission signals that the dimension was not considered.

## When to Apply

The six dimensions apply to feature delivery, bug fixes, refactors, and dependency upgrades — any workflow whose output is a diff to tracked code. Apply the dimensions at authoring time, not retrospectively.

The dimensions do not apply to read-only investigation, documentation-only changes, or formatting-only changes. Those workflows produce no code change and therefore no impact to assess. If a documentation change is accompanied by a code change, the code change requires a note.

## Project-Specific Overrides

Each project under `projects/<name>/` may define maintainability rules tied to its stack and architecture in a file named `MAINTAINABILITY_NOTES.md`. Project-specific rules extend the six dimensions — they do not replace them. A project might require, for example, that every new module be accompanied by an entry in its codemap, or that error handling follow a specific result-type convention. Those constraints live in the project file; the core dimensions still apply to all projects.

## Verification

The maintainability impact note is checked during code review, not after merge. Reviewers confirm that the note is present, that it addresses each of the six dimensions, and that the claims in the note are consistent with the diff. A note that says "testability: no shared state introduced" while the diff adds a global singleton is a review failure, not a passing note.

Tone and density reference: `core/rules/token-efficiency.md`. Evidence that the six dimensions improve review quality relative to the original twelve lives in `docs/measurement/` as case studies accumulate.
