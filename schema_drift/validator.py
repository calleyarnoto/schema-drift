"""Validates schemas and diffs for common issues and anti-patterns."""

from dataclasses import dataclass, field
from typing import List

from schema_drift.models import Table
from schema_drift.comparator import ComparisonResult, DiffType


@dataclass
class ValidationIssue:
    severity: str  # 'error' | 'warning'
    code: str
    message: str

    def __repr__(self) -> str:
        return f"[{self.severity.upper()}] {self.code}: {self.message}"


@dataclass
class ValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def __repr__(self) -> str:
        return (
            f"ValidationReport(errors={len(self.errors)}, "
            f"warnings={len(self.warnings)})"
        )


def validate_table(table: Table) -> List[ValidationIssue]:
    """Check a single table for structural issues."""
    issues = []

    if not table.columns:
        issues.append(ValidationIssue(
            severity="error",
            code="EMPTY_TABLE",
            message=f"Table '{table.name}' has no columns.",
        ))

    has_primary_key = any(
        c.primary_key for c in table.columns
    )
    if not has_primary_key:
        issues.append(ValidationIssue(
            severity="warning",
            code="NO_PRIMARY_KEY",
            message=f"Table '{table.name}' has no primary key column.",
        ))

    seen_names = set()
    for col in table.columns:
        if col.name in seen_names:
            issues.append(ValidationIssue(
                severity="error",
                code="DUPLICATE_COLUMN",
                message=f"Table '{table.name}' has duplicate column '{col.name}'.",
            ))
        seen_names.add(col.name)

    return issues


def validate_result(result: ComparisonResult) -> ValidationReport:
    """Validate all diffs in a ComparisonResult for risky changes."""
    issues = []

    for diff in result.diffs:
        if diff.diff_type == DiffType.COLUMN_TYPE_CHANGED:
            issues.append(ValidationIssue(
                severity="error",
                code="DESTRUCTIVE_TYPE_CHANGE",
                message=(
                    f"Column type changed on '{diff.table_name}.{diff.column_name}': "
                    f"{diff.old_value!r} -> {diff.new_value!r}. "
                    "This may cause data loss."
                ),
            ))
        elif diff.diff_type == DiffType.COLUMN_REMOVED:
            issues.append(ValidationIssue(
                severity="error",
                code="COLUMN_REMOVED",
                message=(
                    f"Column '{diff.column_name}' removed from table '{diff.table_name}'. "
                    "Existing data will be lost."
                ),
            ))
        elif diff.diff_type == DiffType.TABLE_REMOVED:
            issues.append(ValidationIssue(
                severity="error",
                code="TABLE_REMOVED",
                message=f"Table '{diff.table_name}' removed. All data will be lost.",
            ))
        elif diff.diff_type == DiffType.NULLABLE_CHANGED:
            if diff.new_value is False:
                issues.append(ValidationIssue(
                    severity="warning",
                    code="NOT_NULL_ADDED",
                    message=(
                        f"Column '{diff.column_name}' in '{diff.table_name}' "
                        "changed to NOT NULL. Existing NULLs will cause migration failure."
                    ),
                ))

    return ValidationReport(issues=issues)
