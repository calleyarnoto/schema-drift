"""Default callback handler used by the watch CLI command."""

from __future__ import annotations

import sys
from typing import TextIO

from schema_drift.loader import load_schema_from_json
from schema_drift.comparator import compare_schemas
from schema_drift.formatter import format_result
from schema_drift.watcher import WatchEvent


def make_handler(
    fmt: str = "text",
    out: TextIO = sys.stdout,
    err: TextIO = sys.stderr,
) -> "Callable[[WatchEvent], None]":
    """Return a watch callback that loads, compares, and prints schema diffs.

    Args:
        fmt: Output format – ``"text"``, ``"json"``, or ``"markdown"``.
        out: Stream for normal output.
        err: Stream for error messages.

    Returns:
        A callable suitable for passing to :func:`schema_drift.watcher.watch`.
    """

    def _handler(event: WatchEvent) -> None:
        out.write(
            f"[schema-drift] Change detected — re-comparing schemas…\n"
        )
        try:
            source = load_schema_from_json(event.source_path)
            target = load_schema_from_json(event.target_path)
        except Exception as exc:  # noqa: BLE001
            err.write(f"[schema-drift] ERROR loading schemas: {exc}\n")
            return

        result = compare_schemas(source, target)
        report = format_result(result, fmt=fmt)
        out.write(report)
        out.write("\n")

    return _handler
