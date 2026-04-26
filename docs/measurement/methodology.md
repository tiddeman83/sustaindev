# Measurement Methodology

## Purpose

Measurement is mandatory: without numbers, "sustainable" is marketing. With numbers, workflow claims are evidence. This file standardizes how to measure model usage, cost, and latency. It defines what to capture; it does not collect the data. Case studies do that.

## What Gets Measured

- **Input tokens:** the number of tokens sent to the model in the prompt.
- **Output tokens:** the number of tokens the model generated in the completion.
- **Wall-clock seconds:** end-to-end latency from request dispatch to final artifact write.
- **Dollar cost:** API cost, where applicable, at the provider's pricing tier at the time of the run.
- **Output quality:** qualitative review of whether the output meets the task requirements.
- **Completeness:** binary — was the task finished, or only partially completed?

## What "A Task" Means

A task is a single, complete unit of work with a clear before-and-after: drafting a specific file, classifying an idea, producing a codemap. Multi-task workflows are measured by summing the per-task measurements. Continuous chat sessions are not tasks for measurement purposes; they are noise.

## Comparing Approaches

The standard comparison is "approach A vs approach B for the same task." Both approaches must be run end-to-end with the same task definition and input. Cherry-picking one approach's best run against another's worst is advocacy, not measurement.

## Token Counting Caveats

Tokenizers differ across providers: OpenAI uses tiktoken, Anthropic uses its own, local models use their own. Cross-provider token comparisons are approximate. Dollar cost is the apples-to-apples metric when comparing efficiency across providers. Wall-clock latency is the apples-to-apples metric when comparing user experience.

## What to Report

A measurement report at `docs/measurement/case-study-XX.md` includes: a task description, the tool setup (cloud model, local model if applicable, hardware), a per-approach metrics table, a quality comparison, what worked and what failed, and reproducibility notes. The issue template at `.github/ISSUE_TEMPLATE/measurement_report.md` mirrors this structure for community submissions.

## What Not to Claim

- Do not claim percentage savings on a single task. Percentages mean something only across many tasks of the same class.
- Do not extrapolate from one hardware tier to an untested tier without measuring.
- Do not present an estimate as a measurement. Estimates must be labeled as estimates.
- Do not claim "10x faster" or "90% cheaper" without a measurement that produced those numbers.

## How To Reproduce a Measurement

Every case study includes the detail needed for reproduction: model versions, prompts, hardware, settings. An independent reproducer should be able to attempt the same measurement and report whether they got the same numbers. If a measurement cannot be reproduced, it is anecdote, not evidence.

## Verification

The methodology itself is reviewed and updated as case studies accumulate. If multiple case studies show that a measurement convention produces misleading comparisons, the methodology updates, and existing case studies note the methodology version they used.
