# Model Routing

## Purpose

Routing tasks to the appropriate model tier is the primary lever for managing token cost, dollar cost, wall-clock latency, and overall accessibility. This document defines the objective criteria for when to use local prework, when to require a cloud model, and when to halt for human review. It is a default baseline; specific projects override these rules via their own `<project>/AI_POLICY.md` files.

## Three Tiers

Execution in this repository is divided into three distinct tiers:
- **Local prework tier** — utilizes a local model for cheap, structured, draft-quality work where latency is less critical.
- **Cloud reasoning tier** — leverages a strong cloud model for actual code change, full-document authoring, and final review steps.
- **Human review tier** — strictly required for any security-sensitive, production-affecting, or migration-related work before it is committed.

## When to Use the Local Tier

Route tasks to the local tier when ALL of the following conditions are true:
- Output is short or structural (such as a codemap, classification, summary, or brief expansion) rather than a full prose document.
- No secrets, authentication mechanisms, payment gateways, or migration logic are in scope for the task.
- Output will be reviewed by a stronger cloud model or a human before any code commit occurs.
- Total input context fits comfortably within the local model's context window (typically <32k tokens, though modern models like Qwen 3.5 9B support up to 262k).
- Wall-clock latency is perfectly acceptable because the user is not actively waiting on the result.

## When to Use the Cloud Tier

Route tasks to the cloud tier when ANY of the following triggers occur:
- Code change touches more than three distinct files.
- Code change touches authentication, security, payment, migration, or production configuration logic.
- Task requires multi-step planning across established architectural boundaries.
- Task serves as the final review gate immediately before merging.
- Local model produced a draft that strictly needs verification or completion.
- User is actively waiting on output during a live, interactive session.

## When to Require Human Review

ALWAYS require strict human review when:
- Diff touches core dependency files (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
- Diff touches infrastructure-as-code definitions (Terraform, Helm, Kubernetes manifests, Dockerfiles).
- Diff touches anything explicitly matching the project's `RISKS.md` definitions.
- The change involves a data migration, schema change, or anything irreversible without a verified backup.
- The local-tier output is being directly committed without an intervening cloud verification step.

## Strong-Fit / Weak-Fit Matrix for the Local Tier

| Task class | Fit | Why | Evidence |
|---|---|---|---|
| Idea triage / classification | Strong | Tiny output, fast inference, real cloud savings at scale. | Theoretical; not yet measured. |
| Codemap drafts from file lists | Strong | Pattern extraction; benefits from large context window. | Theoretical; not yet measured. |
| Summarization of long documents | Strong | Plays to 262k context window; output is bounded. | Theoretical; not yet measured. |
| Risk extraction from existing prose | Strong | Pattern-matching task; structure matters more than prose quality. | Theoretical; not yet measured. |
| Idea expansion: rough capture → structured task brief | Strong | Hero-workflow centerpiece; latency is acceptable because user has walked away. | Theoretical; not yet measured. |
| Batch / overnight prework | Strong | Wall-clock cost is zero. | Theoretical; not yet measured. |
| Full-document drafting from rich brief | Weak | Reasoning overhead + wall-clock cost outweighs cloud savings. | Measured in `docs/measurement/case-study-01.md`. |
| Adapter templates | Weak | Requires accurate tool-specific knowledge that 9B class models get wrong. | Theoretical; not yet measured. |
| Cross-document consistency checks | Weak | Wall-clock penalty too high for active sessions. | Theoretical; not yet measured. |
| Time-critical authoring | Weak | User is waiting; latency is unacceptable. | Implicit from case-study-01. |

The "Theoretical; not yet measured" entries are honest acknowledgements. Only one task class has been empirically tested in the v0.1 release cycle. The v0.2 release will systematically fill in measurements for the remaining task classes.

## Hardware Tiers

Note that the strong-fit / weak-fit matrix above assumes mainstream Apple Silicon operating at 16–24 GB unified memory, running a 7B–9B model. Workstations equipped with discrete GPUs running 14B–32B coder models may reliably shift some weak-fit tasks toward strong-fit. Specific hardware recommendations and optimizations live exclusively in `adapters/lm-studio/usage.md`.

## Project-Specific Overrides

Each individual project may override this routing framework in its local `AI_POLICY.md` file. The default routing presented here is strictly the floor. Projects with stricter requirements—such as those handling regulated data or production-critical systems—may explicitly forbid the local tier entirely.

## Verification

Routing claims must be rigorously measured per task class. New routing rules require newly documented measurements before they can replace or modify the defaults in this document. Reference `docs/measurement/methodology.md` for the exact requirements on how to perform and document these measurements.
