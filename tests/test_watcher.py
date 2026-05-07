"""Tests for schema_drift.watcher."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from schema_drift.watcher import WatchEvent, _file_hash, watch


# ---------------------------------------------------------------------------
# _file_hash
# ---------------------------------------------------------------------------


def test_file_hash_returns_string_for_existing_file(tmp_path: Path) -> None:
    f = tmp_path / "schema.json"
    f.write_text('{"name": "s"}')
    result = _file_hash(str(f))
    assert isinstance(result, str) and len(result) == 32


def test_file_hash_returns_none_for_missing_file() -> None:
    assert _file_hash("/no/such/file.json") is None


def test_file_hash_changes_when_content_changes(tmp_path: Path) -> None:
    f = tmp_path / "schema.json"
    f.write_text('{"name": "v1"}')
    h1 = _file_hash(str(f))
    f.write_text('{"name": "v2"}')
    h2 = _file_hash(str(f))
    assert h1 != h2


# ---------------------------------------------------------------------------
# WatchEvent
# ---------------------------------------------------------------------------


def test_watch_event_repr() -> None:
    ev = WatchEvent(source_path="a.json", target_path="b.json", source_hash="aaa", target_hash="bbb")
    r = repr(ev)
    assert "a.json" in r
    assert "b.json" in r


def test_watch_event_timestamp_set_automatically() -> None:
    before = time.time()
    ev = WatchEvent(source_path="a", target_path="b", source_hash="", target_hash="")
    after = time.time()
    assert before <= ev.timestamp <= after


# ---------------------------------------------------------------------------
# watch() — functional test with max_events
# ---------------------------------------------------------------------------


def test_watch_fires_callback_on_change(tmp_path: Path) -> None:
    src = tmp_path / "source.json"
    tgt = tmp_path / "target.json"

    src.write_text(json.dumps({"name": "src", "tables": []}))
    tgt.write_text(json.dumps({"name": "tgt", "tables": []}))

    events: list[WatchEvent] = []

    def _modify_and_collect(ev: WatchEvent) -> None:
        events.append(ev)

    import threading

    def _trigger() -> None:
        time.sleep(0.05)
        tgt.write_text(json.dumps({"name": "tgt", "tables": [{"name": "t", "columns": []}]}))

    t = threading.Thread(target=_trigger, daemon=True)
    t.start()

    watch(
        source_path=str(src),
        target_path=str(tgt),
        callback=_modify_and_collect,
        interval=0.02,
        max_events=1,
    )

    assert len(events) == 1
    assert events[0].target_path == str(tgt)
