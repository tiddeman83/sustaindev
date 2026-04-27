#!/usr/bin/env python3
"""
draft-catalog.py — overnight/short probe for case-study-05.

Asks a local LM Studio model to draft a service catalog from a project's
service interface files. The output should match `core/templates/service-catalog.md`
in the SustainDev repo.

This probes the routing-matrix row "codemap drafts from file lists" — the
model receives a small bundle of source files (interface definitions, a few
hundred lines total) and produces a structured markdown catalog. Same task
class as codemap drafting; different artifact shape.

Usage from a project root:

    python3 path/to/draft-catalog.py [options]

Default behavior:
    Recursively finds files matching `--interface-glob` (default: `*Service*.cs`)
    under `--services-root` (default: `src/`), filters to public interface
    declarations, and sends them as one bundle. Outputs the drafted catalog
    to .sustaindev/measurement/.

Common options:
    --services-root PATH   Where to look for interfaces (default: src/).
    --interface-glob PAT   Glob for interface files (default: *Service*.cs).
    --max-files N          Cap the file count (default: 25; service catalogs
                           are usually small).
    --lm-studio-context N  Loaded context length for pre-flight check (16384).
    --dry-run              Print the prompt that would be sent and exit.
    --model ID             Override loaded model id.
    --temperature FLOAT    Default 0.2.
    --max-tokens N         Default 4000.

Output:
    <project-root>/.sustaindev/measurement/catalog-<timestamp>.md
    <project-root>/.sustaindev/measurement/catalog-<timestamp>.json

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
from typing import Optional


DEFAULT_LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3.5-9b"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TIMEOUT = 600

PROJECT_LAYER_FILES = [
    "PROJECT_CONTEXT.md",
    "CODEMAP.md",
]

SYSTEM_PROMPT = """\
/no_think

You are a code-structure summarizer. Your job is to read a small bundle of
service interface files (C#, TypeScript, Python — whatever the project uses)
and produce a markdown service catalog.

Output rules — follow exactly:

1. Output a markdown document starting with the H1 header
   `# Service Catalog: <project-name>`. Replace `<project-name>` with the
   name from the project context if available; otherwise leave the placeholder.
2. Include a one-paragraph "## Layer summary" section describing the
   service-layer architecture as you understand it from the inputs.
3. For each interface in the input bundle, produce a `### `<IInterfaceName>`` section with:
   - File: relative path
   - Implementation: relative path or "(not in this bundle)"
   - DI scope: singleton / scoped / transient / unknown
   - Responsibility: ONE sentence under 25 words
   - Public methods: list with full signatures, one per line, in a code block
   - Depends on: comma-separated list, or "none"
   - Used by: comma-separated list, or "(not visible from this bundle)"
   - Notes: 0-2 sentences if relevant; otherwise omit the line
4. End with a "## Last verified" line: `Last verified: <today's date> by local-model draft.`
5. Do NOT produce content outside the catalog structure. No preamble, no
   postamble, no <think> tags, no explanations of your reasoning.
6. Do NOT invent methods. If you cannot read a method signature from the
   input, mark it `<unreadable — see source>`.
7. Do NOT invent implementation paths. Mark them `(not in this bundle)` if
   you only see the interface file.

The output is a draft. A human will review it before it becomes the project's
canonical SERVICE_CATALOG.md.
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


def find_interface_files(services_root: Path, glob: str, max_files: int,
                         interfaces_only: bool = True) -> list[Path]:
    """Find candidate files. By default returns interfaces only.

    The filter:
      - excludes generated/build directories.
      - excludes test files (*Tests.cs, *.Tests.cs, *_test.py, etc.).
      - excludes obvious non-production patterns (Stub, Mock, Fake, Null).
      - if interfaces_only=True (default), restricts to filenames starting
        with 'I' (C# convention) or files explicitly named *Interface.* in
        TypeScript/Python/etc.
    """
    matches: list[Path] = []
    excluded_parts = {"bin", "obj", "node_modules", "dist", "build", ".git"}
    excluded_substrings = ("Stub.", "Mock.", "Fake.", "Null", "Tests.", "_test.", ".test.", "Test.")
    for p in sorted(services_root.rglob(glob)):
        if any(part in excluded_parts for part in p.parts):
            continue
        if not p.is_file():
            continue
        name = p.name
        if any(s in name for s in excluded_substrings):
            continue
        if interfaces_only:
            # C# convention: interface files start with 'I' followed by uppercase.
            # Some non-C# projects use *Interface.* — accept both.
            stem = p.stem
            looks_like_interface = (
                (len(stem) >= 2 and stem[0] == "I" and stem[1].isupper())
                or "Interface" in stem
            )
            if not looks_like_interface:
                continue
        matches.append(p)
        if len(matches) >= max_files:
            break
    return matches


def read_optional(path: Path, label: str) -> Optional[str]:
    if not path.is_file():
        warn(f"Skipping missing {label}: {path}")
        return None
    return path.read_text(encoding="utf-8")


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
    parser.add_argument("--project-root", default=os.getcwd())
    parser.add_argument("--services-root", default="src/")
    parser.add_argument("--interface-glob", default="*Service*.cs")
    parser.add_argument("--max-files", type=int, default=25)
    parser.add_argument("--include-implementations", action="store_true",
                        help="Also include implementation files (not just interfaces). "
                             "Off by default — implementations are heavy and the catalog "
                             "needs only signatures.")
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
    if args.help:
        print(__doc__)
        sys.exit(0)
    return args


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    services_root = (project_root / args.services_root).resolve()
    if not services_root.is_dir():
        fail(f"--services-root not found: {services_root}")

    files = find_interface_files(
        services_root, args.interface_glob, args.max_files,
        interfaces_only=not args.include_implementations,
    )
    if not files:
        fail(f"No files matched {args.interface_glob} under {services_root}.")
    print(f"Found {len(files)} files matching {args.interface_glob}.", file=sys.stderr)

    # Gather optional context.
    context_blocks: list[str] = []
    for filename in PROJECT_LAYER_FILES:
        text = read_optional(project_root / filename, filename)
        if text is not None:
            context_blocks.append(f"### {filename}\n\n{text.strip()}")

    # Read all interface files into the prompt.
    file_blocks: list[str] = []
    total_chars = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception as e:
            warn(f"Could not read {f}: {e}")
            continue
        rel = f.relative_to(project_root)
        block = f"### `{rel}`\n\n```\n{content}\n```\n"
        file_blocks.append(block)
        total_chars += len(content)

    user_message_parts = [
        "Project context (read-only, abbreviated):",
        "",
    ]
    if context_blocks:
        user_message_parts.extend(context_blocks)
    else:
        user_message_parts.append("(no project layer files found)")
    user_message_parts.extend([
        "",
        f"Interface files to summarize ({len(file_blocks)} total, ~{total_chars} chars source):",
        "",
        *file_blocks,
        "",
        "Produce the markdown service catalog as specified by the system prompt.",
    ])
    user_message = "\n".join(user_message_parts)

    # Pre-flight token check.
    prompt_chars = len(SYSTEM_PROMPT) + len(user_message)
    estimated_prompt_tokens = int(prompt_chars / 3.8)
    estimated_total = estimated_prompt_tokens + args.max_tokens + 512
    if estimated_total >= args.lm_studio_context and not args.force:
        fail(
            f"Pre-flight: estimated context need ({estimated_total} tokens) exceeds "
            f"--lm-studio-context ({args.lm_studio_context}).\n"
            f"  Prompt: ~{estimated_prompt_tokens} tokens ({prompt_chars} chars)\n"
            f"  Output budget: {args.max_tokens}\n"
            f"Options: raise LM Studio context, lower --max-files, lower --max-tokens, or --force.",
            code=6,
        )

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN")
        print("=" * 60)
        print(f"Files: {len(file_blocks)}")
        print(f"Prompt chars: {prompt_chars}")
        print(f"Estimated prompt tokens: {estimated_prompt_tokens}")
        print(f"User message preview (first 1500 chars):")
        print(user_message[:1500])
        return 0

    measurement_dir = project_root / ".sustaindev" / "measurement"
    measurement_dir.mkdir(parents=True, exist_ok=True)
    stamp = utc_filestamp()
    out_md = measurement_dir / f"catalog-{stamp}.md"
    out_json = measurement_dir / f"catalog-{stamp}.json"

    print(f"Calling LM Studio ({args.model}) to draft catalog from {len(file_blocks)} files... "
          f"(prompt ~{estimated_prompt_tokens} tokens)", file=sys.stderr)
    t0 = time.perf_counter()
    response = call_lm_studio(args.lm_studio_url, args.model, SYSTEM_PROMPT, user_message,
                              args.temperature, args.max_tokens, args.timeout)
    elapsed = time.perf_counter() - t0
    output, reasoning = extract_content(response)
    usage = response.get("usage", {}) or {}

    out_md.write_text(
        f"# Catalog Draft Output ({utc_iso()})\n\n"
        f"Project root: `{project_root}`\n"
        f"Services root: `{services_root}`\n"
        f"Interface glob: `{args.interface_glob}`\n"
        f"Files included: {len(file_blocks)}\n"
        f"Source chars: {total_chars}\n"
        f"Model: `{args.model}`\n"
        f"Wall-clock: {elapsed:.1f}s\n"
        f"Total tokens: {usage.get('total_tokens', 'n/a')}\n\n"
        f"---\n\n"
        f"{output}\n",
        encoding="utf-8",
    )
    out_json.write_text(
        json.dumps({
            "task": "draft-catalog",
            "model": args.model,
            "endpoint": args.lm_studio_url,
            "wall_clock_s": round(elapsed, 2),
            "files_count": len(file_blocks),
            "source_chars": total_chars,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "reasoning_chars": len(reasoning),
            "output_chars": len(output),
            "lm_studio_context": args.lm_studio_context,
            "output_md_path": str(out_md),
            "timestamp_utc": utc_iso(),
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Done. wall_clock={elapsed:.1f}s tokens={usage.get('total_tokens', 'n/a')} "
        f"files={len(file_blocks)} source_chars={total_chars} "
        f"reasoning_chars={len(reasoning)} output_chars={len(output)}",
        file=sys.stderr,
    )
    print(f"Markdown: {out_md}", file=sys.stderr)
    print(f"JSON:     {out_json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
