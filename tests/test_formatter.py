"""Tests for schema_drift.formatter module."""

import json
import pytest
from schema_drift.models import Column, Table
from schema_drift.comparator import compare_schemas, DiffType
from schema_drift.formatter import format_text, format_json, format_markdown, format_result


@pytest.fixture()
def identical_result():
    col = Column(name="id", data_type="integer")
    table = Table(name="users", columns=[col])
    return compare_schemas({"users": table}, {"users": table}, schema_name="mydb")


@pytest.fixture()
def drift_result():
    source_col = Column(name="id", data_type="integer")
    target_col = Column(name="id", data_type="bigint")
    source_extra = Column(name="email", data_type="varchar")
    source_table = Table(name="users", columns=[source_col, source_extra])
    target_table = Table(name="users", columns=[target_col])
    new_table = Table(name="orders", columns=[Column(name="order_id", data_type="integer")])
    return compare_schemas(
        {"users": source_table},
        {"users": target_table, "orders": new_table},
        schema_name="mydb",
    )


class TestFormatText:
    def test_no_changes_message(self, identical_result):
        output = format_text(identical_result)
        assert "No differences found" in output

    def test_schema_name_in_header(self, drift_result):
        output = format_text(drift_result)
        assert "mydb" in output

    def test_added_table_prefix(self, drift_result):
        output = format_text(drift_result)
        assert "[+]" in output

    def test_removed_column_prefix(self, drift_result):
        output = format_text(drift_result)
        assert "[-]" in output

    def test_total_changes_shown(self, drift_result):
        output = format_text(drift_result)
        assert "Total changes" in output


class TestFormatJson:
    def test_valid_json(self, drift_result):
        output = format_json(drift_result)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_has_changes_true(self, drift_result):
        parsed = json.loads(format_json(drift_result))
        assert parsed["has_changes"] is True

    def test_no_changes_false(self, identical_result):
        parsed = json.loads(format_json(identical_result))
        assert parsed["has_changes"] is False

    def test_diffs_list_present(self, drift_result):
        parsed = json.loads(format_json(drift_result))
        assert isinstance(parsed["diffs"], list)
        assert len(parsed["diffs"]) > 0

    def test_diff_entry_fields(self, drift_result):
        parsed = json.loads(format_json(drift_result))
        entry = parsed["diffs"][0]
        assert "diff_type" in entry
        assert "table" in entry


class TestFormatMarkdown:
    def test_header_present(self, drift_result):
        output = format_markdown(drift_result)
        assert output.startswith("# Schema Drift Report")

    def test_table_row_format(self, drift_result):
        output = format_markdown(drift_result)
        assert "|" in output

    def test_no_changes_message(self, identical_result):
        output = format_markdown(identical_result)
        assert "No differences found" in output


class TestFormatResult:
    def test_dispatches_text(self, drift_result):
        out = format_result(drift_result, fmt="text")
        assert "Total changes" in out

    def test_dispatches_json(self, drift_result):
        out = format_result(drift_result, fmt="json")
        json.loads(out)  # should not raise

    def test_dispatches_markdown(self, drift_result):
        out = format_result(drift_result, fmt="markdown")
        assert out.startswith("#")

    def test_unknown_format_raises(self, drift_result):
        with pytest.raises(ValueError, match="Unknown format"):
            format_result(drift_result, fmt="xml")
