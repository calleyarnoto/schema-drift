"""Command-line interface for schema-drift."""

import argparse
import sys
from schema_drift.loader import load_schema_from_json
from schema_drift.comparator import compare_schemas
from schema_drift.formatter import format_result
from schema_drift.exporter import export_result
from schema_drift.filter import (
    filter_by_diff_type,
    filter_by_tables,
    exclude_tables,
)
from schema_drift.comparator import DiffType


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schema-drift",
        description="Compare database schemas across environments.",
    )
    parser.add_argument("source", help="Path to the source schema JSON file.")
    parser.add_argument("target", help="Path to the target schema JSON file.")
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write report to FILE instead of stdout.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if drift is detected.",
    )
    parser.add_argument(
        "--only-tables",
        metavar="TABLE",
        nargs="+",
        help="Restrict comparison to these tables.",
    )
    parser.add_argument(
        "--exclude-tables",
        metavar="TABLE",
        nargs="+",
        dest="exclude_tables",
        help="Exclude these tables from the comparison.",
    )
    parser.add_argument(
        "--only-types",
        metavar="TYPE",
        nargs="+",
        choices=[t.value for t in DiffType],
        help="Show only diffs of these types.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        source = load_schema_from_json(args.source)
    except FileNotFoundError:
        print(f"Error: source file not found: {args.source}", file=sys.stderr)
        return 2

    try:
        target = load_schema_from_json(args.target)
    except FileNotFoundError:
        print(f"Error: target file not found: {args.target}", file=sys.stderr)
        return 2

    result = compare_schemas(source, target)

    if args.only_tables:
        result = filter_by_tables(result, args.only_tables)
    if args.exclude_tables:
        result = exclude_tables(result, args.exclude_tables)
    if args.only_types:
        types = [DiffType(t) for t in args.only_types]
        result = filter_by_diff_type(result, types)

    if args.output:
        export_result(result, args.output)
    else:
        print(format_result(result, fmt=args.format))

    if args.exit_code and result.has_changes():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
