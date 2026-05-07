"""Tests for schema_drift.annotator and schema_drift.formatter_annotation."""

import json
import pytest

from schema_drift.comparator import ComparisonResult, DiffType, SchemaDiff
from schema_drift.annotator import Annotation, annotate, highest_risk
from schema_drift.formatter_annotation import (
    format_annotation_text,
    format_annotation_json,
    format_annotation_markdown,
    format_annotation,
)


def _make_diff(diff_type, table="users", column=None, detail=None):
    return SchemaDiff(diff_type=diff_type, table_name=table, column_name=column, detail=detail)


@pytest.fixture
def empty_result():
    return ComparisonResult(source_name="s", target_name="t", diffs=[])


@pytest.fixture
def mixed_result():
    return ComparisonResult(
        source_name="s",
        target_name="t",
        diffs=[
            _make_diff(DiffType.TABLE_ADDED, table="orders"),
            _make_diff(DiffType.COLUMN_REMOVED, table="users", column="email"),
            _make_diff(DiffType.COLUMN_MODIFIED, table="users", column="age", detail="type changed"),
        ],
    )


class TestAnnotate:
    def test_empty_result_returns_empty_list(self, empty_result):
        assert annotate(empty_result) == []

    def test_returns_one_annotation_per_diff(self, mixed_result):
        anns = annotate(mixed_result)
        assert len(anns) == 3

    def test_table_added_is_low_risk(self, mixed_result):
        anns = annotate(mixed_result)
        table_added = next(a for a in anns if a.diff.diff_type == DiffType.TABLE_ADDED)
        assert table_added.risk == "low"

    def test_column_removed_is_high_risk(self, mixed_result):
        anns = annotate(mixed_result)
        col_removed = next(a for a in anns if a.diff.diff_type == DiffType.COLUMN_REMOVED)
        assert col_removed.risk == "high"

    def test_column_modified_is_medium_risk(self, mixed_result):
        anns = annotate(mixed_result)
        col_mod = next(a for a in anns if a.diff.diff_type == DiffType.COLUMN_MODIFIED)
        assert col_mod.risk == "medium"

    def test_annotation_repr(self, mixed_result):
        ann = annotate(mixed_result)[0]
        assert "Annotation(" in repr(ann)

    def test_description_contains_table_name(self, mixed_result):
        anns = annotate(mixed_result)
        for ann in anns:
            assert ann.diff.table_name in ann.description


class TestHighestRisk:
    def test_empty_list_returns_low(self):
        assert highest_risk([]) == "low"

    def test_all_low_returns_low(self, mixed_result):
        low_anns = [Annotation(diff=_make_diff(DiffType.TABLE_ADDED), description="x", risk="low")]
        assert highest_risk(low_anns) == "low"

    def test_mixed_returns_high(self, mixed_result):
        anns = annotate(mixed_result)
        assert highest_risk(anns) == "high"


class TestFormatAnnotation:
    def test_text_no_diffs_message(self):
        out = format_annotation_text([])
        assert "No diffs" in out

    def test_text_contains_risk_level(self, mixed_result):
        anns = annotate(mixed_result)
        out = format_annotation_text(anns)
        assert "HIGH" in out

    def test_json_parses_correctly(self, mixed_result):
        anns = annotate(mixed_result)
        data = json.loads(format_annotation_json(anns))
        assert "annotations" in data
        assert len(data["annotations"]) == 3
        assert data["overall_risk"] == "high"

    def test_markdown_contains_table_header(self, mixed_result):
        anns = annotate(mixed_result)
        out = format_annotation_markdown(anns)
        assert "| Risk |" in out

    def test_format_dispatch_json(self, mixed_result):
        anns = annotate(mixed_result)
        out = format_annotation(anns, fmt="json")
        assert out.startswith("{")

    def test_format_dispatch_markdown(self, mixed_result):
        anns = annotate(mixed_result)
        out = format_annotation(anns, fmt="markdown")
        assert "##" in out

    def test_format_dispatch_default_is_text(self, mixed_result):
        anns = annotate(mixed_result)
        assert format_annotation(anns) == format_annotation_text(anns)
