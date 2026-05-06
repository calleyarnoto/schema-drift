"""Tests for schema_drift.summarizer."""

import pytest

from schema_drift.comparator import ComparisonResult, DiffType, SchemaDiff
from schema_drift.summarizer import SchemaSummary, summarize


def _make_diff(diff_type: DiffType, table: str = "users", column: str = None) -> SchemaDiff:
    return SchemaDiff(
        diff_type=diff_type,
        table_name=table,
        column_name=column,
        detail=f"{diff_type.value} on {table}",
    )


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
            _make_diff(DiffType.COLUMN_REMOVED, "users", "phone"),
            _make_diff(DiffType.COLUMN_TYPE_CHANGED, "products", "price"),
        ],
    )


class TestSummarize:
    def test_empty_result_no_changes(self, empty_result):
        summary = summarize(empty_result)
        assert not summary.has_changes
        assert summary.total_diffs == 0

    def test_schema_name_preserved(self, empty_result):
        summary = summarize(empty_result)
        assert summary.schema_name == "mydb"

    def test_total_diffs_count(self, mixed_result):
        summary = summarize(mixed_result)
        assert summary.total_diffs == 5

    def test_tables_added_count(self, mixed_result):
        summary = summarize(mixed_result)
        assert summary.tables_added == 1

    def test_tables_removed_count(self, mixed_result):
        summary = summarize(mixed_result)
        assert summary.tables_removed == 1

    def test_tables_modified_count(self, mixed_result):
        summary = summarize(mixed_result)
        # users (column_added + column_removed) and products (type_changed)
        assert summary.tables_modified == 2

    def test_affected_tables_sorted(self, mixed_result):
        summary = summarize(mixed_result)
        assert summary.affected_tables == sorted(summary.affected_tables)

    def test_affected_tables_contains_all(self, mixed_result):
        summary = summarize(mixed_result)
        assert set(summary.affected_tables) == {"orders", "legacy", "users", "products"}

    def test_diffs_by_type_keys(self, mixed_result):
        summary = summarize(mixed_result)
        assert DiffType.TABLE_ADDED.value in summary.diffs_by_type
        assert DiffType.COLUMN_ADDED.value in summary.diffs_by_type

    def test_diffs_by_type_counts(self, mixed_result):
        summary = summarize(mixed_result)
        assert summary.diffs_by_type[DiffType.COLUMN_ADDED.value] == 1
        assert summary.diffs_by_type[DiffType.COLUMN_REMOVED.value] == 1

    def test_repr(self, mixed_result):
        summary = summarize(mixed_result)
        assert "SchemaSummary" in repr(summary)
        assert "mydb" in repr(summary)
