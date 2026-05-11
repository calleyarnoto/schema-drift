"""Linter for schema drift results — flags common schema anti-patterns."""

from dataclasses import dataclass, field
from typing import List

from schema_drift.comparator import ComparisonResult, DiffType


@dataclass
class LintWarning:
    table: str
    column: str | None
    code: str
    message: str

    def __repr__(self) -> str:
        loc = f"{self.table}.{self.column}" if self.column else self.table
        return f"LintWarning({self.code}, {loc!r})"


@dataclass
class LintReport:
    schema_name: str
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def __repr__(self) -> str:
        return f"LintReport({self.schema_name!r}, warnings={self.warning_count})"


def _check_nullable_added(diff, warnings: List[LintWarning]) -> None:
    """Warn when a non-nullable column is added (may break existing rows)."""
    if diff.diff_type == DiffType.COLUMN_ADDED:
        col = diff.column
        if col and not col.nullable and col.default is None:
            warnings.append(LintWarning(
                table=diff.table_name,
                column=col.name,
                code="L001",
                message=(
                    f"Column '{col.name}' added as NOT NULL with no default — "
                    "existing rows will fail unless backfilled."
                ),
            ))


def _check_type_changed(diff, warnings: List[LintWarning]) -> None:
    """Warn when a column type changes, which may cause data loss."""
    if diff.diff_type == DiffType.COLUMN_MODIFIED:
        details = diff.detail or ""
        if "type" in details.lower():
            warnings.append(LintWarning(
                table=diff.table_name,
                column=diff.column_name,
                code="L002",
                message=(
                    f"Column '{diff.column_name}' type changed — "
                    "verify data compatibility before migrating."
                ),
            ))


def _check_column_removed(diff, warnings: List[LintWarning]) -> None:
    """Warn when a column is removed — destructive change."""
    if diff.diff_type == DiffType.COLUMN_REMOVED:
        warnings.append(LintWarning(
            table=diff.table_name,
            column=diff.column_name,
            code="L003",
            message=(
                f"Column '{diff.column_name}' removed from '{diff.table_name}' — "
                "ensure no application code depends on this column."
            ),
        ))


def lint_result(result: ComparisonResult) -> LintReport:
    """Run all lint checks against a ComparisonResult and return a LintReport."""
    warnings: List[LintWarning] = []
    for diff in result.diffs:
        _check_nullable_added(diff, warnings)
        _check_type_changed(diff, warnings)
        _check_column_removed(diff, warnings)
    return LintReport(schema_name=result.schema_name, warnings=warnings)
