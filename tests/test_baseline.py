"""Tests for schema_drift.baseline module."""

import json
import os
import tempfile

import pytest

from schema_drift.baseline import (
    Baseline,
    baseline_exists,
    create_baseline,
    load_baseline,
    save_baseline,
)
from schema_drift.models import Column, Table


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_tables() -> dict:
    col_id = Column(name="id", data_type="INTEGER", nullable=False)
    col_name = Column(name="name", data_type="VARCHAR", nullable=True, max_length=100)
    users = Table(name="users", columns={"id": col_id, "name": col_name})
    return {"users": users}


# ---------------------------------------------------------------------------
# create_baseline
# ---------------------------------------------------------------------------

class TestCreateBaseline:
    def test_name_stored(self):
        b = create_baseline(_make_tables(), name="prod")
        assert b.name == "prod"

    def test_tables_stored(self):
        tables = _make_tables()
        b = create_baseline(tables, name="prod")
        assert "users" in b.tables

    def test_created_at_set(self):
        b = create_baseline(_make_tables(), name="prod")
        assert b.created_at != ""

    def test_description_defaults_empty(self):
        b = create_baseline(_make_tables(), name="prod")
        assert b.description == ""

    def test_description_stored(self):
        b = create_baseline(_make_tables(), name="prod", description="snapshot")
        assert b.description == "snapshot"

    def test_repr_contains_name(self):
        b = create_baseline(_make_tables(), name="staging")
        assert "staging" in repr(b)


# ---------------------------------------------------------------------------
# save_baseline / load_baseline round-trip
# ---------------------------------------------------------------------------

class TestSaveLoadBaseline:
    def test_round_trip_name(self, tmp_path):
        path = str(tmp_path / "baseline.json")
        b = create_baseline(_make_tables(), name="prod", description="test snap")
        save_baseline(b, path)
        loaded = load_baseline(path)
        assert loaded.name == "prod"

    def test_round_trip_description(self, tmp_path):
        path = str(tmp_path / "baseline.json")
        b = create_baseline(_make_tables(), name="prod", description="my desc")
        save_baseline(b, path)
        loaded = load_baseline(path)
        assert loaded.description == "my desc"

    def test_round_trip_tables(self, tmp_path):
        path = str(tmp_path / "baseline.json")
        b = create_baseline(_make_tables(), name="prod")
        save_baseline(b, path)
        loaded = load_baseline(path)
        assert "users" in loaded.tables

    def test_round_trip_columns(self, tmp_path):
        path = str(tmp_path / "baseline.json")
        b = create_baseline(_make_tables(), name="prod")
        save_baseline(b, path)
        loaded = load_baseline(path)
        assert "id" in loaded.tables["users"].columns

    def test_file_is_valid_json(self, tmp_path):
        path = str(tmp_path / "baseline.json")
        b = create_baseline(_make_tables(), name="prod")
        save_baseline(b, path)
        with open(path) as fh:
            data = json.load(fh)
        assert "name" in data
        assert "schema" in data


# ---------------------------------------------------------------------------
# baseline_exists
# ---------------------------------------------------------------------------

class TestBaselineExists:
    def test_returns_true_when_file_present(self, tmp_path):
        path = str(tmp_path / "bl.json")
        b = create_baseline(_make_tables(), name="x")
        save_baseline(b, path)
        assert baseline_exists(path) is True

    def test_returns_false_when_missing(self, tmp_path):
        path = str(tmp_path / "nope.json")
        assert baseline_exists(path) is False
