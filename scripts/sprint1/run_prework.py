#!/usr/bin/env python3
"""
Sprint 1 first test: call LM Studio to draft a Sprint 1 markdown file
and capture measurement data for case-study-01.

Run from your Mac (not from the Claude sandbox):
    python3 scripts/sprint1/run_prework.py

Prerequisites:
    - LM Studio installed
    - Qwen 3.5 9B (MLX 4-bit recommended) loaded
    - Local server enabled, default port 1234
    - Python 3.9+

Outputs:
    scripts/sprint1/output/draft.md            <- model's draft
    scripts/sprint1/output/measurement.json    <- timing + token counts
    scripts/sprint1/output/run.log             <- console log

The script intentionally has zero external dependencies (urllib only)
so you don't need to set up a venv to test the pipeline.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# --- Config -----------------------------------------------------------------

LM_STUDIO_URL = os.environ.get("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
LM_STUDIO_MODEL = os.environ.get("LM_STUDIO_MODEL", "qwen/qwen3.5-9b")  # matches LM Studio's namespaced id
TEMPERATURE = float(os.environ.get("LM_STUDIO_TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.environ.get("LM_STUDIO_MAX_TOKENS", "4000"))  # generous; Qwen 3.x may emit reasoning tokens
REQUEST_TIMEOUT = int(os.environ.get("LM_STUDIO_TIMEOUT", "600"))  # seconds

HERE = Path(__file__).resolve().parent
SYSTEM_PROMPT_FILE = HERE / "system_prompt.md"
USER_BRIEF_FILE = HERE / "user_brief.md"
OUTPUT_DIR = HERE / "output"
DRAFT_OUT = OUTPUT_DIR / "draft.md"
MEASUREMENT_OUT = OUTPUT_DIR / "measurement.json"
LOG_OUT = OUTPUT_DIR / "run.log"
RAW_RESPONSE_OUT = OUTPUT_DIR / "raw_response.json"


# --- Helpers ----------------------------------------------------------------


def log(msg: str, log_lines: list) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
    print(line)
    log_lines.append(line)


def read_file(path: Path) -> str:
    if not path.is_file():
        sys.exit(f"ERROR: required file missing: {path}")
    return path.read_text(encoding="utf-8").strip()


def list_models() -> list:
    """Best-effort: ask LM Studio which models are loaded."""
    url = LM_STUDIO_URL.replace("/chat/completions", "/models")
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m.get("id", "") for m in data.get("data", [])]
    except Exception:
        return []


def call_lm_studio(system_prompt: str, user_brief: str) -> dict:
    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_brief},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LM_STUDIO_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


# --- Main -------------------------------------------------------------------


def main() -> int:
    log_lines: list = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log(f"Endpoint: {LM_STUDIO_URL}", log_lines)
    log(f"Model id (configured): {LM_STUDIO_MODEL}", log_lines)
    loaded = list_models()
    if loaded:
        log(f"Loaded models reported by LM Studio: {loaded}", log_lines)
        if LM_STUDIO_MODEL not in loaded:
            log(
                f"WARNING: configured model '{LM_STUDIO_MODEL}' not in loaded list. "
                f"LM Studio is usually permissive about model id, but if the call fails, "
                f"set LM_STUDIO_MODEL env var to one of: {loaded}",
                log_lines,
            )
    else:
        log("Could not list models (server may not expose /v1/models). Proceeding anyway.", log_lines)

    system_prompt = read_file(SYSTEM_PROMPT_FILE)
    user_brief = read_file(USER_BRIEF_FILE)
    log(f"System prompt: {len(system_prompt)} chars", log_lines)
    log(f"User brief:    {len(user_brief)} chars", log_lines)

    log("Calling LM Studio (this may take 30s-3min depending on hardware)...", log_lines)
    t0 = time.perf_counter()
    try:
        response = call_lm_studio(system_prompt, user_brief)
    except urllib.error.URLError as e:
        log(f"ERROR: could not reach LM Studio at {LM_STUDIO_URL}: {e}", log_lines)
        LOG_OUT.write_text("\n".join(log_lines), encoding="utf-8")
        return 2
    elapsed_s = time.perf_counter() - t0

    # Always dump the raw response for debugging (so we never fly blind).
    RAW_RESPONSE_OUT.write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")
    log(f"Wrote raw response -> {RAW_RESPONSE_OUT.relative_to(HERE.parent.parent)}", log_lines)

    # Extract draft. Handle three cases:
    #   1. Normal: message.content has the draft.
    #   2. Reasoning model: message.content is empty, message.reasoning_content has thinking,
    #      and the actual answer either follows or never came (hit max_tokens during reasoning).
    #   3. Inline thinking: message.content includes <think>...</think> tags wrapping reasoning,
    #      with the real answer after the closing tag.
    try:
        message = response["choices"][0]["message"]
    except (KeyError, IndexError) as e:
        log(f"ERROR: unexpected response shape from LM Studio: {e}", log_lines)
        LOG_OUT.write_text("\n".join(log_lines), encoding="utf-8")
        return 3

    raw_content = (message.get("content") or "").strip()
    reasoning = (message.get("reasoning_content") or "").strip()

    # Strip <think>...</think> blocks if present.
    import re
    stripped_content = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()

    if stripped_content:
        draft = stripped_content
        if reasoning:
            log(f"Note: model emitted {len(reasoning)} chars of reasoning_content (discarded).", log_lines)
        if raw_content != stripped_content:
            log("Note: <think> blocks stripped from content.", log_lines)
    elif reasoning:
        # Some Qwen 3.x configs put the entire answer in reasoning_content if /no_think didn't take.
        log("WARNING: message.content empty but reasoning_content present. Using reasoning as draft (may need cleanup).", log_lines)
        draft = reasoning
    else:
        log("ERROR: model returned no usable content. See raw_response.json for full payload.", log_lines)
        log("Common fixes: (a) ensure /no_think is at the top of system_prompt.md, (b) raise LM_STUDIO_MAX_TOKENS, (c) try a different model.", log_lines)
        DRAFT_OUT.write_text("", encoding="utf-8")
        LOG_OUT.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        return 4

    # Extract token counts (LM Studio usually returns these in `usage`).
    usage = response.get("usage", {}) or {}
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")

    log(f"Wall-clock: {elapsed_s:.2f}s", log_lines)
    log(f"Tokens: prompt={prompt_tokens} completion={completion_tokens} total={total_tokens}", log_lines)
    log(f"Draft length: {len(draft)} chars, ~{len(draft.split())} words", log_lines)

    DRAFT_OUT.write_text(draft.strip() + "\n", encoding="utf-8")
    log(f"Wrote draft -> {DRAFT_OUT.relative_to(HERE.parent.parent)}", log_lines)

    measurement = {
        "task": "draft core/rules/token-efficiency.md",
        "tier": "local-prework",
        "tool": "LM Studio",
        "endpoint": LM_STUDIO_URL,
        "model_id_configured": LM_STUDIO_MODEL,
        "loaded_models_reported": loaded,
        "temperature": TEMPERATURE,
        "max_tokens_request": MAX_TOKENS,
        "wall_clock_s": round(elapsed_s, 2),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "draft_chars": len(draft),
        "draft_words_approx": len(draft.split()),
        "dollar_cost_usd": 0.0,  # local model
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "notes": "First Sprint 1 measurement. Cloud-side review cost will be added in case-study-01.md.",
    }
    MEASUREMENT_OUT.write_text(json.dumps(measurement, indent=2) + "\n", encoding="utf-8")
    log(f"Wrote measurement -> {MEASUREMENT_OUT.relative_to(HERE.parent.parent)}", log_lines)

    LOG_OUT.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    log(f"Wrote log -> {LOG_OUT.relative_to(HERE.parent.parent)}", log_lines)

    return 0


if __name__ == "__main__":
    sys.exit(main())
