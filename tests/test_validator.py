"""Tests for schema_drift.validator."""

import pytest

from schema_drift.models import Column, Table
from schema_drift.comparator import ComparisonResult, SchemaDiff, DiffType
from schema_drift.validator import (
    ValidationIssue,
    ValidationReport,
    validate_table,
    validate_result,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _col(name, col_type="VARCHAR", nullable=True, primary_key=False):
    return Column(name=name, col_type=col_type, nullable=nullable, primary_key=primary_key)


def _diff(diff_type, table_name="users", column_name=None, old_value=None, new_value=None):
    return SchemaDiff(
        diff_type=diff_type,
        table_name=table_name,
        column_name=column_name,
        old_value=old_value,
        new_value=new_value,
    )


# ---------------------------------------------------------------------------
# ValidationIssue / ValidationReport
# ---------------------------------------------------------------------------

class TestValidationReport:
    def test_has_errors_true(self):
        report = ValidationReport(issues=[
            ValidationIssue(severity="error", code="X", message="m"),
        ])
        assert report.has_errors is True

    def test_has_errors_false_when_only_warnings(self):
        report = ValidationReport(issues=[
            ValidationIssue(severity="warning", code="X", message="m"),
        ])
        assert report.has_errors is False

    def test_errors_and_warnings_split(self):
        report = ValidationReport(issues=[
            ValidationIssue(severity="error", code="E", message="e"),
            ValidationIssue(severity="warning", code="W", message="w"),
        ])
        assert len(report.errors) == 1
        assert len(report.warnings) == 1

    def test_repr_contains_counts(self):
        report = ValidationReport(issues=[
            ValidationIssue(severity="error", code="E", message="e"),
        ])
        assert "errors=1" in repr(report)
        assert "warnings=0" in repr(report)


# ---------------------------------------------------------------------------
# validate_table
# ---------------------------------------------------------------------------

class TestValidateTable:
    def test_empty_table_returns_error(self):
        table = Table(name="empty", columns=[])
        issues = validate_table(table)
        codes = [i.code for i in issues]
        assert "EMPTY_TABLE" in codes

    def test_no_primary_key_returns_warning(self):
        table = Table(name="t", columns=[_col("id")])
        issues = validate_table(table)
        codes = [i.code for i in issues]
        assert "NO_PRIMARY_KEY" in codes

    def test_valid_table_no_issues(self):
        table = Table(name="t", columns=[_col("id", primary_key=True), _col("name")])
        issues = validate_table(table)
        assert issues == []

    def test_duplicate_column_returns_error(self):
        table = Table(name="t", columns=[
            _col("id", primary_key=True),
            _col("name"),
            _col("name"),
        ])
        issues = validate_table(table)
        codes = [i.code for i in issues]
        assert "DUPLICATE_COLUMN" in codes


# ---------------------------------------------------------------------------
# validate_result
# ---------------------------------------------------------------------------

class TestValidateResult:
    def _result(self, diffs):
        return ComparisonResult(schema_name="test", diffs=diffs)

    def test_no_diffs_returns_empty_report(self):
        report = validate_result(self._result([]))
        assert not report.has_errors
        assert not report.has_warnings

    def test_column_type_changed_is_error(self):
        report = validate_result(self._result([
            _diff(DiffType.COLUMN_TYPE_CHANGED, column_name="age",
                  old_value="INT", new_value="VARCHAR"),
        ]))
        assert report.has_errors
        assert any(i.code == "DESTRUCTIVE_TYPE_CHANGE" for i in report.errors)

    def test_column_removed_is_error(self):
        report = validate_result(self._result([
            _diff(DiffType.COLUMN_REMOVED, column_name="email"),
        ]))
        assert any(i.code == "COLUMN_REMOVED" for i in report.errors)

    def test_table_removed_is_error(self):
        report = validate_result(self._result([
            _diff(DiffType.TABLE_REMOVED),
        ]))
        assert any(i.code == "TABLE_REMOVED" for i in report.errors)

    def test_nullable_changed_to_false_is_warning(self):
        report = validate_result(self._result([
            _diff(DiffType.NULLABLE_CHANGED, column_name="name",
                  old_value=True, new_value=False),
        ]))
        assert report.has_warnings
        assert any(i.code == "NOT_NULL_ADDED" for i in report.warnings)

    def test_nullable_changed_to_true_no_warning(self):
        report = validate_result(self._result([
            _diff(DiffType.NULLABLE_CHANGED, column_name="name",
                  old_value=False, new_value=True),
        ]))
        assert not report.has_warnings
