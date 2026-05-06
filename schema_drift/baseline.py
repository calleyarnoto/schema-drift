"""Baseline management: save and load comparison baselines for tracking schema drift over time."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from schema_drift.loader import load_schema_from_dict, schema_to_dict
from schema_drift.models import Table


@dataclass
class Baseline:
    name: str
    created_at: str
    tables: dict[str, Table] = field(default_factory=dict)
    description: str = ""

    def __repr__(self) -> str:
        return f"Baseline(name={self.name!r}, tables={len(self.tables)}, created_at={self.created_at!r})"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_baseline(
    tables: dict[str, Table],
    name: str,
    description: str = "",
) -> Baseline:
    """Create a new Baseline from a dict of Table objects."""
    return Baseline(
        name=name,
        created_at=_now_iso(),
        tables=tables,
        description=description,
    )


def save_baseline(baseline: Baseline, path: str) -> None:
    """Persist a Baseline to a JSON file."""
    payload = {
        "name": baseline.name,
        "created_at": baseline.created_at,
        "description": baseline.description,
        "schema": {
            "name": baseline.name,
            "tables": {name: schema_to_dict({name: tbl})["tables"][name]
                       for name, tbl in baseline.tables.items()},
        },
    }
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def load_baseline(path: str) -> Baseline:
    """Load a Baseline from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    schema_dict = payload["schema"]
    schema = load_schema_from_dict(schema_dict)
    return Baseline(
        name=payload["name"],
        created_at=payload.get("created_at", ""),
        description=payload.get("description", ""),
        tables=schema.tables,
    )


def baseline_exists(path: str) -> bool:
    """Return True if a baseline file exists at the given path."""
    return os.path.isfile(path)
