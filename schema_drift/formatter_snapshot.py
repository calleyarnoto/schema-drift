"""Format snapshot information for text, JSON, and Markdown output."""

from __future__ import annotations

import json
from typing import List

from schema_drift.snapshotter import Snapshot


def format_snapshot_text(snapshot: Snapshot) -> str:
    lines = [
        f"Snapshot: {snapshot.name}",
        f"Captured: {snapshot.captured_at}",
    ]
    if snapshot.tag:
        lines.append(f"Tag:      {snapshot.tag}")
    lines.append(f"Tables:   {len(snapshot.tables)}")
    for table_name in sorted(snapshot.tables):
        t = snapshot.tables[table_name]
        lines.append(f"  - {table_name} ({len(t.columns)} columns)")
    return "\n".join(lines)


def format_snapshot_list_text(snapshots: List[Snapshot]) -> str:
    if not snapshots:
        return "No snapshots found."
    lines = [f"{len(snapshots)} snapshot(s) found:", ""]
    for s in snapshots:
        tag_part = f" [{s.tag}]" if s.tag else ""
        lines.append(f"  {s.captured_at}  {s.name}{tag_part}  ({len(s.tables)} tables)")
    return "\n".join(lines)


def format_snapshot_json(snapshot: Snapshot) -> str:
    return json.dumps(
        {
            "name": snapshot.name,
            "captured_at": snapshot.captured_at,
            "tag": snapshot.tag,
            "table_count": len(snapshot.tables),
            "tables": sorted(snapshot.tables.keys()),
        },
        indent=2,
    )


def format_snapshot_markdown(snapshot: Snapshot) -> str:
    lines = [
        f"## Snapshot: `{snapshot.name}`",
        "",
        f"- **Captured:** {snapshot.captured_at}",
        f"- **Tag:** {snapshot.tag or '—'}",
        f"- **Tables:** {len(snapshot.tables)}",
        "",
        "| Table | Columns |",
        "| ----- | ------- |",
    ]
    for table_name in sorted(snapshot.tables):
        t = snapshot.tables[table_name]
        lines.append(f"| `{table_name}` | {len(t.columns)} |")
    return "\n".join(lines)


def format_snapshot(
    snapshot: Snapshot,
    fmt: str = "text",
) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_snapshot_json(snapshot)
    if fmt == "markdown":
        return format_snapshot_markdown(snapshot)
    return format_snapshot_text(snapshot)
