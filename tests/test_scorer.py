"""Tests for schema_drift.scorer and schema_drift.formatter_score."""

import json
import pytest

from schema_drift.comparator import ComparisonResult, SchemaDiff, DiffType
from schema_drift.scorer import DriftScore, score_result, _severity_label
from schema_drift.formatter_score import (
    format_score_text,
    format_score_json,
    format_score_markdown,
    format_score,
)


def _make_diff(diff_type: DiffType) -> SchemaDiff:
    return SchemaDiff(diff_type=diff_type, table="users", detail="test")


@pytest.fixture
def empty_result():
    return ComparisonResult(schema_name="prod", diffs=[])


@pytest.fixture
def mixed_result():
    return ComparisonResult(
        schema_name="prod",
        diffs=[
            _make_diff(DiffType.TABLE_REMOVED),   # weight 5
            _make_diff(DiffType.COLUMN_ADDED),    # weight 2
            _make_diff(DiffType.COLUMN_REMOVED),  # weight 4
        ],
    )


class TestSeverityLabel:
    def test_zero_is_none(self):
        assert _severity_label(0) == "none"

    def test_low_boundary(self):
        assert _severity_label(5) == "low"

    def test_medium_boundary(self):
        assert _severity_label(15) == "medium"

    def test_high_boundary(self):
        assert _severity_label(30) == "high"

    def test_above_high_is_critical(self):
        assert _severity_label(31) == "critical"


class TestScoreResult:
    def test_empty_result_zero_score(self, empty_result):
        s = score_result(empty_result)
        assert s.total == 0
        assert s.severity == "none"
        assert s.breakdown == {}

    def test_total_matches_weights(self, mixed_result):
        s = score_result(mixed_result)
        assert s.total == 11  # 5 + 2 + 4

    def test_breakdown_keys(self, mixed_result):
        s = score_result(mixed_result)
        assert DiffType.TABLE_REMOVED.value in s.breakdown
        assert DiffType.COLUMN_ADDED.value in s.breakdown

    def test_severity_medium_for_mixed(self, mixed_result):
        s = score_result(mixed_result)
        assert s.severity == "medium"

    def test_repr(self, mixed_result):
        s = score_result(mixed_result)
        assert "DriftScore" in repr(s)
        assert "medium" in repr(s)


class TestFormatScoreText:
    def test_severity_in_output(self, mixed_result):
        s = score_result(mixed_result)
        out = format_score_text(s, schema_name="prod")
        assert "MEDIUM" in out

    def test_schema_name_in_header(self, mixed_result):
        s = score_result(mixed_result)
        out = format_score_text(s, schema_name="prod")
        assert "prod" in out

    def test_no_drift_message(self, empty_result):
        s = score_result(empty_result)
        out = format_score_text(s)
        assert "No drift detected" in out


class TestFormatScoreJson:
    def test_valid_json(self, mixed_result):
        s = score_result(mixed_result)
        out = format_score_json(s, schema_name="prod")
        data = json.loads(out)
        assert data["severity"] == "medium"
        assert data["total"] == 11
        assert data["schema"] == "prod"


class TestFormatScoreMarkdown:
    def test_heading_present(self, mixed_result):
        s = score_result(mixed_result)
        out = format_score_markdown(s, schema_name="staging")
        assert "##" in out
        assert "staging" in out

    def test_table_rendered_for_breakdown(self, mixed_result):
        s = score_result(mixed_result)
        out = format_score_markdown(s)
        assert "|" in out


class TestFormatScoreDispatch:
    def test_default_is_text(self, empty_result):
        s = score_result(empty_result)
        assert format_score(s) == format_score_text(s)

    def test_json_dispatch(self, mixed_result):
        s = score_result(mixed_result)
        assert format_score(s, fmt="json") == format_score_json(s)

    def test_markdown_dispatch(self, mixed_result):
        s = score_result(mixed_result)
        assert format_score(s, fmt="markdown") == format_score_markdown(s)
