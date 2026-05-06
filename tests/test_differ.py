"""Tests for schema_drift.differ module."""

import pytest
from schema_drift.models import Column
from schema_drift.differ import ColumnChange, diff_columns, describe_column_diffs


def _col(**kwargs) -> Column:
    defaults = dict(
        name="col",
        data_type="VARCHAR",
        nullable=True,
        default=None,
        max_length=None,
        primary_key=False,
    )
    defaults.update(kwargs)
    return Column(**defaults)


class TestColumnChange:
    def test_repr(self):
        change = ColumnChange("data_type", "INT", "VARCHAR")
        assert "data_type" in repr(change)
        assert "INT" in repr(change)
        assert "VARCHAR" in repr(change)

    def test_to_description_basic(self):
        change = ColumnChange("nullable", True, False)
        desc = change.to_description()
        assert "nullable" in desc
        assert "True" in desc
        assert "False" in desc

    def test_to_description_none_shown_as_null(self):
        change = ColumnChange("default", None, "'active'")
        desc = change.to_description()
        assert "null" in desc
        assert "'active'" in desc


class TestDiffColumns:
    def test_identical_columns_no_changes(self):
        col = _col(name="id", data_type="INT", nullable=False)
        assert diff_columns(col, col) == []

    def test_data_type_change_detected(self):
        old = _col(data_type="INT")
        new = _col(data_type="BIGINT")
        changes = diff_columns(old, new)
        assert len(changes) == 1
        assert changes[0].attribute == "data_type"
        assert changes[0].old_value == "INT"
        assert changes[0].new_value == "BIGINT"

    def test_nullable_change_detected(self):
        old = _col(nullable=True)
        new = _col(nullable=False)
        changes = diff_columns(old, new)
        assert any(c.attribute == "nullable" for c in changes)

    def test_default_change_detected(self):
        old = _col(default=None)
        new = _col(default="0")
        changes = diff_columns(old, new)
        assert any(c.attribute == "default" for c in changes)

    def test_max_length_change_detected(self):
        old = _col(max_length=100)
        new = _col(max_length=255)
        changes = diff_columns(old, new)
        assert any(c.attribute == "max_length" for c in changes)

    def test_primary_key_change_detected(self):
        old = _col(primary_key=False)
        new = _col(primary_key=True)
        changes = diff_columns(old, new)
        assert any(c.attribute == "primary_key" for c in changes)

    def test_multiple_changes_returned(self):
        old = _col(data_type="INT", nullable=True)
        new = _col(data_type="TEXT", nullable=False)
        changes = diff_columns(old, new)
        assert len(changes) == 2


class TestDescribeColumnDiffs:
    def test_returns_strings(self):
        old = _col(data_type="INT")
        new = _col(data_type="BIGINT")
        descriptions = describe_column_diffs(old, new)
        assert all(isinstance(d, str) for d in descriptions)

    def test_empty_when_no_changes(self):
        col = _col()
        assert describe_column_diffs(col, col) == []

    def test_description_contains_attribute(self):
        old = _col(nullable=True)
        new = _col(nullable=False)
        descriptions = describe_column_diffs(old, new)
        assert any("nullable" in d for d in descriptions)
