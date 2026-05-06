"""Filtering utilities for schema comparison results."""

from typing import List, Optional
from schema_drift.comparator import ComparisonResult, SchemaDiff, DiffType


def filter_by_diff_type(
    result: ComparisonResult,
    diff_types: List[DiffType],
) -> ComparisonResult:
    """Return a new ComparisonResult containing only diffs of the given types."""
    filtered_diffs = [
        diff for diff in result.diffs if diff.diff_type in diff_types
    ]
    return ComparisonResult(
        source_schema=result.source_schema,
        target_schema=result.target_schema,
        diffs=filtered_diffs,
    )


def filter_by_table(
    result: ComparisonResult,
    table_name: str,
) -> ComparisonResult:
    """Return a new ComparisonResult containing only diffs for a specific table."""
    filtered_diffs = [
        diff for diff in result.diffs if diff.table_name == table_name
    ]
    return ComparisonResult(
        source_schema=result.source_schema,
        target_schema=result.target_schema,
        diffs=filtered_diffs,
    )


def filter_by_tables(
    result: ComparisonResult,
    table_names: List[str],
) -> ComparisonResult:
    """Return a new ComparisonResult containing only diffs for the given tables."""
    name_set = set(table_names)
    filtered_diffs = [
        diff for diff in result.diffs if diff.table_name in name_set
    ]
    return ComparisonResult(
        source_schema=result.source_schema,
        target_schema=result.target_schema,
        diffs=filtered_diffs,
    )


def exclude_tables(
    result: ComparisonResult,
    table_names: List[str],
) -> ComparisonResult:
    """Return a new ComparisonResult excluding diffs for the given tables."""
    name_set = set(table_names)
    filtered_diffs = [
        diff for diff in result.diffs if diff.table_name not in name_set
    ]
    return ComparisonResult(
        source_schema=result.source_schema,
        target_schema=result.target_schema,
        diffs=filtered_diffs,
    )
