"""Formats a ValidationReport into text, JSON, or Markdown."""

import json
from typing import Literal

from schema_drift.validator import ValidationReport

FormatType = Literal["text", "json", "markdown"]


def format_validation_text(report: ValidationReport) -> str:
    lines = ["=== Validation Report ==="]
    if not report.issues:
        lines.append("No issues found.")
        return "\n".join(lines)

    if report.errors:
        lines.append(f"\nErrors ({len(report.errors)}):")
        for issue in report.errors:
            lines.append(f"  [{issue.code}] {issue.message}")

    if report.warnings:
        lines.append(f"\nWarnings ({len(report.warnings)}):")
        for issue in report.warnings:
            lines.append(f"  [{issue.code}] {issue.message}")

    lines.append(
        f"\nTotal: {len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )
    return "\n".join(lines)


def format_validation_json(report: ValidationReport) -> str:
    data = {
        "errors": [
            {"code": i.code, "message": i.message}
            for i in report.errors
        ],
        "warnings": [
            {"code": i.code, "message": i.message}
            for i in report.warnings
        ],
        "summary": {
            "total_errors": len(report.errors),
            "total_warnings": len(report.warnings),
        },
    }
    return json.dumps(data, indent=2)


def format_validation_markdown(report: ValidationReport) -> str:
    lines = ["## Validation Report"]
    if not report.issues:
        lines.append("_No issues found._")
        return "\n".join(lines)

    if report.errors:
        lines.append(f"\n### Errors ({len(report.errors)})")
        for issue in report.errors:
            lines.append(f"- **[{issue.code}]** {issue.message}")

    if report.warnings:
        lines.append(f"\n### Warnings ({len(report.warnings)})")
        for issue in report.warnings:
            lines.append(f"- **[{issue.code}]** {issue.message}")

    lines.append(
        f"\n> {len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )
    return "\n".join(lines)


def format_validation(report: ValidationReport, fmt: FormatType = "text") -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_validation_json(report)
    if fmt == "markdown":
        return format_validation_markdown(report)
    return format_validation_text(report)
