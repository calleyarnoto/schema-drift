"""Summarize comparison results into statistics and high-level metrics."""

from dataclasses import dataclass, field
from typing import Dict, List

from schema_drift.comparator import ComparisonResult, DiffType


@dataclass
class SchemaSummary:
    schema_name: str
    total_tables: int = 0
    tables_added: int = 0
    tables_removed: int = 0
    tables_modified: int = 0
    total_diffs: int = 0
    diffs_by_type: Dict[str, int] = field(default_factory=dict)
    affected_tables: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return self.total_diffs > 0

    def __repr__(self) -> str:
        return (
            f"SchemaSummary(schema={self.schema_name!r}, "
            f"total_diffs={self.total_diffs}, "
            f"tables_modified={self.tables_modified})"
        )


def summarize(result: ComparisonResult) -> SchemaSummary:
    """Generate a SchemaSummary from a ComparisonResult."""
    summary = SchemaSummary(schema_name=result.schema_name)
    summary.total_diffs = len(result.diffs)

    table_names_with_diffs: set = set()
    diffs_by_type: Dict[str, int] = {}

    for diff in result.diffs:
        type_key = diff.diff_type.value
        diffs_by_type[type_key] = diffs_by_type.get(type_key, 0) + 1
        table_names_with_diffs.add(diff.table_name)

        if diff.diff_type == DiffType.TABLE_ADDED:
            summary.tables_added += 1
        elif diff.diff_type == DiffType.TABLE_REMOVED:
            summary.tables_removed += 1

    summary.diffs_by_type = diffs_by_type
    summary.affected_tables = sorted(table_names_with_diffs)

    # Tables modified = affected tables minus purely added/removed tables
    purely_structural = {
        d.table_name
        for d in result.diffs
        if d.diff_type in (DiffType.TABLE_ADDED, DiffType.TABLE_REMOVED)
    }
    modified_tables = table_names_with_diffs - purely_structural
    summary.tables_modified = len(modified_tables)
    summary.total_tables = len(result.diffs)  # approximate; refined via schema if available

    return summary
