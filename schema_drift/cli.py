"""Command-line interface for schema-drift."""

import argparse
import sys

from schema_drift.comparator import compare_schemas
from schema_drift.loader import load_schema_from_json
from schema_drift.reporter import generate_text_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schema-drift",
        description="Compare database schemas across environments and report differences.",
    )
    parser.add_argument(
        "source",
        metavar="SOURCE",
        help="Path to the source schema JSON file (e.g. production).",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to the target schema JSON file (e.g. staging).",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        default=None,
        help="Write the report to FILE instead of stdout.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when drift is detected, 0 otherwise.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        source_schema = load_schema_from_json(args.source)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error loading source schema: {exc}", file=sys.stderr)
        return 2

    try:
        target_schema = load_schema_from_json(args.target)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error loading target schema: {exc}", file=sys.stderr)
        return 2

    result = compare_schemas(source_schema, target_schema)
    report = generate_text_report(result)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(report)
        except OSError as exc:
            print(f"Error writing report: {exc}", file=sys.stderr)
            return 2
    else:
        print(report)

    if args.exit_code and result.has_changes:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
