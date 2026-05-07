"""Snapshot management: capture and compare schema snapshots over time."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from schema_drift.loader import load_schema_from_dict, schema_to_dict
from schema_drift.models import Table


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Snapshot:
    name: str
    tables: Dict[str, Table]
    captured_at: str = field(default_factory=_now_iso)
    tag: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f"Snapshot(name={self.name!r}, tables={len(self.tables)}, "
            f"tag={self.tag!r}, captured_at={self.captured_at!r})"
        )


def capture_snapshot(
    schema_dict: dict,
    tag: Optional[str] = None,
) -> Snapshot:
    """Create a Snapshot from a raw schema dictionary."""
    schema = load_schema_from_dict(schema_dict)
    return Snapshot(
        name=schema.name,
        tables={t.name: t for t in schema.tables},
        tag=tag,
    )


def save_snapshot(snapshot: Snapshot, path: str | Path) -> None:
    """Persist a snapshot to a JSON file."""
    payload = {
        "name": snapshot.name,
        "captured_at": snapshot.captured_at,
        "tag": snapshot.tag,
        "tables": schema_to_dict({"name": snapshot.name, "tables": list(snapshot.tables.values())})["tables"],
    }
    Path(path).write_text(json.dumps(payload, indent=2))


def load_snapshot(path: str | Path) -> Snapshot:
    """Load a snapshot from a JSON file."""
    raw = json.loads(Path(path).read_text())
    schema = load_schema_from_dict({"name": raw["name"], "tables": raw["tables"]})
    return Snapshot(
        name=raw["name"],
        tables={t.name: t for t in schema.tables},
        captured_at=raw.get("captured_at", ""),
        tag=raw.get("tag"),
    )


def list_snapshots(directory: str | Path) -> List[Snapshot]:
    """Return all snapshots found in a directory, sorted by captured_at."""
    directory = Path(directory)
    snapshots = []
    for p in sorted(directory.glob("*.snapshot.json")):
        try:
            snapshots.append(load_snapshot(p))
        except (KeyError, json.JSONDecodeError):
            continue
    snapshots.sort(key=lambda s: s.captured_at)
    return snapshots
