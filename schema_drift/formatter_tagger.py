"""Formatters for TaggedResult objects."""

import json
from typing import Literal

from schema_drift.tagger import TaggedResult

FormatName = Literal["text", "json", "markdown"]


def format_tagged_text(result: TaggedResult) -> str:
    lines = [
        f"Tagged Drift Report: {result.source_name} → {result.target_name}",
        "-" * 60,
    ]
    if not result.tagged_diffs:
        lines.append("No diffs found.")
        return "\n".join(lines)

    for td in result.tagged_diffs:
        tag_str = ", ".join(sorted(td.tags)) if td.tags else "(untagged)"
        lines.append(f"  [{tag_str}] {td.diff!r}")
    return "\n".join(lines)


def format_tagged_json(result: TaggedResult) -> str:
    payload = {
        "source": result.source_name,
        "target": result.target_name,
        "diffs": [
            {
                "table": td.diff.table_name,
                "diff_type": td.diff.diff_type.value,
                "tags": sorted(td.tags),
            }
            for td in result.tagged_diffs
        ],
        "all_tags": result.all_tags(),
    }
    return json.dumps(payload, indent=2)


def format_tagged_markdown(result: TaggedResult) -> str:
    lines = [
        f"## Tagged Drift Report",
        f"**Source:** {result.source_name}  ",
        f"**Target:** {result.target_name}",
        "",
    ]
    if not result.tagged_diffs:
        lines.append("_No diffs found._")
        return "\n".join(lines)

    lines.append("| Table | Diff Type | Tags |")
    lines.append("|-------|-----------|------|")
    for td in result.tagged_diffs:
        tag_str = ", ".join(sorted(td.tags)) if td.tags else "—"
        lines.append(
            f"| {td.diff.table_name} | {td.diff.diff_type.value} | {tag_str} |"
        )
    return "\n".join(lines)


def format_tagged(result: TaggedResult, fmt: FormatName = "text") -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_tagged_json(result)
    if fmt == "markdown":
        return format_tagged_markdown(result)
    return format_tagged_text(result)
