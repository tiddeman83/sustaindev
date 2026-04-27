#!/usr/bin/env python3
"""
summarize-doc.py — probe for case-study-06: summarization as a strong-fit
local-tier task class.

Asks a local LM Studio model to summarize a long document into a bounded
output. The point is to measure whether reasoning overhead scales with INPUT
size (the document being summarized) or stays bounded by OUTPUT structure.
This is the open question case-study-05 left.

Usage:

    python3 path/to/summarize-doc.py <doc-path> [options]

Common options:
    --target-words N         Target summary length in words. Default 500.
                             The model is instructed but not strictly bound
                             to this; expect ±25% in practice.
    --shape SHAPE            One of: executive, structured, bulleted.
                             Default: structured.
    --lm-studio-context N    Loaded model context length (default 16384).
                             For long docs (>30KB) you may need 32768.
    --max-tokens N           Output budget. Default 2000 (smaller than other
                             probes because summary output is bounded).
    --dry-run                Print the prompt that would be sent and exit.
    --model ID               Override loaded model id.
    --temperature FLOAT      Default 0.2.
    --force                  Skip the pre-flight context check.

Output:
    <project-root>/.sustaindev/measurement/summary-<timestamp>.md
    <project-root>/.sustaindev/measurement/summary-<timestamp>.json

The output's measurement JSON includes input_chars, input_tokens_estimated,
and reasoning_chars so case-study-06 can answer: at this hardware tier,
does reasoning scale linearly with input, sublinearly, or stay bounded?

Local-only by design. Zero external dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Shared post-processing utilities (v0.1.6+).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from postprocess import (
    detect_planning_prose,
    extract_after_planning,
    extract_last_draft,
)


DEFAULT_LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3.5-9b"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 2000
DEFAULT_TIMEOUT = 900
DEFAULT_TARGET_WORDS = 500


SYSTEM_PROMPT_TEMPLATE = """\
/no_think

You are a technical document summarizer. Your output will be read by an engineer
who has already seen the source and wants a quick reference.

Summary shape: {shape_description}

Length target: {target_words} words (acceptable range: {target_min}-{target_max}).

Output rules — follow exactly:

1. Produce ONLY the summary. No preamble, no postamble, no <think> tags, no
   meta-commentary about the document or the summarization process.
2. Preserve the source's primary language. If the source is non-English, keep
   the summary in that language.
3. Cite section headers when summarizing a section's content; do not invent
   section names that aren't in the source.
4. Do not invent facts, decisions, or claims that aren't in the source. If
   something is implied but not stated, write "(implied)".
5. The first sentence is a one-line description of what the document is.
6. The last sentence is the single most important takeaway.
7. Stay within the length target. Going substantially over wastes the
   reader's time.
"""

SHAPE_DESCRIPTIONS = {
    "executive": "A flowing prose summary in 3-5 paragraphs. No headers, no bullets.",
    "structured": "A summary with H2 section headers mirroring the source's structure, with 1-3 sentences per section.",
    "bulleted": "A summary as a single bulleted list, ~5-12 points, each one full sentence.",
}


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"WARNING: {msg}", file=sys.stderr)


def utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_filestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def call_lm_studio(url: str, model: str, system_prompt: str, user_message: str,
                   temperature: float, max_tokens: int, timeout: int) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature, "max_tokens": max_tokens, "stream": False,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = "(no body)"
        fail(
            f"LM Studio rejected the request with HTTP {e.code} {e.reason}.\n"
            f"  Server said: {err_body}\n"
            f"  Common causes: model id mismatch, context too small, max_tokens too high.",
            code=5,
        )
    except urllib.error.URLError as e:
        fail(f"Could not reach LM Studio at {url}: {e}", code=2)
    return {}


def extract_content(response: dict) -> tuple[str, str]:
    try:
        message = response["choices"][0]["message"]
    except (KeyError, IndexError) as e:
        fail(f"Unexpected response shape: {e}")
    raw = (message.get("content") or "").strip()
    reasoning = (message.get("reasoning_content") or "").strip()
    stripped = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    if stripped:
        return stripped, reasoning
    if reasoning:
        warn("content empty; using reasoning_content as fallback.")
        return reasoning, reasoning
    fail("Model returned no usable content.", code=4)
    return "", ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("doc_path", nargs="?")
    parser.add_argument("--project-root", default=os.getcwd())
    parser.add_argument("--target-words", type=int, default=DEFAULT_TARGET_WORDS)
    parser.add_argument("--shape", default="structured", choices=list(SHAPE_DESCRIPTIONS.keys()))
    parser.add_argument("--lm-studio-url", default=os.environ.get("LM_STUDIO_URL", DEFAULT_LM_STUDIO_URL))
    parser.add_argument("--lm-studio-context", type=int, default=int(os.environ.get("LM_STUDIO_CONTEXT", "16384")))
    parser.add_argument("--model", default=os.environ.get("LM_STUDIO_MODEL", DEFAULT_MODEL))
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()
    if args.help or args.doc_path is None:
        print(__doc__)
        sys.exit(0)
    return args


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    doc_path = (project_root / args.doc_path).resolve() if not Path(args.doc_path).is_absolute() else Path(args.doc_path)
    if not doc_path.is_file():
        fail(f"Document not found: {doc_path}")

    doc_text = doc_path.read_text(encoding="utf-8")
    input_chars = len(doc_text)
    estimated_input_tokens = int(input_chars / 3.8)

    target_min = int(args.target_words * 0.75)
    target_max = int(args.target_words * 1.25)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        shape_description=SHAPE_DESCRIPTIONS[args.shape],
        target_words=args.target_words,
        target_min=target_min,
        target_max=target_max,
    )
    user_message = (
        f"Source document: `{doc_path.relative_to(project_root) if doc_path.is_relative_to(project_root) else doc_path}`\n\n"
        f"---\n\n"
        f"{doc_text}\n"
    )

    # Pre-flight context check.
    prompt_chars = len(system_prompt) + len(user_message)
    estimated_prompt_tokens = int(prompt_chars / 3.8)
    estimated_total = estimated_prompt_tokens + args.max_tokens + 512
    if estimated_total >= args.lm_studio_context and not args.force:
        fail(
            f"Pre-flight: estimated context need ({estimated_total} tokens) "
            f"exceeds --lm-studio-context ({args.lm_studio_context}).\n"
            f"  Document:      {input_chars} chars (~{estimated_input_tokens} tokens)\n"
            f"  Output budget: {args.max_tokens}\n"
            f"Options:\n"
            f"  - Raise LM Studio's context length to {((estimated_total // 1024) + 1) * 1024} or 32768.\n"
            f"    Reload the model after changing the slider.\n"
            f"  - Lower --max-tokens (default {DEFAULT_MAX_TOKENS}).\n"
            f"  - Pass --force to call anyway (model will likely reject it).\n"
            f"  - Use --shape bulleted with smaller --target-words for a smaller output.",
            code=6,
        )

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN")
        print("=" * 60)
        print(f"Document: {doc_path}")
        print(f"Input chars: {input_chars} (~{estimated_input_tokens} tokens)")
        print(f"Shape: {args.shape}")
        print(f"Target words: {args.target_words} (range {target_min}-{target_max})")
        print(f"Total estimated context: {estimated_total} tokens")
        print(f"--- system prompt (first 600 chars) ---")
        print(system_prompt[:600])
        print(f"--- user message (first 800 chars) ---")
        print(user_message[:800])
        return 0

    measurement_dir = project_root / ".sustaindev" / "measurement"
    measurement_dir.mkdir(parents=True, exist_ok=True)
    stamp = utc_filestamp()
    out_md = measurement_dir / f"summary-{stamp}.md"
    out_json = measurement_dir / f"summary-{stamp}.json"

    print(
        f"Calling LM Studio ({args.model}) to summarize {doc_path.name} "
        f"({input_chars} chars, ~{estimated_input_tokens} tokens, shape={args.shape}, "
        f"target={args.target_words} words)...",
        file=sys.stderr,
    )
    t0 = time.perf_counter()
    response = call_lm_studio(args.lm_studio_url, args.model, system_prompt, user_message,
                              args.temperature, args.max_tokens, args.timeout)
    elapsed = time.perf_counter() - t0
    raw_output, reasoning = extract_content(response)
    usage = response.get("usage", {}) or {}

    # Post-process: handle three failure modes from case-study-06.
    # (1) Reasoning leaked into visible output (16k context, tight cap).
    # (2) Visible content empty, reasoning_content used as fallback (32k context).
    # (3) Multiple drafts produced inside the output during the model's
    #     reasoning phase. Extract the LAST one.
    output = raw_output
    postprocess_notes: list[str] = []

    # Detect fallback condition: extract_content returns the same string for
    # both `output` and `reasoning` when content was empty and reasoning was
    # used as the fallback.
    fallback_used = raw_output == reasoning and len(reasoning) > 0
    if fallback_used:
        postprocess_notes.append(
            "visible content was empty; using reasoning_content as fallback"
        )

    if fallback_used or detect_planning_prose(output):
        last_draft = extract_last_draft(output, anchor_pattern=r"^#")
        if last_draft and last_draft != output:
            postprocess_notes.append(
                f"extracted last draft from {len(output)}-char reasoning text "
                f"(now {len(last_draft)} chars)"
            )
            output = last_draft
        elif detect_planning_prose(output):
            stripped = extract_after_planning(output, anchor_pattern=r"^#")
            if stripped != output:
                postprocess_notes.append("stripped planning preamble before first H1")
                output = stripped

    for note in postprocess_notes:
        print(f"Post-process: {note}", file=sys.stderr)

    output_words = len(output.split())
    out_md.write_text(
        f"# Summary Output ({utc_iso()})\n\n"
        f"Source: `{doc_path}`\n"
        f"Input chars: {input_chars}\n"
        f"Input tokens (est.): {estimated_input_tokens}\n"
        f"Shape: {args.shape}\n"
        f"Target words: {args.target_words}\n"
        f"Actual words: {output_words}\n"
        f"Model: `{args.model}`\n"
        f"Wall-clock: {elapsed:.1f}s\n"
        f"Total tokens: {usage.get('total_tokens', 'n/a')}\n\n"
        f"---\n\n"
        f"{output}\n",
        encoding="utf-8",
    )
    out_json.write_text(
        json.dumps({
            "task": "summarize-doc",
            "model": args.model,
            "endpoint": args.lm_studio_url,
            "wall_clock_s": round(elapsed, 2),
            "doc_path": str(doc_path),
            "input_chars": input_chars,
            "input_tokens_estimated": estimated_input_tokens,
            "shape": args.shape,
            "target_words": args.target_words,
            "actual_words": output_words,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "reasoning_chars": len(reasoning),
            "output_chars": len(output),
            "lm_studio_context": args.lm_studio_context,
            "postprocess_notes": postprocess_notes,
            "fallback_used": fallback_used,
            "output_md_path": str(out_md),
            "timestamp_utc": utc_iso(),
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Done. wall_clock={elapsed:.1f}s tokens={usage.get('total_tokens', 'n/a')} "
        f"input_chars={input_chars} output_words={output_words} "
        f"reasoning_chars={len(reasoning)} output_chars={len(output)}",
        file=sys.stderr,
    )
    print(f"Markdown: {out_md}", file=sys.stderr)
    print(f"JSON:     {out_json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
