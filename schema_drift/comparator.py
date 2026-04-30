"""Schema comparator module for detecting differences between two database schemas."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from schema_drift.models import Table, Column


class DiffType(Enum):
    TABLE_ADDED = "table_added"
    TABLE_REMOVED = "table_removed"
    COLUMN_ADDED = "column_added"
    COLUMN_REMOVED = "column_removed"
    COLUMN_MODIFIED = "column_modified"


@dataclass
class SchemaDiff:
    diff_type: DiffType
    table_name: str
    column_name: Optional[str] = None
    old_value: Optional[object] = None
    new_value: Optional[object] = None

    def __repr__(self) -> str:
        if self.column_name:
            return (
                f"SchemaDiff({self.diff_type.value}, table={self.table_name!r}, "
                f"column={self.column_name!r})"
            )
        return f"SchemaDiff({self.diff_type.value}, table={self.table_name!r})"


@dataclass
class ComparisonResult:
    diffs: List[SchemaDiff] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.diffs) > 0

    @property
    def summary(self) -> str:
        if not self.has_changes:
            return "No schema differences detected."
        counts = {}
        for diff in self.diffs:
            counts[diff.diff_type] = counts.get(diff.diff_type, 0) + 1
        parts = [f"{v} {k.value.replace('_', ' ')}(s)" for k, v in counts.items()]
        return "Changes detected: " + ", ".join(parts) + "."


def compare_schemas(
    source: List[Table], target: List[Table]
) -> ComparisonResult:
    """Compare two lists of Table objects and return a ComparisonResult."""
    result = ComparisonResult()

    source_map = {t.name: t for t in source}
    target_map = {t.name: t for t in target}

    for table_name in source_map:
        if table_name not in target_map:
            result.diffs.append(
                SchemaDiff(DiffType.TABLE_REMOVED, table_name=table_name)
            )
            continue
        _compare_columns(source_map[table_name], target_map[table_name], result)

    for table_name in target_map:
        if table_name not in source_map:
            result.diffs.append(
                SchemaDiff(DiffType.TABLE_ADDED, table_name=table_name)
            )

    return result


def _compare_columns(
    source_table: Table, target_table: Table, result: ComparisonResult
) -> None:
    source_cols = {c.name: c for c in source_table.columns}
    target_cols = {c.name: c for c in target_table.columns}

    for col_name, col in source_cols.items():
        if col_name not in target_cols:
            result.diffs.append(
                SchemaDiff(DiffType.COLUMN_REMOVED, source_table.name, col_name,
                           old_value=col)
            )
        elif col != target_cols[col_name]:
            result.diffs.append(
                SchemaDiff(DiffType.COLUMN_MODIFIED, source_table.name, col_name,
                           old_value=col, new_value=target_cols[col_name])
            )

    for col_name, col in target_cols.items():
        if col_name not in source_cols:
            result.diffs.append(
                SchemaDiff(DiffType.COLUMN_ADDED, source_table.name, col_name,
                           new_value=col)
            )
