"""Tests for schema_drift.watch_handler."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from schema_drift.watch_handler import make_handler
from schema_drift.watcher import WatchEvent


def _write_schema(path: Path, name: str, tables: list) -> None:
    path.write_text(json.dumps({"name": name, "tables": tables}))


@pytest.fixture()
def schema_files(tmp_path: Path):
    src = tmp_path / "source.json"
    tgt = tmp_path / "target.json"
    _write_schema(src, "mydb", [])
    _write_schema(tgt, "mydb", [])
    return src, tgt


def _make_event(src: Path, tgt: Path) -> WatchEvent:
    return WatchEvent(
        source_path=str(src),
        target_path=str(tgt),
        source_hash="aaa",
        target_hash="bbb",
    )


def test_handler_writes_change_notice(schema_files) -> None:
    src, tgt = schema_files
    out = io.StringIO()
    handler = make_handler(fmt="text", out=out)
    handler(_make_event(src, tgt))
    assert "Change detected" in out.getvalue()


def test_handler_outputs_no_drift_message_for_identical(schema_files) -> None:
    src, tgt = schema_files
    out = io.StringIO()
    handler = make_handler(fmt="text", out=out)
    handler(_make_event(src, tgt))
    output = out.getvalue()
    assert "No schema drift detected" in output


def test_handler_reports_drift_when_tables_differ(tmp_path: Path) -> None:
    src = tmp_path / "source.json"
    tgt = tmp_path / "target.json"
    _write_schema(src, "mydb", [])
    _write_schema(
        tgt,
        "mydb",
        [{"name": "users", "columns": [{"name": "id", "type": "integer", "nullable": False}]}],
    )
    out = io.StringIO()
    handler = make_handler(fmt="text", out=out)
    handler(_make_event(src, tgt))
    assert "users" in out.getvalue()


def test_handler_writes_error_on_bad_file(tmp_path: Path) -> None:
    src = tmp_path / "missing_source.json"
    tgt = tmp_path / "missing_target.json"
    out = io.StringIO()
    err = io.StringIO()
    handler = make_handler(fmt="text", out=out, err=err)
    event = WatchEvent(source_path=str(src), target_path=str(tgt), source_hash="", target_hash="")
    handler(event)
    assert "ERROR" in err.getvalue()


def test_handler_json_format(schema_files) -> None:
    src, tgt = schema_files
    out = io.StringIO()
    handler = make_handler(fmt="json", out=out)
    handler(_make_event(src, tgt))
    # Should contain valid JSON somewhere in the output
    output = out.getvalue()
    assert "{" in output
