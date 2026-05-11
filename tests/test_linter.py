"""Tests for schema_drift.linter and schema_drift.formatter_linter."""

import json
import pytest

from schema_drift.comparator import ComparisonResult, SchemaDiff, DiffType
from schema_drift.models import Column
from schema_drift.linter import LintWarning, LintReport, lint_result
from schema_drift.formatter_linter import format_lint, format_lint_text, format_lint_json, format_lint_markdown


def _make_diff(diff_type, table="users", column_name="email", detail=None, column=None):
    return SchemaDiff(
        diff_type=diff_type,
        table_name=table,
        column_name=column_name,
        detail=detail,
        column=column,
    )


def _col(name, nullable=True, col_type="VARCHAR", default=None):
    return Column(name=name, col_type=col_type, nullable=nullable, default=default)


@pytest.fixture
def empty_result():
    return ComparisonResult(schema_name="mydb", diffs=[])


@pytest.fixture
def risky_result():
    diffs = [
        _make_diff(DiffType.COLUMN_ADDED, column=_col("status", nullable=False, default=None)),
        _make_diff(DiffType.COLUMN_MODIFIED, column_name="age", detail="type changed: INT -> TEXT"),
        _make_diff(DiffType.COLUMN_REMOVED, column_name="legacy_id"),
    ]
    return ComparisonResult(schema_name="mydb", diffs=diffs)


class TestLintResult:
    def test_empty_result_no_warnings(self, empty_result):
        report = lint_result(empty_result)
        assert not report.has_warnings
        assert report.warning_count == 0

    def test_schema_name_preserved(self, empty_result):
        report = lint_result(empty_result)
        assert report.schema_name == "mydb"

    def test_nullable_added_triggers_l001(self, risky_result):
        report = lint_result(risky_result)
        codes = [w.code for w in report.warnings]
        assert "L001" in codes

    def test_type_change_triggers_l002(self, risky_result):
        report = lint_result(risky_result)
        codes = [w.code for w in report.warnings]
        assert "L002" in codes

    def test_column_removed_triggers_l003(self, risky_result):
        report = lint_result(risky_result)
        codes = [w.code for w in report.warnings]
        assert "L003" in codes

    def test_nullable_column_with_default_no_l001(self):
        diff = _make_diff(DiffType.COLUMN_ADDED, column=_col("status", nullable=False, default="active"))
        result = ComparisonResult(schema_name="db", diffs=[diff])
        report = lint_result(result)
        assert all(w.code != "L001" for w in report.warnings)

    def test_lint_report_repr(self, risky_result):
        report = lint_result(risky_result)
        assert "LintReport" in repr(report)
        assert "mydb" in repr(report)

    def test_lint_warning_repr(self, risky_result):
        report = lint_result(risky_result)
        assert report.has_warnings
        r = repr(report.warnings[0])
        assert "LintWarning" in r


class TestFormatLint:
    def test_text_no_warnings(self, empty_result):
        report = lint_result(empty_result)
        out = format_lint_text(report)
        assert "No lint warnings" in out
        assert "mydb" in out

    def test_text_shows_warnings(self, risky_result):
        report = lint_result(risky_result)
        out = format_lint_text(report)
        assert "L001" in out or "L002" in out or "L003" in out

    def test_json_is_valid(self, risky_result):
        report = lint_result(risky_result)
        out = format_lint_json(report)
        data = json.loads(out)
        assert data["schema_name"] == "mydb"
        assert isinstance(data["warnings"], list)

    def test_json_warning_count_matches(self, risky_result):
        report = lint_result(risky_result)
        out = format_lint_json(report)
        data = json.loads(out)
        assert data["warning_count"] == report.warning_count

    def test_markdown_contains_table(self, risky_result):
        report = lint_result(risky_result)
        out = format_lint_markdown(report)
        assert "|" in out
        assert "Code" in out

    def test_format_dispatch_json(self, risky_result):
        report = lint_result(risky_result)
        out = format_lint(report, fmt="json")
        json.loads(out)

    def test_format_dispatch_markdown(self, risky_result):
        report = lint_result(risky_result)
        out = format_lint(report, fmt="markdown")
        assert "##" in out

    def test_format_dispatch_default_text(self, risky_result):
        report = lint_result(risky_result)
        out = format_lint(report)
        assert "Lint Report" in out
