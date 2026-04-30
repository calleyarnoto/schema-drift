"""Schema comparison logic for schema-drift."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from schema_drift.models import Table


class DiffType(str, Enum):
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
    detail: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        parts = [self.diff_type.value, self.table_name]
        if self.column_name:
            parts.append(self.column_name)
        if self.detail:
            parts.append(f"({self.detail})")
        return " ".join(parts)


@dataclass
class ComparisonResult:
    schema_name: Optional[str] = None
    diffs: List[SchemaDiff] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.diffs) > 0

    def add(self, diff: SchemaDiff) -> None:
        self.diffs.append(diff)

    def tables_added(self) -> List[SchemaDiff]:
        return [d for d in self.diffs if d.diff_type == DiffType.TABLE_ADDED]

    def tables_removed(self) -> List[SchemaDiff]:
        return [d for d in self.diffs if d.diff_type == DiffType.TABLE_REMOVED]

    def columns_changed(self) -> List[SchemaDiff]:
        return [
            d
            for d in self.diffs
            if d.diff_type
            in (DiffType.COLUMN_ADDED, DiffType.COLUMN_REMOVED, DiffType.COLUMN_MODIFIED)
        ]


def _compare_tables(table_name: str, source: Table, target: Table) -> List[SchemaDiff]:
    diffs: List[SchemaDiff] = []
    source_cols = {c.name: c for c in source.columns}
    target_cols = {c.name: c for c in target.columns}

    for col_name, col in source_cols.items():
        if col_name not in target_cols:
            diffs.append(
                SchemaDiff(
                    diff_type=DiffType.COLUMN_REMOVED,
                    table_name=table_name,
                    column_name=col_name,
                )
            )
        elif col != target_cols[col_name]:
            detail = f"{col.data_type} -> {target_cols[col_name].data_type}"
            diffs.append(
                SchemaDiff(
                    diff_type=DiffType.COLUMN_MODIFIED,
                    table_name=table_name,
                    column_name=col_name,
                    detail=detail,
                )
            )

    for col_name in target_cols:
        if col_name not in source_cols:
            diffs.append(
                SchemaDiff(
                    diff_type=DiffType.COLUMN_ADDED,
                    table_name=table_name,
                    column_name=col_name,
                )
            )

    return diffs


def compare_schemas(
    source: Dict[str, Table],
    target: Dict[str, Table],
    schema_name: Optional[str] = None,
) -> ComparisonResult:
    result = ComparisonResult(schema_name=schema_name)

    for table_name in source:
        if table_name not in target:
            result.add(
                SchemaDiff(diff_type=DiffType.TABLE_REMOVED, table_name=table_name)
            )
        else:
            for diff in _compare_tables(table_name, source[table_name], target[table_name]):
                result.add(diff)

    for table_name in target:
        if table_name not in source:
            result.add(
                SchemaDiff(diff_type=DiffType.TABLE_ADDED, table_name=table_name)
            )

    return result
