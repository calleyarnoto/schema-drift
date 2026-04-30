"""Formatters for schema diff output in multiple formats (text, JSON, Markdown)."""

import json
from typing import List
from schema_drift.comparator import ComparisonResult, DiffType


def format_text(result: ComparisonResult) -> str:
    """Format a ComparisonResult as plain text."""
    lines = []
    schema_label = (
        f"Schema: {result.schema_name}" if result.schema_name else "Schema Comparison"
    )
    lines.append(schema_label)
    lines.append("=" * len(schema_label))

    if not result.has_changes():
        lines.append("No differences found.")
        return "\n".join(lines)

    for diff in result.diffs:
        prefix = {
            DiffType.TABLE_ADDED: "[+]",
            DiffType.TABLE_REMOVED: "[-]",
            DiffType.COLUMN_ADDED: "  [+]",
            DiffType.COLUMN_REMOVED: "  [-]",
            DiffType.COLUMN_MODIFIED: "  [~]",
        }.get(diff.diff_type, "  [?]")
        lines.append(f"{prefix} {diff}")

    lines.append(f"\nTotal changes: {len(result.diffs)}")
    return "\n".join(lines)


def format_json(result: ComparisonResult) -> str:
    """Format a ComparisonResult as a JSON string."""
    payload = {
        "schema_name": result.schema_name,
        "has_changes": result.has_changes(),
        "total_changes": len(result.diffs),
        "diffs": [
            {
                "diff_type": diff.diff_type.value,
                "table": diff.table_name,
                "column": diff.column_name,
                "detail": diff.detail,
            }
            for diff in result.diffs
        ],
    }
    return json.dumps(payload, indent=2)


def format_markdown(result: ComparisonResult) -> str:
    """Format a ComparisonResult as a Markdown report."""
    lines = []
    schema_label = result.schema_name or "Schema Comparison"
    lines.append(f"# Schema Drift Report: {schema_label}")
    lines.append("")

    if not result.has_changes():
        lines.append("_No differences found._")
        return "\n".join(lines)

    lines.append(f"**Total changes:** {len(result.diffs)}")
    lines.append("")
    lines.append("| Type | Table | Column | Detail |")
    lines.append("|------|-------|--------|--------|")

    for diff in result.diffs:
        dtype = diff.diff_type.value.replace("_", " ").title()
        table = diff.table_name or ""
        column = diff.column_name or ""
        detail = diff.detail or ""
        lines.append(f"| {dtype} | {table} | {column} | {detail} |")

    return "\n".join(lines)


FORMAT_HANDLERS = {
    "text": format_text,
    "json": format_json,
    "markdown": format_markdown,
}


def format_result(result: ComparisonResult, fmt: str = "text") -> str:
    """Dispatch to the appropriate formatter by name."""
    handler = FORMAT_HANDLERS.get(fmt)
    if handler is None:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {list(FORMAT_HANDLERS)}")
    return handler(result)
