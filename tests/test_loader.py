"""Tests for schema_drift.loader module."""

import json
import pytest
from pathlib import Path

from schema_drift.loader import load_schema_from_dict, load_schema_from_json, schema_to_dict


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_schema.json"


class TestLoadSchemaFromDict:
    def test_schema_name(self, sample_dict):
        schema = load_schema_from_dict(sample_dict)
        assert schema.name == "test_db"

    def test_tables_loaded(self, sample_dict):
        schema = load_schema_from_dict(sample_dict)
        assert "users" in schema.tables
        assert len(schema.tables) == 1

    def test_columns_loaded(self, sample_dict):
        schema = load_schema_from_dict(sample_dict)
        table = schema.tables["users"]
        assert len(table.columns) == 2

    def test_column_attributes(self, sample_dict):
        schema = load_schema_from_dict(sample_dict)
        col = schema.tables["users"].get_column("id")
        assert col.data_type == "INTEGER"
        assert col.primary_key is True
        assert col.nullable is False

    def test_column_defaults(self, sample_dict):
        schema = load_schema_from_dict(sample_dict)
        col = schema.tables["users"].get_column("email")
        assert col.max_length == 255
        assert col.default is None

    def test_empty_schema(self):
        schema = load_schema_from_dict({"name": "empty", "tables": {}})
        assert schema.name == "empty"
        assert schema.tables == {}

    def test_missing_name_defaults(self):
        schema = load_schema_from_dict({"tables": {}})
        assert schema.name == "unnamed"


class TestLoadSchemaFromJson:
    def test_load_from_file(self):
        schema = load_schema_from_json(FIXTURE_PATH)
        assert schema.name == "production"
        assert "users" in schema.tables
        assert "orders" in schema.tables

    def test_load_from_json_string(self, sample_dict):
        json_str = json.dumps(sample_dict)
        schema = load_schema_from_json(json_str)
        assert schema.name == "test_db"


class TestSchemaToDict:
    def test_roundtrip(self, sample_dict):
        schema = load_schema_from_dict(sample_dict)
        result = schema_to_dict(schema)
        assert result["name"] == sample_dict["name"]
        assert "users" in result["tables"]
        cols = result["tables"]["users"]["columns"]
        assert any(c["name"] == "id" for c in cols)


@pytest.fixture
def sample_dict():
    return {
        "name": "test_db",
        "tables": {
            "users": {
                "columns": [
                    {"name": "id", "data_type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "email", "data_type": "VARCHAR", "nullable": False, "max_length": 255},
                ]
            }
        },
    }
