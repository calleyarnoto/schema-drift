"""Human-readable report generation from ComparisonResult."""

from schema_drift.comparator import ComparisonResult, DiffType, SchemaDiff


INDENT = "  "

_SYMBOLS = {
    DiffType.TABLE_ADDED: "+",
    DiffType.TABLE_REMOVED: "-",
    DiffType.COLUMN_ADDED: "+",
    DiffType.COLUMN_REMOVED: "-",
    DiffType.COLUMN_MODIFIED: "~",
}


def _format_diff_line(diff: SchemaDiff) -> str:
    symbol = _SYMBOLS.get(diff.diff_type, "?")
    if diff.diff_type == DiffType.TABLE_ADDED:
        return f"{symbol} TABLE {diff.table_name} (added)"
    if diff.diff_type == DiffType.TABLE_REMOVED:
        return f"{symbol} TABLE {diff.table_name} (removed)"
    if diff.diff_type == DiffType.COLUMN_ADDED:
        return f"{INDENT}{symbol} COLUMN {diff.column_name}: {diff.new_value!r}"
    if diff.diff_type == DiffType.COLUMN_REMOVED:
        return f"{INDENT}{symbol} COLUMN {diff.column_name}: {diff.old_value!r}"
    if diff.diff_type == DiffType.COLUMN_MODIFIED:
        return (
            f"{INDENT}{symbol} COLUMN {diff.column_name}:\n"
            f"{INDENT*2}before: {diff.old_value!r}\n"
            f"{INDENT*2}after:  {diff.new_value!r}"
        )
    return f"{symbol} {diff.diff_type.value}: {diff.table_name}"


def generate_text_report(result: ComparisonResult, title: str = "Schema Diff Report") -> str:
    """Generate a plain-text diff report from a ComparisonResult."""
    lines = [
        "=" * 50,
        title,
        "=" * 50,
    ]

    if not result.has_changes:
        lines.append("No differences found. Schemas are identical.")
        lines.append("=" * 50)
        return "\n".join(lines)

    # Group diffs by table for readability
    table_diffs: dict = {}
    for diff in result.diffs:
        table_diffs.setdefault(diff.table_name, []).append(diff)

    for table_name, diffs in table_diffs.items():
        lines.append(f"\nTable: {table_name}")
        lines.append("-" * 30)
        for diff in diffs:
            lines.append(_format_diff_line(diff))

    lines.append("")
    lines.append("=" * 50)
    lines.append(result.summary)
    lines.append("=" * 50)
    return "\n".join(lines)
