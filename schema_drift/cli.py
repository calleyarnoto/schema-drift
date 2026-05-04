"""Command-line interface for schema-drift."""

import sys
import argparse
from typing import List, Optional

from schema_drift.loader import load_schema_from_json
from schema_drift.comparator import compare_schemas
from schema_drift.formatter import format_result
from schema_drift.exporter import export_result, SUPPORTED_FORMATS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schema-drift",
        description="Compare database schemas across environments.",
    )
    parser.add_argument("source", help="Path to source schema JSON file.")
    parser.add_argument("target", help="Path to target schema JSON file.")
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        default=False,
        help="Exit with code 1 when schema drift is detected.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        dest="fmt",
        help="Output format for the diff report (default: text).",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help=(
            "Write the report to FILE instead of stdout. "
            "Format is inferred from the extension unless --format is given."
        ),
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
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
    report = format_result(result, fmt=args.fmt)

    if args.output:
        try:
            export_result(result, args.output, fmt=args.fmt if args.fmt != "text" else None)
        except (ValueError, OSError) as exc:
            print(f"Error writing output file: {exc}", file=sys.stderr)
            return 2
    else:
        print(report)

    if args.fail_on_drift and result.has_changes:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
