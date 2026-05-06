"""Formatters for DriftScore output."""

import json
from schema_drift.scorer import DriftScore


def format_score_text(score: DriftScore, schema_name: str = "") -> str:
    """Render a DriftScore as plain text."""
    lines: list[str] = []
    header = f"Drift Score Report"
    if schema_name:
        header += f" — {schema_name}"
    lines.append(header)
    lines.append("-" * len(header))
    lines.append(f"Severity : {score.severity.upper()}")
    lines.append(f"Total    : {score.total}")
    if score.breakdown:
        lines.append("Breakdown:")
        for diff_type, points in sorted(score.breakdown.items()):
            lines.append(f"  {diff_type:<30} {points}")
    else:
        lines.append("No drift detected.")
    return "\n".join(lines)


def format_score_json(score: DriftScore, schema_name: str = "") -> str:
    """Render a DriftScore as JSON."""
    payload: dict = {
        "schema": schema_name,
        "severity": score.severity,
        "total": score.total,
        "breakdown": score.breakdown,
    }
    return json.dumps(payload, indent=2)


def format_score_markdown(score: DriftScore, schema_name: str = "") -> str:
    """Render a DriftScore as Markdown."""
    lines: list[str] = []
    heading = f"## Drift Score Report"
    if schema_name:
        heading += f" — {schema_name}"
    lines.append(heading)
    lines.append(f"- **Severity**: {score.severity.upper()}")
    lines.append(f"- **Total score**: {score.total}")
    if score.breakdown:
        lines.append("\n| Diff Type | Points |")
        lines.append("|-----------|--------|")
        for diff_type, points in sorted(score.breakdown.items()):
            lines.append(f"| {diff_type} | {points} |")
    else:
        lines.append("\n_No drift detected._")
    return "\n".join(lines)


def format_score(
    score: DriftScore,
    fmt: str = "text",
    schema_name: str = "",
) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_score_json(score, schema_name)
    if fmt == "markdown":
        return format_score_markdown(score, schema_name)
    return format_score_text(score, schema_name)
