#!/usr/bin/env python3
"""
prepare-task.py — turn a captured idea stub into a structured task brief
using a local model (LM Studio) plus the project's SustainDev layer files.

This is the prework step of the SustainDev `idea-to-prepared-task` skill.
It reads a captured stub, the project layer files (PROJECT_CONTEXT.md,
CODEMAP.md, AI_POLICY.md, MAINTAINABILITY_NOTES.md, VERIFY.md) when
present, and asks the local model to produce a fully-structured brief
matching the scheduled-task template.

Usage:
    python3 scripts/schedule/prepare-task.py <captured-id> [options]

Or pass the full path of a captured stub:
    python3 scripts/schedule/prepare-task.py <queue-root>/captured/<id>.md

Options:
    --project-root <path>      Project root (default: current directory).
    --queue-root <path>        Queue root (default: auto-detect from
                               core/scheduling/queue or .sustaindev/queue).
    --output-status <name>     captured / prework-ready / scheduled
                               (default: prework-ready).
    --keep-captured            Keep the captured stub in queue/captured/.
                               Default behavior: move to output queue.
    --dry-run                  Print the constructed prompt and exit.
    --lm-studio-url <url>      Endpoint (default $LM_STUDIO_URL or
                               http://127.0.0.1:1234/v1/chat/completions).
    --model <id>               Model id (default $LM_STUDIO_MODEL or
                               qwen/qwen3.5-9b).
    --temperature <float>      Default 0.3.
    --max-tokens <int>         Default 4000.
    --timeout <seconds>        Default 600.
    --measurement-dir <path>   Where to write the measurement JSON.
                               Default: <queue-root parent>/measurement/.
    -h / --help                Show this message.

Local-only by design. If LM Studio is unreachable, exits with a clear
error message pointing at adapters/lm-studio/usage.md.

Zero external dependencies (urllib + stdlib only).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# --- Constants --------------------------------------------------------------

DEFAULT_LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3.5-9b"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TIMEOUT = 600

PROJECT_LAYER_FILES = [
    "PROJECT_CONTEXT.md",
    "CODEMAP.md",
    "AI_POLICY.md",
    "MAINTAINABILITY_NOTES.md",
    "VERIFY.md",
    # DECISIONS.md and RISKS.md are optional and tend to be longer; skip by
    # default to keep prompt size under control. Users can opt in by editing
    # the constant if their model has the context window for it.
]

VALID_STATUSES = ("captured", "prework-ready", "scheduled", "completed")

SCHEDULED_TASK_TEMPLATE = """\
# Scheduled Task: <id>

---
id: <id>
title: <task-title>
captured_at: <captured-iso8601>
prepared_at: <prepared-iso8601>
status: prework-ready
priority: <low|medium|high>
execution_tier_suggested: <local|cloud|human>
cloud_tool_suggested: <claude-code|codex|gemini|empty>
time_window_suggested: <for-example-22:00-06:00>
---

## Captured Idea

<one to three sentences preserving the original captured wording>

## Scope

<what this task changes and what it does NOT change; narrow boundary>

## File Targets

- `<path-to-likely-file>` because <why>.
- `<path-to-test-file>` because <what verification it supports>.
- `<path-to-config-or-doc>` because <why it may change>.

## Verify Commands

- `<command-from-VERIFY.md>` confirms <what>.
- `<optional-focused-command>` confirms <specific risk>.

## Maintainability Constraints

<paragraph naming the dimensions most at risk: architecture fit, coupling,
naming, testability, error handling, change cost. State what to preserve.>

## Success Criteria

- <concrete pass/fail condition>
- <behavior that must remain unchanged>
- <required test/lint/build passes>

## Notes for Execution

<anything the executor needs but should not have to rediscover>

## Retrospective

<fill after completion>
"""

SYSTEM_PROMPT = """\
/no_think

You are a prework assistant for an AI-assisted development repository. Your
output is a structured task brief that a stronger model or human will review
before any code change.

Produce ONLY the requested markdown document. No preamble, no postamble,
no conversational text, no <think> tags. Do not invent metrics or numbers
that are not provided in the input.

The user message will provide:
- A captured idea (the rough request as the user wrote it).
- The project's PROJECT_CONTEXT.md, CODEMAP.md, AI_POLICY.md,
  MAINTAINABILITY_NOTES.md, and VERIFY.md (when available).
- The exact target structure for your output.

Your job is to produce a complete brief in the target structure, drawing
file paths from the codemap, verify commands from VERIFY.md, and
maintainability constraints from MAINTAINABILITY_NOTES.md. Do not invent
files that do not appear in the codemap. Do not invent verify commands
that do not appear in VERIFY.md. If the codemap is silent on the right
file location, write `<unknown — codemap silent>` rather than guessing.

The output MUST start with the exact string `# Scheduled Task: ` and
include a YAML front matter block delimited by `---` on its own line.
"""

# --- Helpers ----------------------------------------------------------------


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"WARNING: {msg}", file=sys.stderr)


def utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def detect_queue_root(project_root: Path) -> Path:
    """Find the queue root by trying the two conventional locations."""
    candidates = [
        project_root / ".sustaindev" / "queue",
        project_root / "core" / "scheduling" / "queue",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    fail(
        f"No queue root found under {project_root}. "
        f"Tried: {[str(c) for c in candidates]}. "
        f"Create one with: mkdir -p .sustaindev/queue/{{captured,prework-ready,scheduled,completed}}"
    )
    return Path()  # unreachable


def find_captured_stub(queue_root: Path, captured_id: str) -> Path:
    """Resolve a captured-id (or full path) to an actual stub file."""
    candidate = Path(captured_id)
    if candidate.is_file():
        return candidate
    captured_dir = queue_root / "captured"
    direct = captured_dir / f"{captured_id}.md"
    if direct.is_file():
        return direct
    fail(
        f"No captured stub found for id '{captured_id}'. "
        f"Looked in: {captured_dir}/{captured_id}.md and as direct path."
    )
    return Path()  # unreachable


def read_optional(path: Path, label: str) -> Optional[str]:
    if not path.is_file():
        warn(f"Skipping missing {label}: {path}")
        return None
    return path.read_text(encoding="utf-8")


def parse_captured_yaml(stub_text: str) -> dict:
    """Extract YAML front matter from a captured stub. Flat key:value only."""
    match = re.search(r"^---\s*\n(.*?)\n---\s*\n", stub_text, re.DOTALL | re.MULTILINE)
    if not match:
        return {}
    fields: dict = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip().strip('"')
    return fields


def call_lm_studio(
    url: str,
    model: str,
    system_prompt: str,
    user_message: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # Server reached, but rejected the request. Read the body for the real reason.
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = "(no response body)"
        fail(
            f"LM Studio rejected the request at {url} with HTTP {e.code} {e.reason}.\n"
            f"  Server said: {err_body}\n"
            f"  Sent model id: '{model}'\n"
            f"  Sent prompt: {sum(len(m['content']) for m in payload['messages'])} chars total\n"
            f"  Sent max_tokens: {max_tokens}\n"
            f"  Common causes:\n"
            f"    - Model id doesn't match the loaded model. Run\n"
            f"      curl http://127.0.0.1:1234/v1/models | python3 -m json.tool\n"
            f"      to list loaded ids and pass --model with the exact value.\n"
            f"    - Prompt exceeds the model's loaded context length. Lower context\n"
            f"      consumption: shorter project layer files, or set the LM Studio\n"
            f"      context length larger.\n"
            f"    - max_tokens larger than what the loaded model permits per\n"
            f"      response. Try --max-tokens 2000 to see if it goes through.\n"
            f"    - LM Studio version mismatch with the chat-completions schema.",
            code=5,
        )
    except urllib.error.URLError as e:
        fail(
            f"Could not reach LM Studio at {url}: {e}\n"
            f"  - Is LM Studio running? Open Developer tab and enable Local Server.\n"
            f"  - Is the model loaded? Check with curl http://127.0.0.1:1234/v1/models\n"
            f"  - See adapters/lm-studio/usage.md for full setup.",
            code=2,
        )
    return {}  # unreachable


def extract_content(response: dict) -> tuple[str, str]:
    """Extract content + reasoning from an OpenAI-compatible response.

    Returns (clean_content, raw_reasoning). clean_content has <think>
    blocks stripped. If content is empty but reasoning_content is present,
    returns reasoning as the content (best-effort recovery).
    """
    try:
        message = response["choices"][0]["message"]
    except (KeyError, IndexError) as e:
        fail(f"Unexpected response shape from LM Studio: {e}")
    raw_content = (message.get("content") or "").strip()
    reasoning = (message.get("reasoning_content") or "").strip()
    stripped = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
    if stripped:
        return stripped, reasoning
    if reasoning:
        warn("message.content empty; falling back to reasoning_content (review carefully).")
        return reasoning, reasoning
    fail(
        "Model returned no usable content. Common fixes:\n"
        "  - Ensure /no_think is in the system prompt (it is by default).\n"
        "  - Raise --max-tokens.\n"
        "  - Check the model isn't a vision-only or embedding-only build.",
        code=4,
    )
    return "", ""  # unreachable


def validate_brief(brief: str) -> list[str]:
    """Return a list of validation issues. Empty list = ok."""
    issues: list[str] = []
    if not brief.startswith("# Scheduled Task:"):
        issues.append("Brief does not start with '# Scheduled Task: '.")
    if not re.search(r"^---\s*$", brief, flags=re.MULTILINE):
        issues.append("No YAML front matter delimiters found.")
    required_sections = [
        "## Captured Idea",
        "## Scope",
        "## File Targets",
        "## Verify Commands",
        "## Maintainability Constraints",
        "## Success Criteria",
        "## Retrospective",
    ]
    for section in required_sections:
        if section not in brief:
            issues.append(f"Missing required section: {section}")
    return issues


# --- Main -------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("captured_id", nargs="?")
    parser.add_argument("--project-root", default=os.getcwd())
    parser.add_argument("--queue-root", default=None)
    parser.add_argument("--output-status", default="prework-ready", choices=VALID_STATUSES)
    parser.add_argument("--keep-captured", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--lm-studio-url", default=os.environ.get("LM_STUDIO_URL", DEFAULT_LM_STUDIO_URL))
    parser.add_argument("--model", default=os.environ.get("LM_STUDIO_MODEL", DEFAULT_MODEL))
    parser.add_argument("--temperature", type=float, default=float(os.environ.get("LM_STUDIO_TEMPERATURE", DEFAULT_TEMPERATURE)))
    parser.add_argument("--max-tokens", type=int, default=int(os.environ.get("LM_STUDIO_MAX_TOKENS", DEFAULT_MAX_TOKENS)))
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("LM_STUDIO_TIMEOUT", DEFAULT_TIMEOUT)))
    parser.add_argument("--measurement-dir", default=None)
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()
    if args.help or args.captured_id is None:
        print(__doc__)
        sys.exit(0)
    return args


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    queue_root = Path(args.queue_root).resolve() if args.queue_root else detect_queue_root(project_root)

    captured_path = find_captured_stub(queue_root, args.captured_id)
    captured_text = captured_path.read_text(encoding="utf-8")
    captured_fields = parse_captured_yaml(captured_text)
    captured_id = captured_fields.get("id") or captured_path.stem

    output_dir = queue_root / args.output_status
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{captured_id}.md"
    if output_path.exists() and not args.dry_run:
        fail(f"Output already exists: {output_path}. Move or delete it first.")

    # Gather project context.
    context_blocks: list[str] = []
    for filename in PROJECT_LAYER_FILES:
        text = read_optional(project_root / filename, filename)
        if text is not None:
            context_blocks.append(f"### {filename}\n\n{text.strip()}")

    # Construct the user message.
    user_message_parts = [
        "Captured idea (raw stub the user wrote):",
        "",
        captured_text.strip(),
        "",
        "Project layer context (read-only):",
        "",
    ]
    if context_blocks:
        user_message_parts.extend(context_blocks)
    else:
        user_message_parts.append("(no project layer files found — proceed with what is in the captured idea)")
    user_message_parts.extend(
        [
            "",
            "Produce a complete scheduled-task brief in the following structure.",
            "Fill every section. Use file paths from the codemap. Use verify",
            "commands from VERIFY.md. Use the maintainability dimensions from",
            "MAINTAINABILITY_NOTES.md. Set status: prework-ready in the front",
            "matter and copy captured_at from the input above; set prepared_at",
            f"to {utc_iso()}.",
            "",
            "Target structure (replace placeholder bracketed text, keep the headings):",
            "",
            SCHEDULED_TASK_TEMPLATE,
        ]
    )
    user_message = "\n".join(user_message_parts)

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN: prompt that would be sent to LM Studio")
        print("=" * 60)
        print("--- system prompt ---")
        print(SYSTEM_PROMPT)
        print("--- user message ---")
        print(user_message)
        print("=" * 60)
        print(f"Endpoint: {args.lm_studio_url}")
        print(f"Model:    {args.model}")
        print(f"Output would land at: {output_path}")
        return 0

    print(f"Calling LM Studio ({args.model}) for captured id '{captured_id}'...", file=sys.stderr)
    t0 = time.perf_counter()
    response = call_lm_studio(
        args.lm_studio_url,
        args.model,
        SYSTEM_PROMPT,
        user_message,
        args.temperature,
        args.max_tokens,
        args.timeout,
    )
    elapsed = time.perf_counter() - t0

    brief, reasoning = extract_content(response)
    issues = validate_brief(brief)
    if issues:
        warn(f"Brief failed validation ({len(issues)} issues). Writing anyway for review:")
        for issue in issues:
            warn(f"  - {issue}")

    # Write the prepared brief.
    output_path.write_text(brief.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote prepared brief: {output_path}", file=sys.stderr)

    # Move or delete the captured stub.
    if not args.keep_captured:
        captured_path.unlink()
        print(f"Removed captured stub: {captured_path}", file=sys.stderr)

    # Measurement record.
    usage = response.get("usage", {}) or {}
    measurement_dir = (
        Path(args.measurement_dir).resolve()
        if args.measurement_dir
        else queue_root.parent / "measurement"
    )
    measurement_dir.mkdir(parents=True, exist_ok=True)
    measurement_path = measurement_dir / f"prepare-{captured_id}.json"
    measurement_path.write_text(
        json.dumps(
            {
                "task": "prepare-task",
                "captured_id": captured_id,
                "model": args.model,
                "endpoint": args.lm_studio_url,
                "wall_clock_s": round(elapsed, 2),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "reasoning_chars": len(reasoning),
                "brief_chars": len(brief),
                "validation_issues": issues,
                "output_path": str(output_path),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"Done. wall_clock={elapsed:.1f}s tokens={usage.get('total_tokens', 'n/a')} "
        f"reasoning_chars={len(reasoning)} brief_chars={len(brief)} "
        f"validation_issues={len(issues)}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
