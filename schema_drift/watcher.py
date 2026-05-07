"""Watch schema files for changes and trigger comparison automatically."""

from __future__ import annotations

import time
import hashlib
import os
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class WatchEvent:
    """Represents a detected change event between two schema files."""

    source_path: str
    target_path: str
    source_hash: str
    target_hash: str
    timestamp: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        return (
            f"WatchEvent(source={self.source_path!r}, "
            f"target={self.target_path!r}, "
            f"ts={self.timestamp:.2f})"
        )


def _file_hash(path: str) -> Optional[str]:
    """Return the MD5 hex digest of a file, or None if unreadable."""
    try:
        with open(path, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()
    except OSError:
        return None


def watch(
    source_path: str,
    target_path: str,
    callback: Callable[[WatchEvent], None],
    interval: float = 2.0,
    max_events: Optional[int] = None,
) -> None:
    """Poll source and target schema files and invoke *callback* on change.

    Args:
        source_path: Path to the source schema JSON file.
        target_path: Path to the target schema JSON file.
        callback: Called with a :class:`WatchEvent` whenever either file changes.
        interval: Polling interval in seconds.
        max_events: Stop after this many events (useful for testing / CI).
    """
    last_source = _file_hash(source_path)
    last_target = _file_hash(target_path)
    events_fired = 0

    while True:
        time.sleep(interval)
        cur_source = _file_hash(source_path)
        cur_target = _file_hash(target_path)

        if cur_source != last_source or cur_target != last_target:
            event = WatchEvent(
                source_path=source_path,
                target_path=target_path,
                source_hash=cur_source or "",
                target_hash=cur_target or "",
            )
            callback(event)
            last_source = cur_source
            last_target = cur_target
            events_fired += 1
            if max_events is not None and events_fired >= max_events:
                break
