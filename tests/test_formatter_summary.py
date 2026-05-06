"""Tests for schema_drift.formatter_summary."""

import json

import pytest

from schema_drift.summarizer import SchemaSummary
from schema_drift.formatter_summary import (
    format_summary,
    format_summary_json,
    format_summary_markdown,
    format_summary_text,
)


@pytest.fixture
def summary():
    return SchemaSummary(
        schema_name="testdb",
        total_tables=5,
        tables_added=1,
        tables_removed=0,
        tables_modified=2,
        total_diffs=4,
        diffs_by_type={"column_added": 2, "table_added": 1, "column_type_changed": 1},
        affected_tables=["orders", "products", "users"],
    )


class TestFormatSummaryText:
    def test_schema_name_in_output(self, summary):
        out = format_summary_text(summary)
        assert "testdb" in out

    def test_total_diffs_shown(self, summary):
        out = format_summary_text(summary)
        assert "4" in out

    def test_affected_tables_listed(self, summary):
        out = format_summary_text(summary)
        assert "orders" in out
        assert "users" in out

    def test_diffs_by_type_shown(self, summary):
        out = format_summary_text(summary)
        assert "column_added" in out


class TestFormatSummaryJson:
    def test_valid_json(self, summary):
        out = format_summary_json(summary)
        data = json.loads(out)
        assert isinstance(data, dict)

    def test_schema_name_field(self, summary):
        data = json.loads(format_summary_json(summary))
        assert data["schema_name"] == "testdb"

    def test_affected_tables_field(self, summary):
        data = json.loads(format_summary_json(summary))
        assert "orders" in data["affected_tables"]

    def test_diffs_by_type_field(self, summary):
        data = json.loads(format_summary_json(summary))
        assert data["diffs_by_type"]["column_added"] == 2


class TestFormatSummaryMarkdown:
    def test_heading_present(self, summary):
        out = format_summary_markdown(summary)
        assert "## Schema Summary" in out

    def test_table_syntax(self, summary):
        out = format_summary_markdown(summary)
        assert "|" in out

    def test_affected_tables_listed(self, summary):
        out = format_summary_markdown(summary)
        assert "`orders`" in out


class TestFormatSummaryDispatch:
    def test_text_format(self, summary):
        out = format_summary(summary, fmt="text")
        assert "testdb" in out

    def test_json_format(self, summary):
        out = format_summary(summary, fmt="json")
        assert json.loads(out)["schema_name"] == "testdb"

    def test_markdown_format(self, summary):
        out = format_summary(summary, fmt="markdown")
        assert "##" in out

    def test_unknown_format_raises(self, summary):
        with pytest.raises(ValueError, match="Unknown format"):
            format_summary(summary, fmt="xml")
