#!/usr/bin/env python3
"""
extract-risks.py — risk extraction probe for case-study-07.

Reads a prose document containing risks/issues/concerns and asks a local
model to produce a structured risk catalog with severity tags.

Probes the routing-matrix row "risk extraction from existing prose" — the
sixth strong-fit row to be tested. Specifically:

  Input:   a markdown document mixing prose discussion and embedded
           risks/issues/known-issues.
  Output:  a structured table with columns: ID, Title, Severity, Description,
           Mitigation. One row per risk, with severity tagged from the
           prose's signal words (e.g., "Hoog ernst" -> high).

Uses scripts/lib/postprocess.py (v0.1.6+) from the start — no local
defensive code; the shared module handles all packaging quirks.

Usage:

    python3 path/to/extract-risks.py <doc-path> [options]

Common options:
    --max-risks N           Cap how many risks to extract (default 30).
    --severity-scale SCALE  Comma-separated severity values, in order from
                            highest to lowest. Default: "high,medium,low,info".
                            Use Dutch alternatives like "hoog,middel,laag,info"
                            for non-English projects.
    --lm-studio-context N   Default 16384.
    --max-tokens N          Default 3000 (smaller than summarize because output
                            is bounded structured rows, not prose).
    --dry-run               Print the prompt and exit.
    --model ID              Override loaded model id.
    --temperature FLOAT     Default 0.2.
    --force                 Skip the pre-flight context check.

Output:
    <project-root>/.sustaindev/measurement/risks-<timestamp>.md
    <project-root>/.sustaindev/measurement/risks-<timestamp>.json

Local-only by design. Zero external dependencies (uses scripts/lib/postprocess
which is also stdlib-only).
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
DEFAULT_MAX_TOKENS = 3000
DEFAULT_TIMEOUT = 600


SYSTEM_PROMPT_TEMPLATE = """\
/no_think

You are a risk-extraction assistant. You read documents that mix prose
discussion with embedded mentions of risks, issues, concerns, or known
problems, and you produce a structured risk catalog.

Output rules — follow exactly:

1. Output a markdown table with EXACTLY these columns, in this order:
   ID, Title, Severity, Description, Mitigation.
2. Severity values must be one of: {severity_values}. Pick the closest match
   for each risk based on signal words in the prose ("kritiek", "high",
   "hoog ernst", "blocker", etc.).
3. ID format: R-NN (zero-padded, e.g. R-01, R-02). Number in source order.
4. Title: short label, under 60 chars, in the source's language.
5. Description: one or two sentences in the source's language, summarizing
   the risk concretely.
6. Mitigation: one short sentence describing what the source says about
   reducing or addressing the risk. If the source doesn't mention a
   mitigation, write "(geen mitigatie genoemd)" / "(no mitigation mentioned)"
   in the source's language.
7. Cap at {max_risks} rows. If the source has more than that, list the
   highest-severity ones first and stop.
8. Preserve the source's primary language (if Dutch, output in Dutch).

After the table, output exactly one summary line in this format:
  "Counts: high=N, medium=N, low=N, info=N (total=N)"
(Substitute the actual severity scale values used.)

Do NOT produce any other content. No preamble, no postamble, no <think>
tags, no explanation of your reasoning. Just the table and the counts line.
"""


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
            f"LM Studio rejected with HTTP {e.code} {e.reason}.\n"
            f"  Server said: {err_body}",
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
    parser.add_argument("--max-risks", type=int, default=30)
    parser.add_argument("--severity-scale", default="high,medium,low,info")
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
    doc_path = Path(args.doc_path)
    if not doc_path.is_absolute():
        doc_path = project_root / doc_path
    doc_path = doc_path.resolve()
    if not doc_path.is_file():
        fail(f"Document not found: {doc_path}")

    severities = [s.strip() for s in args.severity_scale.split(",") if s.strip()]
    if not severities:
        fail("--severity-scale must list at least one value.")

    doc_text = doc_path.read_text(encoding="utf-8")
    input_chars = len(doc_text)
    estimated_input_tokens = int(input_chars / 3.8)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        severity_values=", ".join(severities),
        max_risks=args.max_risks,
    )
    user_message = (
        f"Source document: `{doc_path.relative_to(project_root) if doc_path.is_relative_to(project_root) else doc_path}`\n\n"
        f"---\n\n"
        f"{doc_text}\n"
    )

    prompt_chars = len(system_prompt) + len(user_message)
    estimated_prompt_tokens = int(prompt_chars / 3.8)
    estimated_total = estimated_prompt_tokens + args.max_tokens + 512
    if estimated_total >= args.lm_studio_context and not args.force:
        fail(
            f"Pre-flight: estimated context need ({estimated_total} tokens) exceeds "
            f"--lm-studio-context ({args.lm_studio_context}).\n"
            f"  Document: ~{estimated_input_tokens} tokens\n"
            f"Options: raise context, lower --max-tokens, or --force.",
            code=6,
        )

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN")
        print("=" * 60)
        print(f"Document: {doc_path}")
        print(f"Input chars: {input_chars} (~{estimated_input_tokens} tokens)")
        print(f"Severity scale: {severities}")
        print(f"Max risks: {args.max_risks}")
        print(f"--- system prompt ---")
        print(system_prompt[:600])
        print(f"--- user message preview ---")
        print(user_message[:600])
        return 0

    measurement_dir = project_root / ".sustaindev" / "measurement"
    measurement_dir.mkdir(parents=True, exist_ok=True)
    stamp = utc_filestamp()
    out_md = measurement_dir / f"risks-{stamp}.md"
    out_json = measurement_dir / f"risks-{stamp}.json"

    print(f"Calling LM Studio ({args.model}) to extract risks from {doc_path.name}... "
          f"(prompt ~{estimated_prompt_tokens} tokens)", file=sys.stderr)
    t0 = time.perf_counter()
    response = call_lm_studio(args.lm_studio_url, args.model, system_prompt, user_message,
                              args.temperature, args.max_tokens, args.timeout)
    elapsed = time.perf_counter() - t0
    raw_output, reasoning = extract_content(response)
    usage = response.get("usage", {}) or {}

    # Post-process pipeline (using v0.1.6 shared module).
    output = raw_output
    postprocess_notes: list[str] = []
    fallback_used = raw_output == reasoning and len(reasoning) > 0
    if fallback_used:
        postprocess_notes.append("visible content empty; using reasoning_content as fallback")
    if fallback_used or detect_planning_prose(output):
        last_draft = extract_last_draft(output, anchor_pattern=r"^\s*\|")
        # For risk extraction, the "draft" is a markdown table starting with `|`.
        if last_draft and last_draft != output:
            postprocess_notes.append(
                f"extracted last draft from {len(output)}-char text "
                f"(now {len(last_draft)} chars)"
            )
            output = last_draft
        elif detect_planning_prose(output):
            stripped = extract_after_planning(output, anchor_pattern=r"^\s*\|")
            if stripped != output:
                postprocess_notes.append("stripped planning preamble before first table line")
                output = stripped
    for note in postprocess_notes:
        print(f"Post-process: {note}", file=sys.stderr)

    out_md.write_text(
        f"# Risks Output ({utc_iso()})\n\n"
        f"Source: `{doc_path}`\n"
        f"Input chars: {input_chars}\n"
        f"Severity scale: {severities}\n"
        f"Model: `{args.model}`\n"
        f"Wall-clock: {elapsed:.1f}s\n"
        f"Total tokens: {usage.get('total_tokens', 'n/a')}\n\n"
        f"---\n\n"
        f"{output}\n",
        encoding="utf-8",
    )
    out_json.write_text(
        json.dumps({
            "task": "extract-risks",
            "model": args.model,
            "endpoint": args.lm_studio_url,
            "wall_clock_s": round(elapsed, 2),
            "doc_path": str(doc_path),
            "input_chars": input_chars,
            "input_tokens_estimated": estimated_input_tokens,
            "severity_scale": severities,
            "max_risks": args.max_risks,
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
        f"input_chars={input_chars} reasoning_chars={len(reasoning)} "
        f"output_chars={len(output)}",
        file=sys.stderr,
    )
    print(f"Markdown: {out_md}", file=sys.stderr)
    print(f"JSON:     {out_json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
