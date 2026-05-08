"""Archive and retrieve historical comparison results."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from schema_drift.loader import load_schema_from_dict, schema_to_dict
from schema_drift.comparator import ComparisonResult, compare_schemas


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ArchivedResult:
    """A timestamped, labelled snapshot of a comparison result."""

    label: str
    source_name: str
    target_name: str
    created_at: str = field(default_factory=_now_iso)
    diff_count: int = 0
    payload: dict = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ArchivedResult(label={self.label!r}, "
            f"diffs={self.diff_count}, created_at={self.created_at!r})"
        )


def archive_result(result: ComparisonResult, label: str) -> ArchivedResult:
    """Wrap a ComparisonResult in an ArchivedResult for storage."""
    diffs = result.diffs if result.diffs else []
    payload = {
        "source": schema_to_dict(result.source),
        "target": schema_to_dict(result.target),
        "diffs": [
            {
                "diff_type": d.diff_type.value,
                "table_name": d.table_name,
                "column_name": d.column_name,
                "detail": d.detail,
            }
            for d in diffs
        ],
    }
    return ArchivedResult(
        label=label,
        source_name=result.source.name,
        target_name=result.target.name,
        diff_count=len(diffs),
        payload=payload,
    )


def save_archive(entry: ArchivedResult, path: str) -> None:
    """Append an ArchivedResult to a JSON-lines archive file."""
    record = {
        "label": entry.label,
        "source_name": entry.source_name,
        "target_name": entry.target_name,
        "created_at": entry.created_at,
        "diff_count": entry.diff_count,
        "payload": entry.payload,
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def load_archive(path: str) -> List[ArchivedResult]:
    """Load all ArchivedResult entries from a JSON-lines archive file."""
    if not os.path.exists(path):
        return []
    results: List[ArchivedResult] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            results.append(
                ArchivedResult(
                    label=data["label"],
                    source_name=data["source_name"],
                    target_name=data["target_name"],
                    created_at=data["created_at"],
                    diff_count=data["diff_count"],
                    payload=data["payload"],
                )
            )
    return results
