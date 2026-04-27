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
| Idea triage / classification | Conditionally strong | Fast (3.4 s/file), zero hallucinations on 80-row output, ~89% strict accuracy. Needs rich context (RISKS.md + MAINTAINABILITY_NOTES) and human spot-check on edge cases. | Measured in `docs/measurement/case-study-04.md`. |
| Codemap drafts from file lists | Conditionally strong | Zero hallucinations on signatures, accurate DI scope, useful integration of context across files. Needs sufficient `--max-tokens` (~8k for 12 service files) to keep reasoning channeled rather than leaking into output. | Measured in `docs/measurement/case-study-05.md`. |
| Summarization of long documents | Conditionally strong | Content quality high (correct language, structure, takeaway). Packaging unreliable: at smaller context, reasoning leaks into output; at larger context, all output goes to reasoning channel. Recovery requires post-processing. | Measured in `docs/measurement/case-study-06.md`. |
| Risk extraction from existing prose | Strong | Bounded input, bounded structured output, project-aware context. Clean packaging on first try, arithmetic correct, severity mapping clean across languages. | Measured in `docs/measurement/case-study-07.md`. |
| Idea expansion: rough capture → structured task brief | Strong | Hero-workflow centerpiece; structured output from rich context. | Measured in `docs/measurement/case-study-03.md`. |
| Batch / overnight prework | Strong | Wall-clock cost is zero. | Theoretical; not yet measured. |
| Full-document drafting from rich brief | Weak | Reasoning overhead + wall-clock cost outweighs cloud savings. | Measured in `docs/measurement/case-study-01.md`. |
| Adapter templates | Weak | Requires accurate tool-specific knowledge that 9B class models get wrong. | Theoretical; not yet measured. |
| Cross-document consistency checks | Weak | Wall-clock penalty too high for active sessions. | Theoretical; not yet measured. |
| Time-critical authoring | Weak | User is waiting; latency is unacceptable. | Implicit from case-study-01. |

The "Theoretical; not yet measured" entries are honest acknowledgements. Six task classes are now empirically tested (full-document drafting in case-study-01, idea expansion in case-study-03, idea triage in case-study-04, codemap drafts in case-study-05, summarization in case-study-06, risk extraction in case-study-07); the remaining strong-fit rows are v0.2 measurement targets. For a synthesis read across the case studies — the three reasoning regimes, the post-processing pattern, the conditional-vs-unconditional fit shape, and a setup checklist — see `docs/measurement/v0.1.x-lessons.md`. Rule of thumb: set `max_tokens` just high enough to keep reasoning channeled, set `lm_studio_context` just large enough for the prompt, and prefer task classes with bounded input + bounded structured output + project-aware context for unconditional strong fits.

## Hardware Tiers

The matrix above assumes mainstream Apple Silicon at 16–24 GB unified memory running a 7B–9B model. Workstations with discrete GPUs running 14B–32B coder models may shift some weak-fit tasks toward strong-fit. Hardware-specific recommendations live in `adapters/lm-studio/usage.md`.

## Project-Specific Overrides

Each project may override this routing in its `AI_POLICY.md`. The defaults here are the floor. Projects handling regulated data or production-critical systems may forbid the local tier entirely.

## Verification

Routing claims must be measured per task class. New routing rules require new measurements before they replace the defaults. See `docs/measurement/methodology.md` for how to measure and what to report.
