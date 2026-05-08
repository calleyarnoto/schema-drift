"""Tests for schema_drift.formatter_merger."""

import json
import pytest

from schema_drift.comparator import SchemaDiff, DiffType
from schema_drift.merger import MergedResult
from schema_drift.formatter_merger import (
    format_merged_text,
    format_merged_json,
    format_merged_markdown,
    format_merged,
)


def _diff(diff_type, table, column=None, detail=None):
    return SchemaDiff(
        diff_type=diff_type,
        table_name=table,
        column_name=column,
        detail=detail,
    )


@pytest.fixture
def empty_merged():
    return MergedResult(label="empty", sources=["a", "b"], diffs=[])


@pytest.fixture
def full_merged():
    return MergedResult(
        label="full",
        sources=["staging", "prod"],
        diffs=[
            _diff(DiffType.TABLE_ADDED, "orders"),
            _diff(DiffType.COLUMN_REMOVED, "users", "email", "column dropped"),
        ],
    )


class TestFormatMergedText:
    def test_label_in_output(self, full_merged):
        out = format_merged_text(full_merged)
        assert "full" in out

    def test_sources_listed(self, full_merged):
        out = format_merged_text(full_merged)
        assert "staging" in out
        assert "prod" in out

    def test_diff_count_shown(self, full_merged):
        out = format_merged_text(full_merged)
        assert "2" in out

    def test_no_changes_message(self, empty_merged):
        out = format_merged_text(empty_merged)
        assert "No differences" in out

    def test_diff_type_shown(self, full_merged):
        out = format_merged_text(full_merged)
        assert DiffType.TABLE_ADDED.value in out

    def test_column_name_shown(self, full_merged):
        out = format_merged_text(full_merged)
        assert "email" in out


class TestFormatMergedJson:
    def test_valid_json(self, full_merged):
        out = format_merged_json(full_merged)
        data = json.loads(out)
        assert data["label"] == "full"

    def test_diff_count_in_json(self, full_merged):
        data = json.loads(format_merged_json(full_merged))
        assert data["diff_count"] == 2

    def test_sources_in_json(self, full_merged):
        data = json.loads(format_merged_json(full_merged))
        assert "staging" in data["sources"]

    def test_diffs_list_in_json(self, full_merged):
        data = json.loads(format_merged_json(full_merged))
        assert isinstance(data["diffs"], list)
        assert len(data["diffs"]) == 2


class TestFormatMergedMarkdown:
    def test_header_present(self, full_merged):
        out = format_merged_markdown(full_merged)
        assert "##" in out

    def test_table_header_in_markdown(self, full_merged):
        out = format_merged_markdown(full_merged)
        assert "| Type |" in out

    def test_no_changes_italic_message(self, empty_merged):
        out = format_merged_markdown(empty_merged)
        assert "_No differences" in out


class TestFormatMerged:
    def test_default_is_text(self, full_merged):
        out = format_merged(full_merged)
        assert "==" in out

    def test_json_dispatch(self, full_merged):
        out = format_merged(full_merged, fmt="json")
        data = json.loads(out)
        assert "label" in data

    def test_markdown_dispatch(self, full_merged):
        out = format_merged(full_merged, fmt="markdown")
        assert "##" in out
