"""Tests for schema_drift.changelog."""

import pytest

from schema_drift.comparator import ComparisonResult, DiffType, SchemaDiff
from schema_drift.changelog import (
    ChangelogEntry,
    Changelog,
    build_entry,
    create_changelog,
)


def _make_diff(diff_type: DiffType, table: str, column: str = None) -> SchemaDiff:
    return SchemaDiff(diff_type=diff_type, table_name=table, column_name=column)


@pytest.fixture
def empty_result():
    return ComparisonResult(schema_name="mydb", diffs=[])


@pytest.fixture
def mixed_result():
    return ComparisonResult(
        schema_name="mydb",
        diffs=[
            _make_diff(DiffType.TABLE_ADDED, "orders"),
            _make_diff(DiffType.TABLE_REMOVED, "legacy"),
            _make_diff(DiffType.COLUMN_ADDED, "users", "email"),
            _make_diff(DiffType.COLUMN_TYPE_CHANGED, "users", "age"),
        ],
    )


class TestBuildEntry:
    def test_empty_result_has_zero_diffs(self, empty_result):
        entry = build_entry(empty_result)
        assert entry.total_diffs == 0
        assert entry.added_tables == []
        assert entry.removed_tables == []
        assert entry.modified_tables == []

    def test_added_table_captured(self, mixed_result):
        entry = build_entry(mixed_result)
        assert "orders" in entry.added_tables

    def test_removed_table_captured(self, mixed_result):
        entry = build_entry(mixed_result)
        assert "legacy" in entry.removed_tables

    def test_modified_table_captured(self, mixed_result):
        entry = build_entry(mixed_result)
        assert "users" in entry.modified_tables

    def test_total_diffs_count(self, mixed_result):
        entry = build_entry(mixed_result)
        assert entry.total_diffs == 4

    def test_custom_labels_stored(self, empty_result):
        entry = build_entry(empty_result, source_label="prod", target_label="staging")
        assert entry.source_label == "prod"
        assert entry.target_label == "staging"

    def test_custom_timestamp_stored(self, empty_result):
        entry = build_entry(empty_result, timestamp="2024-01-01T00:00:00Z")
        assert entry.timestamp == "2024-01-01T00:00:00Z"

    def test_auto_timestamp_set_when_none(self, empty_result):
        entry = build_entry(empty_result)
        assert entry.timestamp is not None
        assert "T" in entry.timestamp

    def test_repr_contains_counts(self, mixed_result):
        entry = build_entry(mixed_result)
        r = repr(entry)
        assert "added=1" in r
        assert "removed=1" in r
        assert "modified=1" in r


class TestCreateChangelog:
    def test_schema_name_stored(self, empty_result):
        log = create_changelog("mydb", [empty_result])
        assert log.schema_name == "mydb"

    def test_entry_count_matches_results(self, empty_result, mixed_result):
        log = create_changelog("mydb", [empty_result, mixed_result])
        assert len(log.entries) == 2

    def test_has_entries_false_when_empty(self):
        log = Changelog(schema_name="mydb", entries=[])
        assert log.has_entries() is False

    def test_has_entries_true_when_populated(self, empty_result):
        log = create_changelog("mydb", [empty_result])
        assert log.has_entries() is True

    def test_labels_passed_to_entries(self, empty_result):
        log = create_changelog("mydb", [empty_result], labels=[("prod", "dev")])
        assert log.entries[0].source_label == "prod"
        assert log.entries[0].target_label == "dev"

    def test_repr_shows_entry_count(self, empty_result, mixed_result):
        log = create_changelog("mydb", [empty_result, mixed_result])
        assert "entries=2" in repr(log)
