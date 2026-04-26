# What "Sustainable" Means in SustainDev

The word *sustainable* gets used loosely in software. This document defines exactly what it means here, so contributors and users have a shared vocabulary and a skeptical reader can hold the project to its claims.

## Five Dimensions

SustainDev treats sustainability as five concrete things, in this order of priority:

### 1. Token cost per task

The most direct measure. How many input + output tokens does a typical task consume across the full session? A workflow that reduces redundant context-gathering reduces token cost.

This is measurable. SustainDev's measurement methodology (see [`measurement/methodology.md`](measurement/methodology.md), shipping in Sprint 1) defines how to count.

### 2. Dollar cost per task

Tokens are a proxy. Cost is the metric people actually feel. Different models have different per-token prices, and different routing decisions change the bill.

A workflow that runs the prep step on a local model and the change step on a cloud model can reduce cost by 60–90% on the prep portion (local = $0) while keeping reasoning quality. The case studies report both tokens and dollars.

### 3. Environmental footprint

Inference uses energy. Energy uses water (cooling) and produces emissions, depending on grid mix. The exact numbers vary widely and are hard to attribute precisely to one user, but the directional truth is solid: **fewer tokens used = less compute consumed = less energy burned.**

We don't quantify this in case studies (the data is too contested), but we do note it as a real benefit of the underlying optimization. If you're skeptical that personal token reduction matters environmentally, that's fair — the aggregate effect across millions of developers is what matters, not one person's marginal session.

### 4. Accessibility for developers without paid budgets

The dev community is global. Plenty of capable developers don't have access to paid AI subscriptions, reliable high-bandwidth internet, or unlimited cloud-model quota. A system that delegates ~80% of context work to a local model is **a system that works in places where pay-per-token cloud-only systems don't.**

This is the dimension that gets the least attention in mainstream tooling. SustainDev treats it as primary.

### 5. Longevity across model generations

Models change every few months. A workflow tied to specific prompt quirks of `claude-3-5-sonnet-20241022` ages badly. SustainDev's `core/` content is written to describe **what work is being done**, not **how to flatter a specific model into doing it**. Adapters absorb the model-specific quirks; the core stays stable.

This is what *durable knowledge* means: when GPT-6 ships, you update the adapter, not the workflow.

## What Sustainability Does *Not* Mean Here

- It does not mean "reduce AI use to zero." That's a different argument.
- It does not mean "always use the cheapest model." Cheap models on tasks they can't handle waste tokens through retries and rework.
- It does not mean "everything must run locally." Cloud models do irreducibly hard reasoning better; the goal is to reserve them for that.
- It does not mean "open-source models are morally superior." It means "having local-model options preserves access for everyone."

## How To Tell If The Claim Is Real

For any workflow shipped in this repo, ask:

- Is there a measurement case study with real numbers?
- Does it report tokens, dollars, and time?
- Does it compare against the obvious baseline (just doing the task in the cloud tool)?
- Are the numbers plausible (not ten-bagger savings on simple tasks)?

If a workflow doesn't pass that bar, it's marked `status: experimental` in front matter. If you find a workflow making sustainability claims without numbers, that's a bug — please open an issue.

## How To Contribute Measurement Reports

Use [`.github/ISSUE_TEMPLATE/measurement_report.md`](../.github/ISSUE_TEMPLATE/measurement_report.md). The community measurement repository is the most valuable thing in this project. Architecture is cheap; evidence is rare.

## Honest Caveats

- Local-model quality varies by hardware. A 14B model on an M1 MacBook Air may underperform a 7B model on a workstation with a discrete GPU.
- Token counts vary by tokenizer. Comparisons should hold tokenizer constant where possible.
- Some tasks genuinely need cloud-model power and won't show savings — that's expected. The system is designed for the *distribution* of tasks across a typical week, not every task.
- A perfectly engineered prompt in the cloud can sometimes beat a poorly-tuned local-prep + cloud-finish flow. The win is when the **typical** developer applies the **default** workflow and still saves tokens — not when an expert squeezes maximum savings out of a single session.
