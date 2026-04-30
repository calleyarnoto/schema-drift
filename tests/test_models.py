"""Unit tests for schema_drift.models."""

import pytest
from schema_drift.models import Column, Table, Schema


class TestColumn:
    def test_basic_column_repr(self):
        col = Column(name="id", data_type="INTEGER", nullable=False)
        assert "id" in repr(col)
        assert "INTEGER" in repr(col)
        assert "NOT NULL" in repr(col)

    def test_column_with_max_length(self):
        col = Column(name="username", data_type="VARCHAR", max_length=255)
        assert "(255)" in repr(col)

    def test_column_with_default(self):
        col = Column(name="active", data_type="BOOLEAN", default="true")
        assert "DEFAULT true" in repr(col)

    def test_column_equality(self):
        col1 = Column(name="age", data_type="INTEGER", nullable=True)
        col2 = Column(name="age", data_type="INTEGER", nullable=True)
        assert col1 == col2

    def test_column_inequality_different_type(self):
        col1 = Column(name="age", data_type="INTEGER")
        col2 = Column(name="age", data_type="BIGINT")
        assert col1 != col2

    def test_column_inequality_different_nullable(self):
        col1 = Column(name="age", data_type="INTEGER", nullable=True)
        col2 = Column(name="age", data_type="INTEGER", nullable=False)
        assert col1 != col2


class TestTable:
    def setup_method(self):
        self.table = Table(
            name="users",
            columns=[
                Column(name="id", data_type="INTEGER", nullable=False),
                Column(name="email", data_type="VARCHAR", max_length=320),
            ],
        )

    def test_get_existing_column(self):
        col = self.table.get_column("id")
        assert col is not None
        assert col.name == "id"

    def test_get_missing_column_returns_none(self):
        assert self.table.get_column("nonexistent") is None

    def test_column_names_property(self):
        assert self.table.column_names == {"id", "email"}


class TestSchema:
    def setup_method(self):
        self.schema = Schema(
            name="public",
            tables=[
                Table(name="users"),
                Table(name="orders"),
            ],
        )

    def test_get_existing_table(self):
        table = self.schema.get_table("users")
        assert table is not None
        assert table.name == "users"

    def test_get_missing_table_returns_none(self):
        assert self.schema.get_table("nonexistent") is None

    def test_table_names_property(self):
        assert self.schema.table_names == {"users", "orders"}
