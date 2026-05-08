"""Tests for schema_drift.archiver and schema_drift.formatter_archiver."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from schema_drift.models import Column, Table
from schema_drift.loader import load_schema_from_dict
from schema_drift.comparator import compare_schemas
from schema_drift.archiver import (
    ArchivedResult,
    archive_result,
    save_archive,
    load_archive,
)
from schema_drift.formatter_archiver import (
    format_archive_text,
    format_archive_json,
    format_archive_markdown,
    format_archive,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SCHEMA_A = {
    "name": "prod",
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "data_type": "integer", "nullable": False},
                {"name": "email", "data_type": "varchar", "nullable": True},
            ],
        }
    ],
}

_SCHEMA_B = {
    "name": "staging",
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "data_type": "integer", "nullable": False},
            ],
        }
    ],
}


def _make_result():
    src = load_schema_from_dict(_SCHEMA_A)
    tgt = load_schema_from_dict(_SCHEMA_B)
    return compare_schemas(src, tgt)


# ---------------------------------------------------------------------------
# archive_result
# ---------------------------------------------------------------------------

class TestArchiveResult:
    def test_label_stored(self):
        entry = archive_result(_make_result(), label="run-1")
        assert entry.label == "run-1"

    def test_source_and_target_names(self):
        entry = archive_result(_make_result(), label="x")
        assert entry.source_name == "prod"
        assert entry.target_name == "staging"

    def test_diff_count_positive(self):
        entry = archive_result(_make_result(), label="x")
        assert entry.diff_count > 0

    def test_created_at_is_set(self):
        entry = archive_result(_make_result(), label="x")
        assert entry.created_at is not None
        assert "T" in entry.created_at  # ISO format

    def test_payload_contains_diffs(self):
        entry = archive_result(_make_result(), label="x")
        assert "diffs" in entry.payload
        assert len(entry.payload["diffs"]) == entry.diff_count


# ---------------------------------------------------------------------------
# save_archive / load_archive
# ---------------------------------------------------------------------------

class TestSaveLoadArchive:
    def test_round_trip_single_entry(self, tmp_path):
        path = str(tmp_path / "archive.jsonl")
        entry = archive_result(_make_result(), label="v1")
        save_archive(entry, path)
        loaded = load_archive(path)
        assert len(loaded) == 1
        assert loaded[0].label == "v1"
        assert loaded[0].diff_count == entry.diff_count

    def test_multiple_entries_appended(self, tmp_path):
        path = str(tmp_path / "archive.jsonl")
        for label in ("a", "b", "c"):
            save_archive(archive_result(_make_result(), label=label), path)
        loaded = load_archive(path)
        assert len(loaded) == 3
        assert [e.label for e in loaded] == ["a", "b", "c"]

    def test_load_missing_file_returns_empty(self, tmp_path):
        result = load_archive(str(tmp_path / "nonexistent.jsonl"))
        assert result == []


# ---------------------------------------------------------------------------
# formatter_archiver
# ---------------------------------------------------------------------------

@pytest.fixture()
def entries():
    return [archive_result(_make_result(), label="run-1"),
            archive_result(_make_result(), label="run-2")]


class TestFormatArchiveText:
    def test_no_entries_message(self):
        out = format_archive_text([])
        assert "No archived" in out

    def test_label_in_output(self, entries):
        out = format_archive_text(entries)
        assert "run-1" in out
        assert "run-2" in out

    def test_source_and_target_shown(self, entries):
        out = format_archive_text(entries)
        assert "prod" in out
        assert "staging" in out


class TestFormatArchiveJson:
    def test_returns_valid_json(self, entries):
        out = format_archive_json(entries)
        parsed = json.loads(out)
        assert isinstance(parsed, list)
        assert len(parsed) == 2

    def test_no_payload_in_json_output(self, entries):
        out = format_archive_json(entries)
        assert "payload" not in out


class TestFormatArchiveMarkdown:
    def test_no_entries_message(self):
        out = format_archive_markdown([])
        assert "No archived" in out

    def test_table_header_present(self, entries):
        out = format_archive_markdown(entries)
        assert "| Label |" in out

    def test_entry_rows_present(self, entries):
        out = format_archive_markdown(entries)
        assert "run-1" in out


class TestFormatArchiveDispatch:
    def test_default_is_text(self, entries):
        assert format_archive(entries) == format_archive_text(entries)

    def test_json_dispatch(self, entries):
        assert format_archive(entries, fmt="json") == format_archive_json(entries)

    def test_markdown_dispatch(self, entries):
        assert format_archive(entries, fmt="markdown") == format_archive_markdown(entries)

    def test_md_alias(self, entries):
        assert format_archive(entries, fmt="md") == format_archive_markdown(entries)
