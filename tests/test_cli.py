"""Tests for the schema_drift.cli module."""

import json
import os
import tempfile

import pytest

from schema_drift.cli import main


SAMPLE_SCHEMA_A = {
    "name": "app_db",
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                {"name": "email", "type": "VARCHAR", "max_length": 255, "nullable": False},
            ],
        }
    ],
}

SAMPLE_SCHEMA_B = {
    "name": "app_db",
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                {"name": "email", "type": "VARCHAR", "max_length": 320, "nullable": False},
            ],
        },
        {
            "name": "orders",
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
            ],
        },
    ],
}


@pytest.fixture()
def schema_files(tmp_path):
    source = tmp_path / "source.json"
    target = tmp_path / "target.json"
    source.write_text(json.dumps(SAMPLE_SCHEMA_A))
    target.write_text(json.dumps(SAMPLE_SCHEMA_B))
    return str(source), str(target)


def test_identical_schemas_exit_zero(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(SAMPLE_SCHEMA_A))
    assert main([str(path), str(path)]) == 0


def test_drift_detected_exit_zero_without_flag(schema_files):
    source, target = schema_files
    assert main([source, target]) == 0


def test_drift_detected_exit_one_with_flag(schema_files):
    source, target = schema_files
    assert main([source, target, "--exit-code"]) == 1


def test_missing_source_returns_2(tmp_path, schema_files):
    _, target = schema_files
    assert main(["nonexistent_source.json", target]) == 2


def test_missing_target_returns_2(schema_files):
    source, _ = schema_files
    assert main([source, "nonexistent_target.json"]) == 2


def test_output_file_written(schema_files, tmp_path):
    source, target = schema_files
    out = tmp_path / "report.txt"
    exit_code = main([source, target, "--output", str(out)])
    assert exit_code == 0
    content = out.read_text()
    assert len(content) > 0


def test_report_contains_table_name(schema_files, capsys):
    source, target = schema_files
    main([source, target])
    captured = capsys.readouterr()
    assert "orders" in captured.out
