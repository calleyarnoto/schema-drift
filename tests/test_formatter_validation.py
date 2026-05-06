"""Tests for schema_drift.formatter_validation."""

import json
import pytest

from schema_drift.validator import ValidationIssue, ValidationReport
from schema_drift.formatter_validation import (
    format_validation_text,
    format_validation_json,
    format_validation_markdown,
    format_validation,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_report():
    return ValidationReport(issues=[])


@pytest.fixture
def mixed_report():
    return ValidationReport(issues=[
        ValidationIssue(severity="error", code="COLUMN_REMOVED", message="Column 'email' removed."),
        ValidationIssue(severity="warning", code="NOT_NULL_ADDED", message="NOT NULL added to 'name'."),
    ])


# ---------------------------------------------------------------------------
# Text format
# ---------------------------------------------------------------------------

class TestFormatValidationText:
    def test_no_issues_message(self, empty_report):
        out = format_validation_text(empty_report)
        assert "No issues found" in out

    def test_header_present(self, mixed_report):
        out = format_validation_text(mixed_report)
        assert "Validation Report" in out

    def test_error_code_shown(self, mixed_report):
        out = format_validation_text(mixed_report)
        assert "COLUMN_REMOVED" in out

    def test_warning_code_shown(self, mixed_report):
        out = format_validation_text(mixed_report)
        assert "NOT_NULL_ADDED" in out

    def test_summary_line_present(self, mixed_report):
        out = format_validation_text(mixed_report)
        assert "1 error(s)" in out
        assert "1 warning(s)" in out


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------

class TestFormatValidationJson:
    def test_valid_json(self, mixed_report):
        out = format_validation_json(mixed_report)
        data = json.loads(out)
        assert "errors" in data
        assert "warnings" in data

    def test_error_count_in_summary(self, mixed_report):
        data = json.loads(format_validation_json(mixed_report))
        assert data["summary"]["total_errors"] == 1

    def test_warning_count_in_summary(self, mixed_report):
        data = json.loads(format_validation_json(mixed_report))
        assert data["summary"]["total_warnings"] == 1

    def test_empty_report_produces_empty_lists(self, empty_report):
        data = json.loads(format_validation_json(empty_report))
        assert data["errors"] == []
        assert data["warnings"] == []


# ---------------------------------------------------------------------------
# Markdown format
# ---------------------------------------------------------------------------

class TestFormatValidationMarkdown:
    def test_no_issues_message(self, empty_report):
        out = format_validation_markdown(empty_report)
        assert "No issues found" in out

    def test_header_uses_markdown(self, mixed_report):
        out = format_validation_markdown(mixed_report)
        assert "## Validation Report" in out

    def test_error_section_heading(self, mixed_report):
        out = format_validation_markdown(mixed_report)
        assert "### Errors" in out

    def test_warning_section_heading(self, mixed_report):
        out = format_validation_markdown(mixed_report)
        assert "### Warnings" in out

    def test_bold_code_in_output(self, mixed_report):
        out = format_validation_markdown(mixed_report)
        assert "**[COLUMN_REMOVED]**" in out


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

class TestFormatValidationDispatch:
    def test_default_is_text(self, mixed_report):
        out = format_validation(mixed_report)
        assert "Validation Report" in out
        assert out == format_validation_text(mixed_report)

    def test_json_dispatch(self, mixed_report):
        out = format_validation(mixed_report, fmt="json")
        json.loads(out)  # must not raise

    def test_markdown_dispatch(self, mixed_report):
        out = format_validation(mixed_report, fmt="markdown")
        assert "##" in out
