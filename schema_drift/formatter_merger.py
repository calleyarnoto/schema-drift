"""Formatters for MergedResult output."""

import json
from typing import Literal

from schema_drift.merger import MergedResult


def format_merged_text(merged: MergedResult) -> str:
    lines = [f"=== Merged Diff Report: {merged.label} ==="]
    lines.append(f"Sources: {', '.join(merged.sources)}")
    lines.append(f"Total diffs: {merged.diff_count}")
    lines.append("")

    if not merged.has_changes:
        lines.append("No differences found across merged results.")
        return "\n".join(lines)

    for diff in merged.diffs:
        lines.append(f"  [{diff.diff_type.value}] {diff.table_name}"
                     + (f".{diff.column_name}" if diff.column_name else ""))
        if diff.detail:
            lines.append(f"    {diff.detail}")

    return "\n".join(lines)


def format_merged_json(merged: MergedResult) -> str:
    data = {
        "label": merged.label,
        "sources": merged.sources,
        "diff_count": merged.diff_count,
        "diffs": [
            {
                "diff_type": d.diff_type.value,
                "table_name": d.table_name,
                "column_name": d.column_name,
                "detail": d.detail,
            }
            for d in merged.diffs
        ],
    }
    return json.dumps(data, indent=2)


def format_merged_markdown(merged: MergedResult) -> str:
    lines = [f"## Merged Diff Report: {merged.label}"]
    lines.append(f"**Sources:** {', '.join(merged.sources)}  ")
    lines.append(f"**Total diffs:** {merged.diff_count}  ")
    lines.append("")

    if not merged.has_changes:
        lines.append("_No differences found across merged results._")
        return "\n".join(lines)

    lines.append("| Type | Table | Column | Detail |")
    lines.append("|------|-------|--------|--------|")
    for diff in merged.diffs:
        col = diff.column_name or "-"
        detail = diff.detail or "-"
        lines.append(f"| {diff.diff_type.value} | {diff.table_name} | {col} | {detail} |")

    return "\n".join(lines)


def format_merged(
    merged: MergedResult,
    fmt: Literal["text", "json", "markdown"] = "text",
) -> str:
    if fmt == "json":
        return format_merged_json(merged)
    if fmt == "markdown":
        return format_merged_markdown(merged)
    return format_merged_text(merged)
