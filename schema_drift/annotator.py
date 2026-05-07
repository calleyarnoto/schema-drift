"""Annotate schema diffs with human-readable change descriptions and risk hints."""

from dataclasses import dataclass, field
from typing import List, Optional

from schema_drift.comparator import ComparisonResult, DiffType, SchemaDiff


@dataclass
class Annotation:
    diff: SchemaDiff
    description: str
    risk: str  # "low", "medium", "high"
    hint: Optional[str] = None

    def __repr__(self) -> str:
        return f"Annotation(table={self.diff.table_name!r}, risk={self.risk!r})"


_RISK_MAP = {
    DiffType.TABLE_ADDED: ("low", "New table added; no existing data affected."),
    DiffType.TABLE_REMOVED: ("high", "Dropping a table will permanently delete all its data."),
    DiffType.COLUMN_ADDED: ("low", "Adding a column is generally safe; ensure NOT NULL columns have a default."),
    DiffType.COLUMN_REMOVED: ("high", "Removing a column will delete its data and may break dependent queries."),
    DiffType.COLUMN_MODIFIED: ("medium", "Changing a column type or constraint may cause implicit data casting or errors."),
}


def _build_description(diff: SchemaDiff) -> str:
    if diff.diff_type == DiffType.TABLE_ADDED:
        return f"Table '{diff.table_name}' is present in target but not in source."
    if diff.diff_type == DiffType.TABLE_REMOVED:
        return f"Table '{diff.table_name}' exists in source but is missing from target."
    col = diff.column_name or "unknown"
    if diff.diff_type == DiffType.COLUMN_ADDED:
        return f"Column '{col}' was added to table '{diff.table_name}'."
    if diff.diff_type == DiffType.COLUMN_REMOVED:
        return f"Column '{col}' was removed from table '{diff.table_name}'."
    if diff.diff_type == DiffType.COLUMN_MODIFIED:
        detail = f": {diff.detail}" if diff.detail else ""
        return f"Column '{col}' in table '{diff.table_name}' was modified{detail}."
    return str(diff)


def annotate(result: ComparisonResult) -> List[Annotation]:
    """Return a list of Annotation objects for every diff in *result*."""
    annotations: List[Annotation] = []
    for diff in result.diffs:
        risk, hint = _RISK_MAP.get(diff.diff_type, ("low", None))
        annotations.append(
            Annotation(
                diff=diff,
                description=_build_description(diff),
                risk=risk,
                hint=hint,
            )
        )
    return annotations


def highest_risk(annotations: List[Annotation]) -> str:
    """Return the highest risk level found across all annotations."""
    order = ["low", "medium", "high"]
    current = 0
    for ann in annotations:
        idx = order.index(ann.risk) if ann.risk in order else 0
        if idx > current:
            current = idx
    return order[current]
