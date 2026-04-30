"""Tests for schema comparator and reporter."""

import pytest
from schema_drift.models import Table, Column
from schema_drift.comparator import compare_schemas, DiffType, ComparisonResult
from schema_drift.reporter import generate_text_report


def make_users_table(extra_column: bool = False) -> Table:
    cols = [
        Column(name="id", data_type="INTEGER", nullable=False),
        Column(name="email", data_type="VARCHAR", max_length=255),
    ]
    if extra_column:
        cols.append(Column(name="phone", data_type="VARCHAR", max_length=20))
    return Table(name="users", columns=cols)


def make_orders_table() -> Table:
    return Table(
        name="orders",
        columns=[
            Column(name="id", data_type="INTEGER", nullable=False),
            Column(name="total", data_type="DECIMAL"),
        ],
    )


class TestCompareSchemas:
    def test_identical_schemas_no_diffs(self):
        source = [make_users_table()]
        result = compare_schemas(source, source)
        assert not result.has_changes

    def test_table_added(self):
        source = [make_users_table()]
        target = [make_users_table(), make_orders_table()]
        result = compare_schemas(source, target)
        assert result.has_changes
        added = [d for d in result.diffs if d.diff_type == DiffType.TABLE_ADDED]
        assert len(added) == 1
        assert added[0].table_name == "orders"

    def test_table_removed(self):
        source = [make_users_table(), make_orders_table()]
        target = [make_users_table()]
        result = compare_schemas(source, target)
        removed = [d for d in result.diffs if d.diff_type == DiffType.TABLE_REMOVED]
        assert len(removed) == 1
        assert removed[0].table_name == "orders"

    def test_column_added(self):
        source = [make_users_table(extra_column=False)]
        target = [make_users_table(extra_column=True)]
        result = compare_schemas(source, target)
        added_cols = [d for d in result.diffs if d.diff_type == DiffType.COLUMN_ADDED]
        assert any(d.column_name == "phone" for d in added_cols)

    def test_column_removed(self):
        source = [make_users_table(extra_column=True)]
        target = [make_users_table(extra_column=False)]
        result = compare_schemas(source, target)
        removed_cols = [d for d in result.diffs if d.diff_type == DiffType.COLUMN_REMOVED]
        assert any(d.column_name == "phone" for d in removed_cols)

    def test_column_modified(self):
        source = [Table(name="users", columns=[Column("id", "INTEGER")])]
        target = [Table(name="users", columns=[Column("id", "BIGINT")])]
        result = compare_schemas(source, target)
        modified = [d for d in result.diffs if d.diff_type == DiffType.COLUMN_MODIFIED]
        assert len(modified) == 1
        assert modified[0].column_name == "id"

    def test_summary_no_changes(self):
        result = ComparisonResult()
        assert result.summary == "No schema differences detected."


class TestReporter:
    def test_report_no_changes(self):
        result = compare_schemas([make_users_table()], [make_users_table()])
        report = generate_text_report(result)
        assert "No differences found" in report

    def test_report_contains_table_name(self):
        source = [make_users_table()]
        target = [make_users_table(), make_orders_table()]
        result = compare_schemas(source, target)
        report = generate_text_report(result)
        assert "orders" in report
        assert "+" in report

    def test_report_title_appears(self):
        result = ComparisonResult()
        report = generate_text_report(result, title="My Custom Report")
        assert "My Custom Report" in report
