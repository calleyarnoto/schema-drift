"""Format a SchemaSummary into human-readable or machine-readable output."""

import json
from typing import Callable, Dict

from schema_drift.summarizer import SchemaSummary


def format_summary_text(summary: SchemaSummary) -> str:
    """Render a SchemaSummary as plain text."""
    lines = [
        f"Schema Summary: {summary.schema_name}",
        "-" * 40,
        f"Total diffs     : {summary.total_diffs}",
        f"Tables added    : {summary.tables_added}",
        f"Tables removed  : {summary.tables_removed}",
        f"Tables modified : {summary.tables_modified}",
    ]
    if summary.diffs_by_type:
        lines.append("Diffs by type:")
        for diff_type, count in sorted(summary.diffs_by_type.items()):
            lines.append(f"  {diff_type:<25}: {count}")
    if summary.affected_tables:
        lines.append("Affected tables:")
        for table in summary.affected_tables:
            lines.append(f"  - {table}")
    return "\n".join(lines)


def format_summary_json(summary: SchemaSummary) -> str:
    """Render a SchemaSummary as JSON."""
    data = {
        "schema_name": summary.schema_name,
        "total_diffs": summary.total_diffs,
        "tables_added": summary.tables_added,
        "tables_removed": summary.tables_removed,
        "tables_modified": summary.tables_modified,
        "diffs_by_type": summary.diffs_by_type,
        "affected_tables": summary.affected_tables,
    }
    return json.dumps(data, indent=2)


def format_summary_markdown(summary: SchemaSummary) -> str:
    """Render a SchemaSummary as Markdown."""
    lines = [
        f"## Schema Summary: `{summary.schema_name}`",
        "",
        f"| Metric | Value |",
        f"|--------|-------|" ,
        f"| Total diffs | {summary.total_diffs} |",
        f"| Tables added | {summary.tables_added} |",
        f"| Tables removed | {summary.tables_removed} |",
        f"| Tables modified | {summary.tables_modified} |",
    ]
    if summary.affected_tables:
        lines += ["", "### Affected Tables", ""]
        for table in summary.affected_tables:
            lines.append(f"- `{table}`")
    return "\n".join(lines)


_FORMATTERS: Dict[str, Callable[[SchemaSummary], str]] = {
    "text": format_summary_text,
    "json": format_summary_json,
    "markdown": format_summary_markdown,
}


def format_summary(summary: SchemaSummary, fmt: str = "text") -> str:
    """Dispatch to the appropriate summary formatter."""
    formatter = _FORMATTERS.get(fmt)
    if formatter is None:
        raise ValueError(f"Unknown format {fmt!r}. Choose from: {list(_FORMATTERS)}.")
    return formatter(summary)
