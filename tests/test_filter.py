"""Tests for schema_drift.filter module."""

import pytest
from schema_drift.comparator import ComparisonResult, SchemaDiff, DiffType
from schema_drift.filter import (
    filter_by_diff_type,
    filter_by_table,
    filter_by_tables,
    exclude_tables,
)


@pytest.fixture
def sample_result():
    diffs = [
        SchemaDiff(diff_type=DiffType.TABLE_ADDED, table_name="orders"),
        SchemaDiff(diff_type=DiffType.TABLE_REMOVED, table_name="legacy"),
        SchemaDiff(diff_type=DiffType.COLUMN_ADDED, table_name="users", column_name="email"),
        SchemaDiff(diff_type=DiffType.COLUMN_REMOVED, table_name="users", column_name="phone"),
        SchemaDiff(diff_type=DiffType.COLUMN_MODIFIED, table_name="orders", column_name="total"),
    ]
    return ComparisonResult(source_schema="dev", target_schema="prod", diffs=diffs)


class TestFilterByDiffType:
    def test_filter_single_type(self, sample_result):
        result = filter_by_diff_type(sample_result, [DiffType.TABLE_ADDED])
        assert len(result.diffs) == 1
        assert result.diffs[0].diff_type == DiffType.TABLE_ADDED

    def test_filter_multiple_types(self, sample_result):
        result = filter_by_diff_type(
            sample_result, [DiffType.COLUMN_ADDED, DiffType.COLUMN_REMOVED]
        )
        assert len(result.diffs) == 2
        types = {d.diff_type for d in result.diffs}
        assert types == {DiffType.COLUMN_ADDED, DiffType.COLUMN_REMOVED}

    def test_filter_no_match_returns_empty(self, sample_result):
        result = filter_by_diff_type(sample_result, [DiffType.TABLE_MODIFIED])
        assert result.diffs == []
        assert not result.has_changes()

    def test_preserves_schema_names(self, sample_result):
        result = filter_by_diff_type(sample_result, [DiffType.TABLE_ADDED])
        assert result.source_schema == "dev"
        assert result.target_schema == "prod"


class TestFilterByTable:
    def test_filter_single_table(self, sample_result):
        result = filter_by_table(sample_result, "users")
        assert len(result.diffs) == 2
        assert all(d.table_name == "users" for d in result.diffs)

    def test_filter_nonexistent_table(self, sample_result):
        result = filter_by_table(sample_result, "nonexistent")
        assert result.diffs == []

    def test_filter_by_tables_multiple(self, sample_result):
        result = filter_by_tables(sample_result, ["users", "legacy"])
        assert len(result.diffs) == 3
        table_names = {d.table_name for d in result.diffs}
        assert table_names == {"users", "legacy"}

    def test_filter_by_empty_list(self, sample_result):
        result = filter_by_tables(sample_result, [])
        assert result.diffs == []


class TestExcludeTables:
    def test_exclude_single_table(self, sample_result):
        result = exclude_tables(sample_result, ["users"])
        assert all(d.table_name != "users" for d in result.diffs)
        assert len(result.diffs) == 3

    def test_exclude_multiple_tables(self, sample_result):
        result = exclude_tables(sample_result, ["users", "orders"])
        assert len(result.diffs) == 1
        assert result.diffs[0].table_name == "legacy"

    def test_exclude_nonexistent_table(self, sample_result):
        result = exclude_tables(sample_result, ["nonexistent"])
        assert len(result.diffs) == len(sample_result.diffs)
