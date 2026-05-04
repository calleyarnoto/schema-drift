"""Export comparison results to various file formats."""

import json
import os
from pathlib import Path
from typing import Optional

from schema_drift.comparator import ComparisonResult
from schema_drift.formatter import format_text, format_json, format_markdown


SUPPORTED_FORMATS = ("text", "json", "markdown")


def _get_format_from_extension(path: str) -> Optional[str]:
    """Infer export format from file extension."""
    ext = Path(path).suffix.lower()
    return {
        ".txt": "text",
        ".json": "json",
        ".md": "markdown",
        ".markdown": "markdown",
    }.get(ext)


def export_result(
    result: ComparisonResult,
    output_path: str,
    fmt: Optional[str] = None,
) -> str:
    """Write a ComparisonResult to *output_path* in the requested format.

    If *fmt* is None the format is inferred from the file extension.
    Returns the resolved format string that was used.

    Raises:
        ValueError: if the format cannot be determined or is unsupported.
        OSError: if the file cannot be written.
    """
    resolved_fmt = fmt or _get_format_from_extension(output_path)
    if resolved_fmt is None:
        raise ValueError(
            f"Cannot infer export format from '{output_path}'. "
            f"Provide an explicit format or use a recognised extension "
            f"({', '.join(SUPPORTED_FORMATS)})."
        )
    if resolved_fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{resolved_fmt}'. "
            f"Choose one of: {', '.join(SUPPORTED_FORMATS)}."
        )

    formatters = {
        "text": format_text,
        "json": format_json,
        "markdown": format_markdown,
    }
    content = formatters[resolved_fmt](result)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(content)

    return resolved_fmt
