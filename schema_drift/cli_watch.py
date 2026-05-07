"""CLI sub-command: ``schema-drift watch``."""

from __future__ import annotations

import argparse
import sys

from schema_drift.watcher import watch
from schema_drift.watch_handler import make_handler


def add_watch_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *watch* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "watch",
        help="Watch schema files and report drift on change.",
    )
    p.add_argument("source", help="Path to the source schema JSON file.")
    p.add_argument("target", help="Path to the target schema JSON file.")
    p.add_argument(
        "--format",
        dest="fmt",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=2.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 2.0).",
    )
    p.set_defaults(func=_run_watch)


def _run_watch(args: argparse.Namespace) -> int:
    handler = make_handler(fmt=args.fmt, out=sys.stdout, err=sys.stderr)
    sys.stdout.write(
        f"[schema-drift] Watching {args.source!r} and {args.target!r} "
        f"(interval={args.interval}s) — press Ctrl+C to stop.\n"
    )
    try:
        watch(
            source_path=args.source,
            target_path=args.target,
            callback=handler,
            interval=args.interval,
        )
    except KeyboardInterrupt:
        sys.stdout.write("\n[schema-drift] Watch stopped.\n")
    return 0
