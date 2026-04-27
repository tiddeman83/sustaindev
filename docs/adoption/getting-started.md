# Your First 30 Minutes With SustainDev

This walkthrough takes you from "I just heard about this repo" to "I have a real local-model probe output on my own project." Concrete CLI from clone to first measurement.

If you haven't yet, read [`docs/measurement/v0.1.x-lessons.md`](../measurement/v0.1.x-lessons.md) first — it explains *why* the workflow looks the way it does. This doc is the *how*.

## What You'll Have At The End

- A local LM Studio model running on your machine.
- A SustainDev project layer for one of your real projects (or a quick-start template).
- One real probe output: a triage of your repo's modified-and-untracked files into commit-now / review-first / archive / build-artifact buckets.
- Enough context to decide whether to keep going, or to know what didn't work and why.

## What You'll Need

- macOS or Linux. Windows works for the LM Studio side; the shell scripts are POSIX. Adopters on Windows-only setups should run the Python probes directly and skip the shell wrappers.
- ~16 GB of free RAM (24 GB comfortable). 8 GB systems can run a 7B model with a smaller context window; expect slower inference and tighter prompt budgets.
- ~10 GB of disk space for LM Studio + a model.
- A real project to point the probe at. The output is more useful when the input is real — even a half-finished personal project beats a hello-world.
- Roughly 30-45 minutes of unbroken time. The model setup takes 10-15 min; the rest is reading and one short LLM call.

## Step 1 — Clone the repo

```sh
git clone https://github.com/<your-fork>/sustaindev.git
cd sustaindev
```

You don't need to install anything from the repo; the probe scripts have zero external Python dependencies (urllib + stdlib only). They live in `scripts/sprint1/` and `scripts/schedule/` and you'll run them directly.

If you prefer to keep SustainDev separate from the project you'll be probing: clone it once into your home directory, then invoke its scripts by absolute path from your project's working directory. That's the pattern this walkthrough uses.

## Step 2 — Install LM Studio

Download from [https://lmstudio.ai](https://lmstudio.ai) and install. It's a desktop app; nothing fancy.

When you launch it, you'll see a model browser. Search for and download:

```text
qwen/qwen3.5-9b
```

Pick the **MLX 4-bit** quantization on Apple Silicon (it runs ~15-30% faster than GGUF and uses ~10% less memory). On other hardware: pick GGUF Q4_K_M.

Why this model? It's the one all seven case studies measured. v0.1.x's claims are about Qwen 3.5 9B specifically; using a different model puts you in unmeasured territory. See [`docs/measurement/v0.1.x-lessons.md`](../measurement/v0.1.x-lessons.md) "Where v0.1.x Doesn't Have Answers Yet" for what changes when you change models.

## Step 3 — Configure context length (this is the trap)

LM Studio's default context length is **4,096 tokens**. This is too small for anything serious. Before you run any probe, change it:

1. In LM Studio's My Models tab, click the gear icon next to `qwen/qwen3.5-9b`.
2. Find **Context Length** (some versions call it `n_ctx`).
3. Set to **16384** (16k). Or 32768 if you have RAM headroom.
4. **Save and reload the model.** This is critical. The slider alone doesn't take effect — the model must be unloaded and reloaded.

Why this matters: the v0.1.x case studies surfaced two failure modes related to context size. At 4k, your prompts overflow before they get to the model. At 16k+, prompts fit but reasoning lands in the proper channel. See [v0.1.x-lessons.md "The Three Reasoning Regimes"](../measurement/v0.1.x-lessons.md) for the details.

## Step 4 — Enable the local server

In LM Studio:

1. Open the **Developer** tab.
2. Toggle **Local Server** on. Default port: 1234.
3. Confirm from your terminal:

```sh
curl -s http://127.0.0.1:1234/v1/models | python3 -m json.tool | head -10
```

You should see your loaded model id. Note it — if it's not exactly `qwen/qwen3.5-9b` (some LM Studio versions add prefixes), you'll need to pass the actual id via `LM_STUDIO_MODEL=<id>` to the probe scripts.

## Step 5 — Set up the project layer for your target project

The probe scripts read your project's *project layer* files for context. If you don't have these yet, the scripts still run — but the model produces generic output instead of project-aware output. The output quality difference is real (case-study-04 measured it).

In your target project's root, create at minimum these two:

```sh
cd /path/to/your/project
touch PROJECT_CONTEXT.md CODEMAP.md
```

Open them in your editor and fill in roughly:

`PROJECT_CONTEXT.md`:

```markdown
# Project Context: <your-project-name>

## What this is
<One sentence about the purpose. Who uses it. What it integrates with.>

## Tech stack
- Language:
- Framework:
- Datastore:
- Deployment target:

## Architecture (one paragraph)
<Cover the main layers/modules and how data flows between them.>
```

`CODEMAP.md`:

```markdown
# Codemap: <your-project-name>

## Top-level layout
<dir/>          # purpose
<config-file>   # purpose
<test-dir/>     # purpose

## Where common tasks touch
- To add an X, look in <path>/.
- To change Y, look in <path>/.

## Stable anchors
- <entry-point-file>
- <main-config-file>

## Hot spots
- <file-that-changes-a-lot> — because <reason>.
```

If your project is non-trivial, consider also creating `RISKS.md` and `MAINTAINABILITY_NOTES.md`. The triage probe specifically uses these (see step 6's notes). Templates for the full set are in `core/templates/`.

Total time on this step: 10-20 minutes if your project is small, longer if it's complex. **You can do this iteratively** — the first probe will work with just PROJECT_CONTEXT and CODEMAP; the others get loaded if present.

## Step 6 — Run your first probe

The most useful first probe is `triage-files.py`. It classifies your modified-and-untracked files into four buckets, with a one-line rationale per file. It's fast (~3-5 minutes for ~50 files) and the output gives you a concrete sense of how the model handles your project.

```sh
cd /path/to/your/project

python3 ~/sustaindev/scripts/sprint1/triage-files.py
```

What happens:

1. The script runs `git status --porcelain=v1` to find your modified-and-untracked files.
2. It auto-scales `--max-files` against your `--lm-studio-context` (default 16384). At 16k context, that's roughly 130 files; the script stops before exceeding budget.
3. It reads `PROJECT_CONTEXT.md`, `CODEMAP.md`, `RISKS.md`, `MAINTAINABILITY_NOTES.md`, `VERIFY.md` if present.
4. It calls LM Studio with the file list + the project context + a system prompt that defines the four buckets.
5. It writes the model's output (post-processed for clean counts) to `.sustaindev/measurement/triage-<timestamp>.md` plus a JSON record.

Expected output on stderr:

```text
Auto-scaled --max-files to 130 (context=16384, reserved=7000, budget=9000 tokens / 80 tokens/file).
Calling LM Studio (qwen/qwen3.5-9b) to triage 47 files...
Done. wall_clock=180.4s tokens=7500 files=47 reasoning_chars=400 output_chars=2300
Markdown: .sustaindev/measurement/triage-2026-04-27T180000Z.md
JSON:     .sustaindev/measurement/triage-2026-04-27T180000Z.json
```

If you see this, you've completed the v0.1.x setup. The model just classified your repo's untracked files. Open the markdown file:

```sh
cat .sustaindev/measurement/triage-*.md | less
```

You'll see a table with one row per file, each tagged with a bucket and a one-sentence rationale. The last line will be a verified counts summary like `Counts (verified by post-processing): commit-now=23, review-first=4, archive=12, build-artifact=8 (total=47; rows seen=47)`.

## Step 7 — Read the output critically

This is the most important step and the one most likely to be skipped. The model's output is *probably right* but *not always right*. Per case-study-04, expect roughly 89% strict accuracy on the first run.

Three things to check:

1. **The `review-first` bucket.** If it's empty, either your repo really has nothing risky (possible) or you didn't load `RISKS.md` (more likely). Without that file, the model defaults to confident "commit-now" classifications. Add `RISKS.md` and re-run if your project has any sensitive code.

2. **The `build-artifact` classifications.** The model can confuse "directory contents are runtime state" with "the directory marker should be ignored." Check that `.gitkeep` files, configuration directories, and intentional empty-directory markers haven't been classified as build-artifact. v0.1.3 added a system-prompt rule for this; if you see misclassification anyway, it's worth a manual review.

3. **The counts line.** Should match the actual table. The script's post-processor recomputes this; if it doesn't, file an issue.

Spend 5-10 minutes reading the table. The point isn't to trust the model blindly; it's to use the output as a starting point for your own review.

## Step 8 — What to do if something went wrong

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Connection refused` at port 1234 | LM Studio's local server isn't running | LM Studio → Developer → toggle Local Server on |
| `HTTP 400: model not found` | Loaded model id doesn't match `qwen/qwen3.5-9b` | Run `curl http://127.0.0.1:1234/v1/models` to see the actual id; pass via `LM_STUDIO_MODEL=...` |
| `HTTP 400: n_keep > n_ctx` | LM Studio context too small for the prompt | Bump context to 16384 (or 32768) and **reload the model** |
| Empty output, "model returned no usable content" | `/no_think` failed; budget too tight | Try `--max-tokens 6000` or larger |
| Output starts with "Thinking Process: 1. Analyze..." | Reasoning leaked into visible content | Probe scripts post-process for this in v0.1.6+; if you see it, you may be on an older version |
| Wall-clock > 5 min for triage | Hardware or model size mismatch | Check Activity Monitor — model swapping = too small RAM. Try Qwen 2.5 Coder 7B as fallback |

If your symptom isn't here, see [`docs/adoption/faq.md`](faq.md). If still stuck: open an issue with your `.sustaindev/measurement/triage-<timestamp>.json` file attached. The measurement record has everything we need to debug.

## Step 9 — What to do when it works

Now you've got a measurement. Two natural next moves:

**A) Run another probe on the same project.** The synthesis doc describes six measured task classes. Try `prepare-task.py` (the hero workflow's brief preparation step) on a captured idea. Or `extract-risks.py` on a known-issues document. Or `summarize-doc.py` on a long internal document. Each one validates a different matrix row on your project's actual content.

**B) Apply the triage output.** The model classified your files. Now decide which classifications you accept, fix any disagreements, and use the buckets to guide an actual cleanup commit. The triage isn't theoretical — it's a directly actionable to-do list.

The local tier shines when the output becomes input to your real workflow. A triage you read and discard is half value; a triage that drives an actual `git add` + `git commit` is full value.

## Where to go from here

- Read [`docs/measurement/v0.1.x-lessons.md`](../measurement/v0.1.x-lessons.md) if you skipped it earlier — it explains the patterns this doc just demonstrated.
- Read [`docs/adoption/faq.md`](faq.md) for the questions you're probably about to ask.
- Read [`core/rules/model-routing.md`](../../core/rules/model-routing.md) when you want to understand which task classes are strong vs weak fits.
- Read individual case studies in `docs/measurement/` when something specific surprises you.
- Open issues for missing answers. The measurement repository at `.github/ISSUE_TEMPLATE/measurement_report.md` is the formal way to share your own probe results.

## What you should not expect

- The local tier doesn't replace cloud models for code change. It's prework: triage, summarization, brief preparation. The router separates them on purpose.
- Expect ~89-95% accuracy on first run, not 100%. Plan for 5-15 minutes of human triage on the output.
- Wall-clock is roughly equivalent to cloud-only on a single task. The savings compound across many tasks (the cloud token cost stays at zero; human triage time is bounded).
- Six matrix rows are measured. The other four are still theoretical. If you're routing a task class that isn't measured, treat the routing decision as a hypothesis to test.

## Done

If you got a triage output and read it critically: you've completed your first 30 minutes with SustainDev. The repo from this point on is just more of the same pattern — different probes, different task classes, the same cycle of "read context, call model, post-process, triage."

The hard part is the cycle. The easy part is doing it again.
