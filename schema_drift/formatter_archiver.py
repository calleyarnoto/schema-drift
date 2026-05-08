"""Format archived comparison results for display."""

from __future__ import annotations

import json
from typing import List

from schema_drift.archiver import ArchivedResult


def format_archive_text(entries: List[ArchivedResult]) -> str:
    """Render a list of archived results as a human-readable text table."""
    if not entries:
        return "No archived comparisons found.\n"

    lines = ["Archived Comparisons", "=" * 40]
    for i, entry in enumerate(entries, start=1):
        lines.append(f"  [{i}] {entry.label}")
        lines.append(f"      Source : {entry.source_name}")
        lines.append(f"      Target : {entry.target_name}")
        lines.append(f"      Diffs  : {entry.diff_count}")
        lines.append(f"      Date   : {entry.created_at}")
        lines.append("")
    return "\n".join(lines)


def format_archive_json(entries: List[ArchivedResult]) -> str:
    """Render archived results as a JSON array (metadata only, no payload)."""
    records = [
        {
            "label": e.label,
            "source_name": e.source_name,
            "target_name": e.target_name,
            "created_at": e.created_at,
            "diff_count": e.diff_count,
        }
        for e in entries
    ]
    return json.dumps(records, indent=2)


def format_archive_markdown(entries: List[ArchivedResult]) -> str:
    """Render archived results as a Markdown table."""
    if not entries:
        return "_No archived comparisons found._\n"

    lines = [
        "## Archived Comparisons",
        "",
        "| Label | Source | Target | Diffs | Date |",
        "|-------|--------|--------|-------|------|",
    ]
    for entry in entries:
        lines.append(
            f"| {entry.label} | {entry.source_name} | "
            f"{entry.target_name} | {entry.diff_count} | {entry.created_at} |"
        )
    lines.append("")
    return "\n".join(lines)


def format_archive(
    entries: List[ArchivedResult], fmt: str = "text"
) -> str:
    """Dispatch to the appropriate formatter."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_archive_json(entries)
    if fmt in ("md", "markdown"):
        return format_archive_markdown(entries)
    return format_archive_text(entries)
