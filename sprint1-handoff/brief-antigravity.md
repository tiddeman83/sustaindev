# Brief: Antigravity (Gemini-Powered)

You are working in Antigravity (Google's IDE-with-agent-loop product, Gemini-powered) on Sprint 1 of SustainDev v0.1. This brief assigns you six files spanning principles, model routing, the LM Studio adapter, and the measurement docs that are the empirical anchor of the v0.1 release.

This brief is **fully self-contained**. If Antigravity's MCP surface or agent loop fails on any task, fall back to Gemini chat with the brief pasted manually — every task includes the inputs needed to complete it without repository-wide search.

## Setup

Branch:

```bash
git checkout main
git pull
git checkout -b sprint1/antigravity
```

Required reading before touching any file:

1. `sprint1-handoff/README.md`
2. `sprint1-handoff/context.md` — tone rules, vocabulary, anti-patterns
3. `sprint1-handoff/case-study-01-data.md` — pre-digested run data; you write the case study around this
4. `sprint1-handoff/review-criteria.md` — what will get your PR rejected
5. `core/rules/token-efficiency.md` — primary style anchor
6. `build_plan.md` Sections 5 (Design Principles), 6.F (Token Efficiency), 6.H (Scheduling)
7. `revised_sprints_v0.1.md` Section "Concrete Routing Triggers"

## Tasks

### Task 1: `core/principles/development-principles.md`

**Goal.** A condensed set of principles that govern every workflow in SustainDev. Source: the 15 principles in `build_plan.md` Section 5. Tighten and reorder for clarity. Do not invent new principles; condense and clarify the existing ones.

**Word count.** 500–800.

**Required sections, in this order:**

1. `# Development Principles` (H1)
2. `## Purpose` — one short paragraph. What this file is (a foundation, not a checklist), how it relates to the rule files (`token-efficiency.md`, `maintainability.md`, `model-routing.md`), and why principles are listed separately from rules (principles tell you why; rules tell you what).
3. `## The Principles` — numbered list of 10–12 principles, each one or two sentences. Condense the original 15 by merging closely related ones (e.g., principles 9 and 10 about MCP vs codemap can become one principle about choosing the right context source). Do not soften the principles in the merge.
4. `## Applying the Principles` — short prose section. Principles inform decisions when rules don't cover a case. When two principles conflict, prefer the one that protects long-term maintainability. When a workflow is ambiguous, principles point to the safer default.
5. `## Verification` — short prose section. Principles aren't directly testable; their effect shows up in maintainability over months and in token cost over weeks. Reference `docs/measurement/` as where evidence accumulates.

**Source for the original 15 principles** (from `build_plan.md` Section 5):

```text
1. Understand the local project before changing it.
2. Prefer narrow context over broad context.
3. Use codemaps and project context before scanning a whole repository.
4. Preserve project architecture unless there is a concrete reason to change it.
5. Treat maintainability as a required output of every workflow.
6. Make verification explicit before implementation starts.
7. Keep reusable instructions in `core/`, not scattered across tools.
8. Keep adapters thin and generated where possible.
9. Use MCPs for external, dynamic, structured, or interactive context.
10. Use local files and codemaps for stable project-owned context.
11. Capture new ideas separately from active implementation.
12. Prepare deferred work immediately while context is fresh.
13. Schedule non-urgent model-heavy work for better execution windows.
14. Require human review after unattended work.
15. Prefer fewer high-quality skills over many overlapping prompts.
```

**Suggested condensation** (you can deviate if a different merge reads better):

- Merge 9 and 10 into one principle about routing context to the right source.
- Merge 11 and 12 into one principle about idea capture and prework freshness.
- Keep 1–8, 13–15 mostly intact, tightening prose.

**Acceptance.** The reviewer compares your condensed list against the original 15 and confirms no principle has been silently dropped. Your final count is 10–12.

---

### Task 2: `core/rules/model-routing.md`

**Goal.** The objective routing rule file. Replaces the soft "low risk vs high risk" framing with concrete, actionable triggers. Includes a strong-fit / weak-fit matrix grounded in `case-study-01-data.md`.

**Word count.** 600–900.

**Required sections, in this order:**

1. `# Model Routing` (H1)
2. `## Purpose` — one short paragraph. Why routing matters (token cost, dollar cost, wall-clock, accessibility) and what this file does and does not do (it is a default; specific projects override via `<project>/AI_POLICY.md`).
3. `## Three Tiers` — short prose section defining the three execution tiers:
    - **Local prework tier** — local model for cheap, structured, draft-quality work.
    - **Cloud reasoning tier** — strong cloud model for code change, full-document authoring, final review.
    - **Human review tier** — required for security-sensitive, production-affecting, or migration work.
4. `## When to Use the Local Tier` — bulleted list of conditions, each one full sentence. ALL of these should be true:
    - Output is short or structural (codemap, classification, summary, brief expansion) rather than a full document.
    - No secrets, auth, payment, or migration logic in scope.
    - Output will be reviewed by a stronger model or a human before any commit.
    - Total input fits in the local model's context window (typically <32k tokens; modern models like Qwen 3.5 9B support up to 262k).
    - Wall-clock latency is acceptable — the user is not actively waiting.
5. `## When to Use the Cloud Tier` — bulleted list. ANY of these triggers cloud:
    - Code change touches more than three files.
    - Code change touches auth, security, payment, migration, or production config.
    - Task requires multi-step planning across architectural boundaries.
    - Task is the final review gate before merge.
    - Local model produced a draft that needs verification or completion.
    - User is actively waiting on output.
6. `## When to Require Human Review` — bulleted list. ALWAYS require human review when:
    - Diff touches dependencies (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
    - Diff touches infrastructure-as-code (Terraform, Helm, Kubernetes manifests, Dockerfiles).
    - Diff touches anything matching the project's `RISKS.md`.
    - The change is a data migration, schema change, or anything irreversible without a backup.
    - The local-tier output is being committed without a cloud verification step.
7. `## Strong-Fit / Weak-Fit Matrix for the Local Tier` — table. The body of this section is the empirical anchor. Source: `case-study-01-data.md`.

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

   The "Theoretical; not yet measured" entries are honest acknowledgements — only one task class has been empirically tested in v0.1. v0.2 will fill in measurements.

8. `## Hardware Tiers` — short prose section. Note that the matrix above assumes mainstream Apple Silicon at 16–24 GB unified memory running a 7B–9B model. Workstations with discrete GPUs running 14B–32B coder models may shift some weak-fit tasks toward strong-fit. Specific hardware recommendations live in `adapters/lm-studio/usage.md`.
9. `## Project-Specific Overrides` — short prose section. Each project may override this routing in its `AI_POLICY.md`. The default routing here is the floor; projects with stricter requirements (regulated data, production-critical) may forbid the local tier entirely.
10. `## Verification` — short prose section. Routing claims must be measured per task class. New routing rules require new measurements before they replace the defaults. Reference `docs/measurement/methodology.md` for how.

**Do not include:**

- Specific local-model recommendations (those live in `adapters/lm-studio/usage.md`).
- Specific cloud-model recommendations (those live in adapter usage files).
- Marketing voice. The matrix is the value of this file; let the data speak.

**Acceptance.** The matrix has at least 10 rows. Each row has a clear "why" and an evidence column. The "When to Require Human Review" section is non-negotiable — the reviewer will check that nothing is softened relative to the brief.

---

### Task 3: `adapters/lm-studio/usage.md`

**Goal.** A user-facing setup and usage guide for LM Studio + a recommended local model. Honest about what local does and does not do well, citing `docs/measurement/case-study-01.md`.

**Word count.** 700–1000.

**Required sections, in this order:**

1. `# LM Studio Adapter` (H1)
2. `## Purpose` — short paragraph. What this adapter does (provides a local-prework execution tier), what it does not do (replace the cloud tier).
3. `## Prerequisites` — bulleted list. LM Studio installed, supported hardware, recommended model.
4. `## Recommended Model` — short prose. Lead with **Qwen 3.5 9B at MLX 4-bit quantization** for Apple Silicon at 16–24 GB. Note that MLX runs ~15–30% faster than GGUF on Apple Silicon and uses ~10% less memory. Mention Qwen 2.5 Coder 7B as a fallback for older Apple Silicon (M1, 8 GB) or non-MLX setups. Briefly note Codestral 22B as an alternative for users with discrete GPUs or 64GB+ unified memory.
5. `## Setup` — numbered steps:
    1. Download LM Studio from `https://lmstudio.ai`.
    2. In LM Studio, search for and download `qwen/qwen3.5-9b` MLX 4-bit.
    3. Open the *Developer* tab and enable the local server (default port 1234).
    4. Confirm the server is reachable: `curl http://127.0.0.1:1234/v1/models`.
6. `## Configuration` — short prose. Recommended settings: temperature 0.3 (more deterministic), context length set to a generous value (the model supports 262k natively; in LM Studio set the context to a value comfortable for your hardware, e.g., 32k for 16GB systems). Mention the `/no_think` directive for Qwen 3.x users to suppress reasoning overhead on tasks that don't benefit from chain-of-thought.
7. `## What This Adapter Is Good For` — bulleted list, each item one full sentence. Mirror the strong-fit rows from `core/rules/model-routing.md`: idea triage, codemap drafts, summarization, risk extraction, idea expansion, batch prework.
8. `## What This Adapter Is Not Good For` — bulleted list. Mirror the weak-fit rows: full-document drafting, adapter templates, cross-document consistency, time-critical authoring. Cite `docs/measurement/case-study-01.md` once.
9. `## Integration with the Hero Workflow` — short prose. The `idea-to-prepared-task` skill (`core/skills/idea-to-prepared-task/SKILL.md`) uses this adapter for the prepare step when the user opts in. The adapter is optional; users who prefer cloud-only can skip the local tier entirely.
10. `## Honest Limitations` — short prose. Local-model quality varies by hardware. Token counts between LM Studio and cloud APIs use different tokenizers and don't compare apples-to-apples. Reasoning-mode behavior in Qwen 3.x can consume significant token budget; the `/no_think` directive helps but does not fully eliminate the overhead. The 215-second wall-clock measured in case-study-01 is realistic for this hardware tier on a 500-word document — your mileage will vary based on task complexity.
11. `## Troubleshooting` — short bullets:
    - Connection refused: enable the local server in LM Studio's Developer tab.
    - Model not found: verify the loaded model id matches `qwen/qwen3.5-9b` exactly.
    - Empty output: ensure `/no_think` is in the system prompt or raise `max_tokens` substantially.
    - Slow inference: switch from GGUF to MLX quantization on Apple Silicon.

**Do not include:**

- A long pitch for local models. Be matter-of-fact.
- Vendor pricing comparisons.
- Performance claims without referencing case-study-01 or stating "measured per task".

**Acceptance.** A new user can install LM Studio, load Qwen 3.5 9B, and confirm the local server is reachable using only this document and the linked references. The honest-limitations section is preserved in the merge — it is the most important section.

---

### Task 4: `adapters/lm-studio/prework-prompt.md`

**Goal.** The default system prompt that the prework step (in `scripts/schedule/prepare-task.sh` — that script is not in v0.1's scope but the prompt anchors what the script will eventually send) sends to the local model. Production-quality prompt for the strong-fit task classes from `core/rules/model-routing.md`.

**Word count.** 300–500.

**Required structure.**

1. Brief header (H1: `# Prework Prompt`) and a one-paragraph explanation of what this file is, who reads it (the prepare-task script and any human curious about the prompt), and which task classes it applies to.
2. The actual prompt, presented as a markdown code block (triple-backtick) so it can be copy-pasted into a script's payload. The prompt itself should:
    - Begin with `/no_think` on its own line (Qwen 3.x optimization).
    - State the role: "You are a prework assistant for an AI-assisted development repository. Your output is a draft that a stronger model or human will review before any code change."
    - State the constraints: produce only the requested artifact, no preamble, no postamble, no `<think>` tags, no marketing voice, no invented numbers.
    - State the task variability: the user message will specify which prework task class applies (idea triage, codemap draft, summarization, risk extraction, idea expansion). The system prompt is shared across all of them.
    - Define the output format: structured markdown with the headings the user message requests; if no headings are requested, use sensible defaults (e.g., for codemap: same shape as `core/templates/codemap.md`).
3. A short section after the prompt explaining how the prompt is parameterized for each strong-fit task class. Show 4–5 example user-message patterns (one per task class) inside their own code blocks.

**Acceptance.** The prompt is portable (works with Qwen 3.5 9B, Qwen 2.5 Coder, Codestral) and produces consistent structured output across the strong-fit task classes. The reviewer will lift the prompt and run it manually against the local model on a sample task to confirm.

---

### Task 5: `docs/measurement/methodology.md`

**Goal.** The measurement methodology that grounds every "save tokens" or "save dollars" claim in the project. Without this file, every workflow claim is unfounded; with it, claims have a process behind them.

**Word count.** 600–900.

**Required sections, in this order:**

1. `# Measurement Methodology` (H1)
2. `## Purpose` — short paragraph. Why measurement is mandatory in this project (without numbers, "sustainable" is marketing; with numbers, claims are evidence). What this file standardizes (how to measure) and what it does not do (it does not collect the measurements; case studies do that).
3. `## What Gets Measured` — bulleted list, each one full sentence. Per task: input tokens, output tokens, wall-clock seconds, dollar cost (where applicable), output quality assessment, completeness (was the task fully completed or only partially).
4. `## What "A Task" Means` — short prose section. A task is a single, complete unit of work that has a clear before-and-after: drafting a specific file, classifying an idea, producing a codemap. Multi-task workflows are measured by summing the per-task measurements. Continuous chat sessions are not tasks for measurement purposes; they are noise.
5. `## Comparing Approaches` — short prose section. The standard comparison is "approach A vs approach B for the same task". Both approaches must be run end-to-end with the same task definition. Cherry-picking one approach's best run vs another's worst run is not measurement; it is advocacy.
6. `## Token Counting Caveats` — short prose section. Tokenizers differ between providers (OpenAI's tiktoken, Anthropic's tokenizer, local models use their own). Cross-provider token comparisons are approximate. Dollar cost is the apples-to-apples metric when comparing across providers; wall-clock is the apples-to-apples metric when comparing user experience.
7. `## What to Report` — short prose section. A measurement report (`docs/measurement/case-study-XX.md`) includes: task description, tool setup (cloud model, local model if applicable, hardware), per-approach metrics in a table, quality comparison, what worked, what did not, reproducibility notes. The issue template at `.github/ISSUE_TEMPLATE/measurement_report.md` mirrors this structure for community submissions.
8. `## What Not to Claim` — bulleted list:
    - Do not claim percentage savings on a single task. Percentages are meaningful only across many tasks of the same class.
    - Do not extrapolate from one hardware tier to another without measuring.
    - Do not present an estimate as a measurement. Estimates are clearly labeled.
    - Do not claim a workflow is "10x faster" or "90% cheaper" without a measurement that produced those numbers.
9. `## How To Reproduce a Measurement` — short prose section. Each case study must include enough detail (model versions, prompts used, hardware, settings) for an independent reproducer to attempt the same measurement and report whether they got the same numbers. If a measurement cannot be reproduced, it is not evidence — it is anecdote.
10. `## Verification` — one short paragraph. The methodology itself is reviewed and updated as case studies accumulate. If multiple case studies show that a measurement convention produces misleading comparisons, the methodology updates and the existing case studies note the methodology version they used.

**Do not include:**

- Specific token-counting code. Tooling lives separately.
- Vendor-specific pricing — pricing changes; the methodology is durable.
- Complaints about other projects' measurement practices.

**Acceptance.** A reader can take any workflow claim in the project, follow this methodology, and produce a comparable measurement that supports or refutes the claim.

---

### Task 6: `docs/measurement/case-study-01.md`

**Goal.** The first case study, documenting the local-model test from Sprint 1. Empirical anchor for the strong-fit / weak-fit matrix in `core/rules/model-routing.md`. Honest, specific, no exaggeration in either direction.

**Inputs.** All the data and analysis you need is in `sprint1-handoff/case-study-01-data.md`. Use the structure suggested there as a starting point but write the prose in your own voice (matching the style anchor `core/rules/token-efficiency.md`).

**Word count.** 800–1200.

**Required sections, in this order:**

1. `# Case Study 01: Local-Model Drafting of a Markdown Rule File` (H1)
2. `## Summary` — one short paragraph. The single-sentence finding (full-document markdown drafting on 16–24 GB Apple Silicon with Qwen 3.5 9B is a weak fit for the local-prework tier) plus a sentence on what task classes remain strong fits.
3. `## What Was Tested` — short prose section sourced from `case-study-01-data.md` "What Was Tested".
4. `## Setup` — table reproducing the setup parameters (model, hardware, system prompt path, etc.).
5. `## Run 1: Default Settings` — short prose narrating Run 1 from the data file. Include the metrics table.
6. `## Run 2: With /no_think` — short prose narrating Run 2 from the data file. Include the metrics table.
7. `## Quality Assessment` — short prose. What was good, what was weak, what was missing. Cite the actual draft if useful (`scripts/sprint1/output/draft.md`).
8. `## Cloud-from-Scratch Counterfactual` — short prose with the comparison table from the data file. Be clear that the cloud-only number is an estimate, not a measurement, and explain why (the cloud baseline was not run separately for this case study; the actual Sprint 1 deliverable was authored cloud-from-scratch by Cowork).
9. `## Conclusions` — numbered list, 4–5 conclusions, each one short paragraph. Use the conclusions in the data file as raw material; rephrase in your own voice; do not soften them.
10. `## What This Does Not Prove` — short prose section. The case study tested one task class on one hardware tier with one model. Other strong-fit task classes (idea triage, codemap drafts, summarization) are claimed but not yet measured. Those measurements are v0.2 work.
11. `## Reproducibility` — short prose. List what an independent reproducer needs: hardware specs, LM Studio version, model variant, system prompt and user brief paths in this repo, the script `scripts/sprint1/run_prework.py`. Note that token counts will vary by tokenizer version and prompt phrasing.

**Do not:**

- Soften the conclusions. The wall-clock cost is real and the data shows it.
- Bash Qwen 3.5 9B as a model. The model performed within expectations for its class. The lesson is about routing, not about the model.
- Extrapolate to untested task classes. The matrix in `model-routing.md` makes the theoretical claim; this case study only supports the one row that was measured.
- Use marketing voice. This is the most-cited document in the v0.1 release; it must read as evidence, not as a sales pitch.

**Acceptance.** A skeptical reader leaves the case study believing two things simultaneously: (1) the local tier's value proposition is real for the task classes the matrix claims, and (2) the project does not overclaim and is honest about what was actually measured. If the case study reads as advocacy rather than evidence, it fails review.

---

## Hand Back

When all six files are on `sprint1/antigravity` and pass `.github/workflows/validate.yml` locally:

```bash
git add core/principles/development-principles.md core/rules/model-routing.md adapters/lm-studio/ docs/measurement/
git commit -m "Sprint 1 Antigravity (Gemini) deliverables"
git push -u origin sprint1/antigravity
```

Open a PR titled `Sprint 1: Antigravity (Gemini) deliverables` against `main`. PR description: list the six files, note any deviations from the brief, confirm CI passes locally, tag the reviewer.

## Self-Check Before Pushing

- All six files exist at the exact paths in this brief.
- Each file's word count is within range (`wc -w <file>`).
- The strong-fit / weak-fit matrix in `model-routing.md` matches the data in `case-study-01-data.md`. No row claims measurement evidence that does not exist.
- `case-study-01.md` does not exaggerate findings. The wall-clock cost is reported honestly.
- Voice is consistent across the six files; matches `core/rules/token-efficiency.md`.
- All cross-file references resolve once the other tool branches merge.
- No private project names anywhere.
- The honest-limitations section in `adapters/lm-studio/usage.md` is intact and prominent.

## Antigravity-Specific Notes

If Antigravity's MCP tooling fails or limits you (e.g., MCP filesystem access fails, agent loop times out, repository search is unreliable), fall back to:

1. Open Gemini chat directly.
2. Paste this brief as the first message.
3. Paste `sprint1-handoff/context.md` as the second message.
4. Paste `sprint1-handoff/case-study-01-data.md` as the third message (only needed for tasks 2 and 6).
5. Work through tasks one at a time, copy results into the repo manually.

The brief is structured to support either flow. Document which mode you used in the PR description so we know how to weight Antigravity feedback in `docs/reviews/sprint-01-review.md`.

If anything blocks you for more than 30 minutes, leave a note in `docs/reviews/sprint-01-blockers.md` and continue with the next task.
