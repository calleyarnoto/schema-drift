"""Generates a structured changelog from a sequence of ComparisonResults over time."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from schema_drift.comparator import ComparisonResult, DiffType


@dataclass
class ChangelogEntry:
    timestamp: str
    source_label: str
    target_label: str
    added_tables: List[str] = field(default_factory=list)
    removed_tables: List[str] = field(default_factory=list)
    modified_tables: List[str] = field(default_factory=list)
    total_diffs: int = 0

    def __repr__(self) -> str:
        return (
            f"ChangelogEntry({self.timestamp!r}, "
            f"added={len(self.added_tables)}, "
            f"removed={len(self.removed_tables)}, "
            f"modified={len(self.modified_tables)})"
        )


@dataclass
class Changelog:
    schema_name: str
    entries: List[ChangelogEntry] = field(default_factory=list)

    def has_entries(self) -> bool:
        return len(self.entries) > 0

    def __repr__(self) -> str:
        return f"Changelog({self.schema_name!r}, entries={len(self.entries)})"


def _now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def build_entry(
    result: ComparisonResult,
    source_label: str = "source",
    target_label: str = "target",
    timestamp: Optional[str] = None,
) -> ChangelogEntry:
    """Convert a ComparisonResult into a ChangelogEntry."""
    added, removed, modified = set(), set(), set()

    for diff in result.diffs:
        if diff.diff_type == DiffType.TABLE_ADDED:
            added.add(diff.table_name)
        elif diff.diff_type == DiffType.TABLE_REMOVED:
            removed.add(diff.table_name)
        else:
            modified.add(diff.table_name)

    return ChangelogEntry(
        timestamp=timestamp or _now_iso(),
        source_label=source_label,
        target_label=target_label,
        added_tables=sorted(added),
        removed_tables=sorted(removed),
        modified_tables=sorted(modified),
        total_diffs=len(result.diffs),
    )


def create_changelog(
    schema_name: str,
    results: List[ComparisonResult],
    labels: Optional[List[tuple]] = None,
) -> Changelog:
    """Build a Changelog from a list of ComparisonResults."""
    entries = []
    for i, result in enumerate(results):
        src, tgt = (labels[i] if labels and i < len(labels) else ("source", "target"))
        entries.append(build_entry(result, source_label=src, target_label=tgt))
    return Changelog(schema_name=schema_name, entries=entries)
