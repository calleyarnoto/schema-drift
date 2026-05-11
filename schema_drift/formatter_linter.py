"""Formatters for LintReport output."""

import json
from schema_drift.linter import LintReport


def format_lint_text(report: LintReport) -> str:
    lines = [f"Lint Report — {report.schema_name}"]
    lines.append("=" * 40)
    if not report.has_warnings:
        lines.append("No lint warnings found.")
        return "\n".join(lines)
    lines.append(f"{report.warning_count} warning(s) found:\n")
    for w in report.warnings:
        loc = f"{w.table}.{w.column}" if w.column else w.table
        lines.append(f"  [{w.code}] {loc}")
        lines.append(f"         {w.message}")
    return "\n".join(lines)


def format_lint_json(report: LintReport) -> str:
    data = {
        "schema_name": report.schema_name,
        "warning_count": report.warning_count,
        "warnings": [
            {
                "code": w.code,
                "table": w.table,
                "column": w.column,
                "message": w.message,
            }
            for w in report.warnings
        ],
    }
    return json.dumps(data, indent=2)


def format_lint_markdown(report: LintReport) -> str:
    lines = [f"## Lint Report — {report.schema_name}", ""]
    if not report.has_warnings:
        lines.append("_No lint warnings found._")
        return "\n".join(lines)
    lines.append(f"**{report.warning_count} warning(s) found**", )
    lines.append("")
    lines.append("| Code | Location | Message |")
    lines.append("|------|----------|---------|")
    for w in report.warnings:
        loc = f"{w.table}.{w.column}" if w.column else w.table
        lines.append(f"| `{w.code}` | `{loc}` | {w.message} |")
    return "\n".join(lines)


def format_lint(report: LintReport, fmt: str = "text") -> str:
    fmt = fmt.lower()
    if fmt == "json":
        return format_lint_json(report)
    if fmt in ("md", "markdown"):
        return format_lint_markdown(report)
    return format_lint_text(report)
