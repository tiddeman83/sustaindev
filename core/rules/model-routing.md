# Model Routing

## Purpose

Routing tasks to the right model tier is the main lever for managing token cost, dollar cost, wall-clock latency, and accessibility. This document defines the criteria for when to use local prework, when to require a cloud model, and when to halt for human review. It is a default baseline; projects override it via their own `AI_POLICY.md`.

## Three Tiers

Execution is divided into three tiers:
- **Local prework tier** — a local model for cheap, structured, draft-quality work where latency is acceptable.
- **Cloud reasoning tier** — a strong cloud model for code change, full-document authoring, and final review.
- **Human review tier** — required for security-sensitive, production-affecting, or migration work before commit.

## When to Use the Local Tier

Route to the local tier when ALL of the following are true:
- Output is short or structural (codemap, classification, summary, brief expansion) rather than a full prose document.
- No secrets, authentication, payment, or migration logic in scope.
- Output will be reviewed by a stronger cloud model or a human before any commit.
- Total input fits in the local model's context window (typically under 32k tokens; modern models like Qwen 3.5 9B support up to 262k).
- Wall-clock latency is acceptable because the user is not waiting.

## When to Use the Cloud Tier

Route to the cloud tier when ANY of the following are true:
- Code change touches more than three files.
- Code change touches authentication, security, payment, migration, or production configuration.
- Task requires multi-step planning across architectural boundaries.
- Task is the final review gate before merge.
- Local model produced a draft that needs verification or completion.
- User is waiting on output during a live session.

## When to Require Human Review

ALWAYS require human review when:
- Diff touches dependency files (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
- Diff touches infrastructure-as-code (Terraform, Helm, Kubernetes manifests, Dockerfiles).
- Diff touches anything matching the project's `RISKS.md`.
- The change is a data migration, schema change, or anything irreversible without a verified backup.
- Local-tier output is being committed without a cloud verification step.

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

The "Theoretical; not yet measured" entries are honest acknowledgements. Only one task class was empirically tested in v0.1. The remaining measurements land in v0.2.

## Hardware Tiers

The matrix above assumes mainstream Apple Silicon at 16–24 GB unified memory running a 7B–9B model. Workstations with discrete GPUs running 14B–32B coder models may shift some weak-fit tasks toward strong-fit. Hardware-specific recommendations live in `adapters/lm-studio/usage.md`.

## Project-Specific Overrides

Each project may override this routing in its `AI_POLICY.md`. The defaults here are the floor. Projects handling regulated data or production-critical systems may forbid the local tier entirely.

## Verification

Routing claims must be measured per task class. New routing rules require new measurements before they replace the defaults. See `docs/measurement/methodology.md` for how to measure and what to report.
