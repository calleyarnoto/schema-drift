"""Generate SQL patch statements from a ComparisonResult to migrate source schema to target."""

from typing import List
from schema_drift.comparator import ComparisonResult, DiffType


def _quote(name: str) -> str:
    return f'"{name}"'


def _column_definition(col) -> str:
    parts = [_quote(col.name), col.data_type.upper()]
    if col.max_length is not None:
        parts[1] += f"({col.max_length})"
    if not col.nullable:
        parts.append("NOT NULL")
    if col.default is not None:
        parts.append(f"DEFAULT {col.default}")
    return " ".join(parts)


def generate_patch_sql(result: ComparisonResult) -> List[str]:
    """Return a list of SQL statements that bring *source* in line with *target*."""
    statements: List[str] = []

    for diff in result.diffs:
        table = _quote(diff.table_name)

        if diff.diff_type == DiffType.TABLE_ADDED:
            # Table exists in target but not source — CREATE it
            cols = ", ".join(_column_definition(c) for c in diff.target_table.columns)
            statements.append(f"CREATE TABLE {table} ({cols});")

        elif diff.diff_type == DiffType.TABLE_REMOVED:
            # Table exists in source but not target — DROP it
            statements.append(f"DROP TABLE {table};")

        elif diff.diff_type == DiffType.COLUMN_ADDED:
            col_def = _column_definition(diff.target_column)
            statements.append(f"ALTER TABLE {table} ADD COLUMN {col_def};")

        elif diff.diff_type == DiffType.COLUMN_REMOVED:
            statements.append(
                f"ALTER TABLE {table} DROP COLUMN {_quote(diff.column_name)};"
            )

        elif diff.diff_type == DiffType.COLUMN_MODIFIED:
            col_def = _column_definition(diff.target_column)
            # Use a generic ALTER … ALTER COLUMN syntax (PostgreSQL-style)
            statements.append(
                f"-- Modified column {diff.column_name} in {diff.table_name}"
            )
            statements.append(
                f"ALTER TABLE {table} ALTER COLUMN {_quote(diff.column_name)} "
                f"TYPE {diff.target_column.data_type.upper()}"
                + (
                    f"({diff.target_column.max_length})"
                    if diff.target_column.max_length is not None
                    else ""
                )
                + ";"
            )

    return statements
