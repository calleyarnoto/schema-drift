"""Tests for schema_drift.exporter."""

import json
import os
import tempfile
import pytest

from schema_drift.comparator import ComparisonResult, SchemaDiff, DiffType
from schema_drift.exporter import export_result, _get_format_from_extension


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(has_diffs: bool = False) -> ComparisonResult:
    diffs = []
    if has_diffs:
        diffs = [SchemaDiff(diff_type=DiffType.TABLE_ADDED, table_name="orders")]
    return ComparisonResult(schema_name="mydb", diffs=diffs)


# ---------------------------------------------------------------------------
# _get_format_from_extension
# ---------------------------------------------------------------------------

class TestGetFormatFromExtension:
    def test_txt_extension(self):
        assert _get_format_from_extension("report.txt") == "text"

    def test_json_extension(self):
        assert _get_format_from_extension("/tmp/out.json") == "json"

    def test_md_extension(self):
        assert _get_format_from_extension("diff.md") == "markdown"

    def test_markdown_extension(self):
        assert _get_format_from_extension("diff.markdown") == "markdown"

    def test_unknown_extension_returns_none(self):
        assert _get_format_from_extension("report.csv") is None


# ---------------------------------------------------------------------------
# export_result
# ---------------------------------------------------------------------------

class TestExportResult:
    def test_export_text_by_extension(self, tmp_path):
        out = tmp_path / "report.txt"
        fmt = export_result(_make_result(), str(out))
        assert fmt == "text"
        assert out.exists()
        assert "mydb" in out.read_text()

    def test_export_json_by_extension(self, tmp_path):
        out = tmp_path / "report.json"
        export_result(_make_result(has_diffs=True), str(out))
        data = json.loads(out.read_text())
        assert data["schema_name"] == "mydb"
        assert len(data["diffs"]) == 1

    def test_export_markdown_by_extension(self, tmp_path):
        out = tmp_path / "report.md"
        fmt = export_result(_make_result(has_diffs=True), str(out))
        assert fmt == "markdown"
        content = out.read_text()
        assert "#" in content

    def test_explicit_format_overrides_extension(self, tmp_path):
        out = tmp_path / "report.txt"
        fmt = export_result(_make_result(), str(out), fmt="markdown")
        assert fmt == "markdown"
        assert "#" in out.read_text()

    def test_unknown_extension_without_fmt_raises(self, tmp_path):
        out = tmp_path / "report.csv"
        with pytest.raises(ValueError, match="Cannot infer"):
            export_result(_make_result(), str(out))

    def test_unsupported_fmt_raises(self, tmp_path):
        out = tmp_path / "report.txt"
        with pytest.raises(ValueError, match="Unsupported format"):
            export_result(_make_result(), str(out), fmt="xml")

    def test_creates_parent_directories(self, tmp_path):
        out = tmp_path / "nested" / "deep" / "report.txt"
        export_result(_make_result(), str(out))
        assert out.exists()
