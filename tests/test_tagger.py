"""Tests for schema_drift.tagger and schema_drift.formatter_tagger."""

import json

import pytest

from schema_drift.comparator import ComparisonResult, DiffType, SchemaDiff
from schema_drift.tagger import TaggedDiff, TaggedResult, tag_result
from schema_drift.formatter_tagger import (
    format_tagged,
    format_tagged_json,
    format_tagged_markdown,
    format_tagged_text,
)


def _make_diff(table: str, diff_type: DiffType = DiffType.TABLE_ADDED) -> SchemaDiff:
    return SchemaDiff(diff_type=diff_type, table_name=table)


@pytest.fixture()
def empty_result() -> ComparisonResult:
    return ComparisonResult(source_name="dev", target_name="prod", diffs=[])


@pytest.fixture()
def mixed_result() -> ComparisonResult:
    return ComparisonResult(
        source_name="dev",
        target_name="prod",
        diffs=[
            _make_diff("users", DiffType.TABLE_ADDED),
            _make_diff("orders", DiffType.TABLE_REMOVED),
            _make_diff("products", DiffType.COLUMN_ADDED),
        ],
    )


# ---------------------------------------------------------------------------
# TaggedDiff
# ---------------------------------------------------------------------------

class TestTaggedDiff:
    def test_has_tag_true(self):
        td = TaggedDiff(diff=_make_diff("users"), tags=["critical", "reviewed"])
        assert td.has_tag("critical") is True

    def test_has_tag_case_insensitive(self):
        td = TaggedDiff(diff=_make_diff("users"), tags=["Critical"])
        assert td.has_tag("critical") is True

    def test_has_tag_false(self):
        td = TaggedDiff(diff=_make_diff("users"), tags=["reviewed"])
        assert td.has_tag("critical") is False


# ---------------------------------------------------------------------------
# tag_result
# ---------------------------------------------------------------------------

class TestTagResult:
    def test_empty_result_returns_empty_tagged(self, empty_result):
        tr = tag_result(empty_result)
        assert tr.tagged_diffs == []

    def test_source_and_target_preserved(self, mixed_result):
        tr = tag_result(mixed_result)
        assert tr.source_name == "dev"
        assert tr.target_name == "prod"

    def test_tags_applied_by_table(self, mixed_result):
        tr = tag_result(mixed_result, tag_map={"users": ["critical"], "orders": ["low"]})
        users_td = next(td for td in tr.tagged_diffs if td.diff.table_name == "users")
        assert users_td.tags == ["critical"]

    def test_untagged_table_has_empty_tags(self, mixed_result):
        tr = tag_result(mixed_result, tag_map={"users": ["critical"]})
        products_td = next(td for td in tr.tagged_diffs if td.diff.table_name == "products")
        assert products_td.tags == []

    def test_filter_by_tag(self, mixed_result):
        tr = tag_result(mixed_result, tag_map={"users": ["critical"], "orders": ["critical"]})
        critical = tr.filter_by_tag("critical")
        assert len(critical) == 2

    def test_all_tags_deduplicated_and_sorted(self, mixed_result):
        tr = tag_result(mixed_result, tag_map={"users": ["critical"], "orders": ["low", "critical"]})
        assert tr.all_tags() == ["critical", "low"]


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

class TestFormatTaggedText:
    def test_no_diffs_message(self, empty_result):
        tr = tag_result(empty_result)
        out = format_tagged_text(tr)
        assert "No diffs found" in out

    def test_header_contains_names(self, mixed_result):
        tr = tag_result(mixed_result)
        out = format_tagged_text(tr)
        assert "dev" in out and "prod" in out

    def test_untagged_label(self, mixed_result):
        tr = tag_result(mixed_result)
        out = format_tagged_text(tr)
        assert "(untagged)" in out

    def test_tag_shown_in_output(self, mixed_result):
        tr = tag_result(mixed_result, tag_map={"users": ["critical"]})
        out = format_tagged_text(tr)
        assert "critical" in out


class TestFormatTaggedJson:
    def test_valid_json(self, mixed_result):
        tr = tag_result(mixed_result)
        data = json.loads(format_tagged_json(tr))
        assert data["source"] == "dev"
        assert len(data["diffs"]) == 3

    def test_all_tags_present(self, mixed_result):
        tr = tag_result(mixed_result, tag_map={"users": ["critical"]})
        data = json.loads(format_tagged_json(tr))
        assert "critical" in data["all_tags"]


class TestFormatTaggedMarkdown:
    def test_table_header_present(self, mixed_result):
        tr = tag_result(mixed_result)
        out = format_tagged_markdown(tr)
        assert "| Table |" in out

    def test_empty_shows_no_diffs(self, empty_result):
        tr = tag_result(empty_result)
        out = format_tagged_markdown(tr)
        assert "No diffs found" in out


class TestFormatTaggedDispatch:
    def test_default_is_text(self, mixed_result):
        tr = tag_result(mixed_result)
        assert format_tagged(tr) == format_tagged_text(tr)

    def test_json_dispatch(self, mixed_result):
        tr = tag_result(mixed_result)
        assert format_tagged(tr, fmt="json") == format_tagged_json(tr)

    def test_markdown_dispatch(self, mixed_result):
        tr = tag_result(mixed_result)
        assert format_tagged(tr, fmt="markdown") == format_tagged_markdown(tr)
