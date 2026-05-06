"""Tests for schema_drift.patcher.generate_patch_sql."""

import pytest
from schema_drift.models import Column, Table
from schema_drift.comparator import compare_schemas, DiffType
from schema_drift.patcher import generate_patch_sql


def _col(name, dtype="varchar", max_length=None, nullable=True, default=None):
    return Column(name=name, data_type=dtype, max_length=max_length,
                  nullable=nullable, default=default)


def _table(name, cols):
    return Table(name=name, columns=cols)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def users_table():
    return _table("users", [_col("id", "integer"), _col("email", "varchar", 255)])


@pytest.fixture()
def orders_table():
    return _table("orders", [_col("id", "integer"), _col("total", "numeric")])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGeneratePatchSQL:

    def test_no_diffs_returns_empty(self, users_table):
        result = compare_schemas(
            {"name": "s", "tables": [users_table]},
            {"name": "s", "tables": [users_table]},
        )
        assert generate_patch_sql(result) == []

    def test_table_added_creates_table(self, users_table, orders_table):
        result = compare_schemas(
            {"name": "s", "tables": [users_table]},
            {"name": "s", "tables": [users_table, orders_table]},
        )
        sql = generate_patch_sql(result)
        assert any("CREATE TABLE" in s and '"orders"' in s for s in sql)

    def test_table_removed_drops_table(self, users_table, orders_table):
        result = compare_schemas(
            {"name": "s", "tables": [users_table, orders_table]},
            {"name": "s", "tables": [users_table]},
        )
        sql = generate_patch_sql(result)
        assert any("DROP TABLE" in s and '"orders"' in s for s in sql)

    def test_column_added_alters_table(self, users_table):
        target = _table("users", [_col("id", "integer"), _col("email", "varchar", 255),
                                   _col("created_at", "timestamp")])
        result = compare_schemas(
            {"name": "s", "tables": [users_table]},
            {"name": "s", "tables": [target]},
        )
        sql = generate_patch_sql(result)
        assert any("ADD COLUMN" in s and '"created_at"' in s for s in sql)

    def test_column_removed_drops_column(self, users_table):
        target = _table("users", [_col("id", "integer")])
        result = compare_schemas(
            {"name": "s", "tables": [users_table]},
            {"name": "s", "tables": [target]},
        )
        sql = generate_patch_sql(result)
        assert any("DROP COLUMN" in s and '"email"' in s for s in sql)

    def test_column_modified_alters_type(self, users_table):
        target = _table("users", [_col("id", "integer"),
                                   _col("email", "text")])
        result = compare_schemas(
            {"name": "s", "tables": [users_table]},
            {"name": "s", "tables": [target]},
        )
        sql = generate_patch_sql(result)
        assert any("ALTER COLUMN" in s and '"email"' in s for s in sql)

    def test_create_table_includes_column_types(self, orders_table):
        result = compare_schemas(
            {"name": "s", "tables": []},
            {"name": "s", "tables": [orders_table]},
        )
        sql = generate_patch_sql(result)
        create = next(s for s in sql if "CREATE TABLE" in s)
        assert "INTEGER" in create or "NUMERIC" in create
