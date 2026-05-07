"""Tests for schema_drift.formatter_snapshot."""

from __future__ import annotations

import json

import pytest

from schema_drift.snapshotter import capture_snapshot
from schema_drift.formatter_snapshot import (
    format_snapshot,
    format_snapshot_json,
    format_snapshot_list_text,
    format_snapshot_markdown,
    format_snapshot_text,
)

_SCHEMA = {
    "name": "staging",
    "tables": [
        {
            "name": "orders",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False},
                {"name": "total", "type": "NUMERIC", "nullable": True},
            ],
        },
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False},
            ],
        },
    ],
}


@pytest.fixture
def snap():
    return capture_snapshot(_SCHEMA, tag="rc1")


class TestFormatSnapshotText:
    def test_name_in_output(self, snap):
        out = format_snapshot_text(snap)
        assert "staging" in out

    def test_tag_in_output(self, snap):
        out = format_snapshot_text(snap)
        assert "rc1" in out

    def test_table_count_shown(self, snap):
        out = format_snapshot_text(snap)
        assert "2" in out

    def test_table_names_listed(self, snap):
        out = format_snapshot_text(snap)
        assert "orders" in out
        assert "users" in out

    def test_no_tag_omits_tag_line(self):
        snap = capture_snapshot(_SCHEMA)
        out = format_snapshot_text(snap)
        assert "Tag:" not in out


class TestFormatSnapshotJson:
    def test_valid_json(self, snap):
        out = format_snapshot_json(snap)
        data = json.loads(out)
        assert data["name"] == "staging"

    def test_table_count_field(self, snap):
        data = json.loads(format_snapshot_json(snap))
        assert data["table_count"] == 2

    def test_tables_field_sorted(self, snap):
        data = json.loads(format_snapshot_json(snap))
        assert data["tables"] == ["orders", "users"]


class TestFormatSnapshotMarkdown:
    def test_header_present(self, snap):
        out = format_snapshot_markdown(snap)
        assert "## Snapshot" in out

    def test_table_row_present(self, snap):
        out = format_snapshot_markdown(snap)
        assert "`orders`" in out

    def test_no_tag_shows_dash(self):
        snap = capture_snapshot(_SCHEMA)
        out = format_snapshot_markdown(snap)
        assert "—" in out


class TestFormatSnapshotDispatch:
    def test_default_is_text(self, snap):
        assert format_snapshot(snap) == format_snapshot_text(snap)

    def test_json_dispatch(self, snap):
        assert format_snapshot(snap, fmt="json") == format_snapshot_json(snap)

    def test_markdown_dispatch(self, snap):
        assert format_snapshot(snap, fmt="markdown") == format_snapshot_markdown(snap)


class TestFormatSnapshotListText:
    def test_empty_list_message(self):
        assert "No snapshots" in format_snapshot_list_text([])

    def test_count_shown(self, snap):
        out = format_snapshot_list_text([snap, snap])
        assert "2" in out

    def test_tag_shown_in_list(self, snap):
        out = format_snapshot_list_text([snap])
        assert "rc1" in out
