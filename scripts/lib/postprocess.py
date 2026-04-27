"""
postprocess.py — shared post-processing utilities for SustainDev probe scripts.

The pattern these utilities encode emerged across case-studies 04, 05, and 06
in the SustainDev public repo:

  Every probe script that asks a local model to produce structured output
  needs to defend against the model's packaging quirks — leaked reasoning
  in visible content, empty visible content with everything in
  reasoning_content, wrong arithmetic in summary lines, duplicate rows,
  inline planning prose, etc.

This module gives each probe script the same defensive primitives instead
of letting them drift apart. Probe scripts import via sys.path manipulation
(the typical pattern in scripts/sprint1/* and scripts/schedule/*):

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
    from postprocess import strip_think_tags, recompute_table_counts, ...

Zero external dependencies (stdlib only).
"""

from __future__ import annotations

import random
import re
from typing import Optional


# --- Reasoning + planning text removal --------------------------------------


def strip_think_tags(text: str) -> str:
    """Remove <think>...</think> blocks (any case, any whitespace) from text.

    Some local models wrap reasoning in <think> tags inside the visible content
    channel. This strips them defensively before downstream parsing.
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()


_PLANNING_MARKERS = (
    "thinking process:",
    "thinking process",
    "let me think",
    "let's think",
    "let me analyze",
    "step 1:",
    "1. analyze the",
    "1.  analyze the",
    "1. analyse the",
    "first, i need to",
    "first, let me",
    "i need to parse",
    "self-correction",
)


def detect_planning_prose(text: str, head_chars: int = 600) -> bool:
    """Heuristic: does the head of `text` look like the model's planning prose?

    We check the first `head_chars` of the (lowercased) text for known
    planning markers. Returns True if any marker is found near the start.
    """
    head = text[:head_chars].lower()
    return any(m in head for m in _PLANNING_MARKERS)


def extract_after_planning(
    text: str,
    anchor_pattern: str = r"^\s*#+\s+",
    dedent: bool = True,
) -> str:
    """Find the first line matching anchor_pattern and return text from there.

    Useful when the model's output has a planning-prose preamble followed by
    the actual artifact. The anchor_pattern is a regex applied to lines;
    default `^\\s*#+\\s+` finds the first markdown heading (any level, with
    optional leading whitespace — Qwen 3.5 9B sometimes indents headings 4-8
    spaces inside its reasoning context).

    Args:
        text: input text (typically containing planning prose then artifact).
        anchor_pattern: regex applied to each line; first match wins.
        dedent: if True (default), strip the common leading whitespace from
            all returned lines. The model often emits indented markdown
            inside reasoning; un-indenting restores standard markdown.

    Returns the text from the matched line onward, optionally dedented.
    If no anchor line is found, returns the original text unchanged.
    """
    lines = text.splitlines()
    pattern = re.compile(anchor_pattern, re.MULTILINE)
    for i, line in enumerate(lines):
        if pattern.match(line):
            tail = lines[i:]
            if dedent:
                # Strip the leading whitespace of the matched line from all
                # subsequent lines. This pulls indented markdown back to
                # column 0 while preserving relative indentation of nested
                # content (sub-bullets, code blocks, etc.).
                strip_len = len(line) - len(line.lstrip())
                if strip_len > 0:
                    tail = [
                        (ln[strip_len:] if len(ln) >= strip_len and not ln[:strip_len].strip() else ln)
                        for ln in tail
                    ]
            return "\n".join(tail)
    return text


# --- Table-row utilities ----------------------------------------------------


def _parse_markdown_row(line: str) -> Optional[list[str]]:
    """Return the cell strings of a markdown table row, or None if not a row.

    Header and separator rows are returned with their cells; callers filter.
    """
    if not line.startswith("|"):
        return None
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return all(set(c) <= set("- :") for c in cells if c) and any("-" in c for c in cells)


def recompute_table_counts(
    text: str,
    bucket_column_index: int,
    valid_buckets: tuple[str, ...],
    counts_line_prefix: str = "Counts:",
    counts_line_format: str = "Counts (verified by post-processing): {body} (total={total}; rows seen={rows})",
) -> tuple[str, dict, list[str]]:
    """Recompute bucket counts from a markdown table; replace any model-emitted
    counts line with verified counts.

    The model's reported totals are unreliable (case-study-04 finding #7); this
    function parses the table itself and produces honest counts.

    Args:
        text: the model's output containing one markdown table plus optional
            counts line.
        bucket_column_index: 0-based index of the cell holding the bucket label.
        valid_buckets: tuple of allowed bucket strings (e.g. ("commit-now",
            "review-first", "archive", "build-artifact")).
        counts_line_prefix: any line starting with this string (case-insensitive)
            is treated as a model-emitted counts line and removed.
        counts_line_format: template for the verified counts line. Receives
            `body` (comma-separated bucket=N), `total` (sum of buckets), and
            `rows` (table rows seen, excluding header/separator).

    Returns:
        (rewritten_text, counts_dict, anomalies)
        rewritten_text: input with the model's counts line removed and the
            verified counts line appended.
        counts_dict: {bucket: int, "total": int, "table_rows": int}.
        anomalies: list of human-readable warning strings for unrecognized
            bucket values, etc.
    """
    counts = {b: 0 for b in valid_buckets}
    anomalies: list[str] = []
    table_rows = 0
    body_lines: list[str] = []
    prefix_re = re.compile(rf"^{re.escape(counts_line_prefix)}\s*", re.IGNORECASE)

    for line in text.splitlines():
        if prefix_re.match(line.strip()):
            continue  # Drop the model's counts line.
        body_lines.append(line)
        cells = _parse_markdown_row(line)
        if cells is None:
            continue
        if len(cells) <= bucket_column_index:
            continue
        bucket_cell = cells[bucket_column_index]
        # Skip the header row.
        if bucket_cell.lower() == "bucket":
            continue
        # Skip the separator row.
        if _is_separator_row(cells):
            continue
        table_rows += 1
        if bucket_cell in counts:
            counts[bucket_cell] += 1
        else:
            anomalies.append(
                f"unrecognized bucket value '{bucket_cell}' on row "
                f"(first cell: {cells[0]!r})"
            )

    total = sum(counts.values())
    body = ", ".join(f"{b}={counts[b]}" for b in valid_buckets)
    counts_line = counts_line_format.format(body=body, total=total, rows=table_rows)
    rewritten = "\n".join(body_lines).rstrip() + "\n\n" + counts_line + "\n"
    return rewritten, {**counts, "total": total, "table_rows": table_rows}, anomalies


def annotate_sample_rows(
    table_text: str, sample_rate: float, seed: int = 0, marker: str = "[SAMPLED]"
) -> str:
    """Mark a random subset of markdown-table rows for human spot-check.

    Rows are detected by leading `|` and excluded if they are header/separator.
    The marker is prepended to the first cell of selected rows.

    Args:
        table_text: text containing a markdown table.
        sample_rate: 0.0 - 1.0 fraction of rows to mark.
        seed: rng seed for reproducible sampling.
        marker: string prepended to the first cell of each sampled row.

    Returns:
        text with the same content plus markers on the sampled rows.
    """
    if sample_rate <= 0:
        return table_text
    rng = random.Random(seed)
    out_lines: list[str] = []
    for line in table_text.splitlines():
        cells = _parse_markdown_row(line)
        if cells is None or _is_separator_row(cells):
            out_lines.append(line)
            continue
        if cells[0].lower() == "file" or cells[0].lower() == "name":
            out_lines.append(line)
            continue
        if rng.random() < sample_rate:
            cells[0] = f"{marker} {cells[0]}".strip()
            line = "| " + " | ".join(cells) + " |"
        out_lines.append(line)
    return "\n".join(out_lines)


# --- Section-header utilities -----------------------------------------------


def dedupe_section_headers(text: str, header_pattern: str = r"^### `?([^`\n]+?)`?\s*$") -> tuple[str, list[str]]:
    """Find duplicate H3-style section headers and remove the second-and-later
    occurrences plus their entire body up to the next header (or EOF).

    Used to fix the case-study-05 finding where draft-catalog.py output had
    one service entry duplicated with identical content.

    Args:
        text: the model's output with H3 section headers.
        header_pattern: regex with one capture group matching the section name.
            Default matches `### `Name`` or `### Name`.

    Returns:
        (deduped_text, removed_names)
        deduped_text: the first occurrence of each section name kept, later
            occurrences (and their bodies) removed.
        removed_names: list of section names that were deduplicated (one
            entry per removal).
    """
    pattern = re.compile(header_pattern, re.MULTILINE)
    lines = text.splitlines()
    seen: set[str] = set()
    out_lines: list[str] = []
    skip_until_next_header = False
    removed: list[str] = []
    for line in lines:
        match = pattern.match(line)
        if match:
            name = match.group(1).strip()
            if name in seen:
                # Start skipping until we hit another section header (or EOF).
                skip_until_next_header = True
                removed.append(name)
                continue
            seen.add(name)
            skip_until_next_header = False
            out_lines.append(line)
            continue
        # If this line starts a new H3 header even without matching the
        # specific pattern, stop the skip.
        if line.startswith("### ") and skip_until_next_header:
            # Different header pattern; stop skipping.
            skip_until_next_header = False
            out_lines.append(line)
            continue
        if skip_until_next_header:
            continue
        out_lines.append(line)
    return "\n".join(out_lines), removed


# --- Multi-draft extraction (for summarization-style outputs) ---------------


_DRAFT_MARKERS = (
    # Loose: match "Revised Draft" / "Final Draft" / "Final Output" anywhere
    # on a line, optionally surrounded by markdown emphasis or list markers.
    # Empirically, Qwen 3.5 9B emits patterns like "    *   *Revised Draft:*"
    # (list-bullet + italic), or "**Revised Draft**:". We just want to find
    # the position of the marker; what surrounds it doesn't matter.
    r"Revised Draft\b",
    r"Final Draft\b",
    r"Final Output\b",
)


def extract_last_draft(
    text: str,
    anchor_pattern: str = r"^\s*#+\s+",
    dedent: bool = True,
) -> Optional[str]:
    """When the model emits multiple drafts during reasoning, find the LAST one.

    Strategy: locate all matches of common draft-marker phrases ("Revised
    Draft", "Final Draft", "Final Output"). For the LAST match, return the
    text from the next line that matches `anchor_pattern` (default: any
    markdown heading with optional leading whitespace) to the end.

    If no draft markers are found, fall back to extract_after_planning.

    Args:
        text: model output text containing one or more draft sections.
        anchor_pattern: regex for the first artifact line after the marker.
        dedent: strip common leading whitespace from the returned text.

    Returns the extracted text (dedented if requested), or None if nothing
    usable was found.
    """
    last_marker_pos = -1
    for marker_re in _DRAFT_MARKERS:
        for m in re.finditer(marker_re, text, flags=re.MULTILINE | re.IGNORECASE):
            if m.start() > last_marker_pos:
                last_marker_pos = m.start()
    if last_marker_pos < 0:
        candidate = extract_after_planning(text, anchor_pattern, dedent)
        return candidate if candidate else None
    after_marker = text[last_marker_pos:]
    return extract_after_planning(after_marker, anchor_pattern, dedent)
