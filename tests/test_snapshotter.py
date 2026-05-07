"""Tests for schema_drift.snapshotter."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from schema_drift.snapshotter import (
    Snapshot,
    capture_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)

_SCHEMA = {
    "name": "production",
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False},
                {"name": "email", "type": "VARCHAR", "nullable": False},
            ],
        }
    ],
}


def test_capture_snapshot_name():
    snap = capture_snapshot(_SCHEMA)
    assert snap.name == "production"


def test_capture_snapshot_tables():
    snap = capture_snapshot(_SCHEMA)
    assert "users" in snap.tables


def test_capture_snapshot_tag():
    snap = capture_snapshot(_SCHEMA, tag="v1.2")
    assert snap.tag == "v1.2"


def test_capture_snapshot_captured_at_set():
    snap = capture_snapshot(_SCHEMA)
    assert snap.captured_at  # non-empty ISO string


def test_snapshot_repr():
    snap = capture_snapshot(_SCHEMA, tag="beta")
    r = repr(snap)
    assert "production" in r
    assert "beta" in r


def test_save_and_load_snapshot(tmp_path):
    snap = capture_snapshot(_SCHEMA, tag="test")
    dest = tmp_path / "snap.snapshot.json"
    save_snapshot(snap, dest)
    loaded = load_snapshot(dest)
    assert loaded.name == snap.name
    assert loaded.tag == snap.tag
    assert "users" in loaded.tables


def test_save_creates_valid_json(tmp_path):
    snap = capture_snapshot(_SCHEMA)
    dest = tmp_path / "snap.snapshot.json"
    save_snapshot(snap, dest)
    raw = json.loads(dest.read_text())
    assert raw["name"] == "production"
    assert isinstance(raw["tables"], list)


def test_list_snapshots_empty(tmp_path):
    result = list_snapshots(tmp_path)
    assert result == []


def test_list_snapshots_returns_sorted(tmp_path):
    for tag in ["a", "b", "c"]:
        snap = capture_snapshot(_SCHEMA, tag=tag)
        save_snapshot(snap, tmp_path / f"{tag}.snapshot.json")
    snaps = list_snapshots(tmp_path)
    assert len(snaps) == 3
    captured_ats = [s.captured_at for s in snaps]
    assert captured_ats == sorted(captured_ats)


def test_list_snapshots_ignores_non_snapshot_files(tmp_path):
    (tmp_path / "notes.txt").write_text("ignore me")
    snap = capture_snapshot(_SCHEMA)
    save_snapshot(snap, tmp_path / "one.snapshot.json")
    result = list_snapshots(tmp_path)
    assert len(result) == 1
