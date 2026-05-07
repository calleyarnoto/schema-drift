"""Format annotated diffs as text, JSON, or Markdown."""

import json
from typing import List

from schema_drift.annotator import Annotation, highest_risk

_RISK_EMOJI = {"low": "🟢", "medium": "🟡", "high": "🔴"}


def format_annotation_text(annotations: List[Annotation]) -> str:
    if not annotations:
        return "No diffs to annotate.\n"
    lines = ["=== Annotated Diff Report ==="]
    overall = highest_risk(annotations)
    lines.append(f"Overall risk: {_RISK_EMOJI.get(overall, '')} {overall.upper()}\n")
    for ann in annotations:
        emoji = _RISK_EMOJI.get(ann.risk, "")
        lines.append(f"  {emoji} [{ann.risk.upper()}] {ann.description}")
        if ann.hint:
            lines.append(f"      Hint: {ann.hint}")
    lines.append("")
    return "\n".join(lines)


def format_annotation_json(annotations: List[Annotation]) -> str:
    payload = [
        {
            "table": ann.diff.table_name,
            "column": ann.diff.column_name,
            "diff_type": ann.diff.diff_type.value,
            "description": ann.description,
            "risk": ann.risk,
            "hint": ann.hint,
        }
        for ann in annotations
    ]
    return json.dumps({"overall_risk": highest_risk(annotations), "annotations": payload}, indent=2)


def format_annotation_markdown(annotations: List[Annotation]) -> str:
    if not annotations:
        return "_No diffs to annotate._\n"
    overall = highest_risk(annotations)
    lines = [
        "## Annotated Diff Report",
        f"",
        f"**Overall risk:** {_RISK_EMOJI.get(overall, '')} `{overall.upper()}`",
        "",
        "| Risk | Table | Column | Description |",
        "|------|-------|--------|-------------|" ,
    ]
    for ann in annotations:
        col = ann.diff.column_name or "—"
        emoji = _RISK_EMOJI.get(ann.risk, "")
        lines.append(f"| {emoji} {ann.risk} | `{ann.diff.table_name}` | `{col}` | {ann.description} |")
    lines.append("")
    return "\n".join(lines)


def format_annotation(annotations: List[Annotation], fmt: str = "text") -> str:
    fmt = fmt.lower()
    if fmt == "json":
        return format_annotation_json(annotations)
    if fmt in ("md", "markdown"):
        return format_annotation_markdown(annotations)
    return format_annotation_text(annotations)
