"""Tests for schema_drift.merger."""

import pytest

from schema_drift.comparator import ComparisonResult, SchemaDiff, DiffType
from schema_drift.merger import MergedResult, merge_results


def _make_diff(diff_type, table, column=None, detail=None):
    return SchemaDiff(
        diff_type=diff_type,
        table_name=table,
        column_name=column,
        detail=detail,
    )


def _make_result(schema_name, diffs):
    result = ComparisonResult(schema_name=schema_name)
    result.diffs = diffs
    return result


@pytest.fixture
def result_a():
    return _make_result("env_a", [
        _make_diff(DiffType.TABLE_ADDED, "orders"),
        _make_diff(DiffType.COLUMN_REMOVED, "users", "email"),
    ])


@pytest.fixture
def result_b():
    return _make_result("env_b", [
        _make_diff(DiffType.COLUMN_MODIFIED, "users", "name", "type changed"),
    ])


class TestMergeResults:
    def test_label_stored(self, result_a, result_b):
        merged = merge_results([result_a, result_b], label="combined")
        assert merged.label == "combined"

    def test_sources_collected(self, result_a, result_b):
        merged = merge_results([result_a, result_b])
        assert "env_a" in merged.sources
        assert "env_b" in merged.sources

    def test_diffs_combined(self, result_a, result_b):
        merged = merge_results([result_a, result_b])
        assert merged.diff_count == 3

    def test_has_changes_true(self, result_a):
        merged = merge_results([result_a])
        assert merged.has_changes is True

    def test_has_changes_false_for_empty(self):
        empty = _make_result("env_empty", [])
        merged = merge_results([empty])
        assert merged.has_changes is False

    def test_deduplication_removes_exact_duplicates(self):
        diff = _make_diff(DiffType.TABLE_ADDED, "orders")
        r1 = _make_result("a", [diff])
        r2 = _make_result("b", [diff])
        merged = merge_results([r1, r2], deduplicate=True)
        assert merged.diff_count == 1

    def test_no_deduplication_keeps_duplicates(self):
        diff = _make_diff(DiffType.TABLE_ADDED, "orders")
        r1 = _make_result("a", [diff])
        r2 = _make_result("b", [diff])
        merged = merge_results([r1, r2], deduplicate=False)
        assert merged.diff_count == 2

    def test_sources_deduplicated(self):
        r1 = _make_result("env_a", [])
        r2 = _make_result("env_a", [])
        merged = merge_results([r1, r2])
        assert merged.sources.count("env_a") == 1

    def test_empty_list_returns_empty_merged(self):
        merged = merge_results([])
        assert merged.diff_count == 0
        assert merged.sources == []

    def test_default_label(self, result_a):
        merged = merge_results([result_a])
        assert merged.label == "merged"
