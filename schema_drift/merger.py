"""Merge two ComparisonResults into a single unified result."""

from dataclasses import dataclass, field
from typing import List, Optional

from schema_drift.comparator import ComparisonResult, SchemaDiff


@dataclass
class MergedResult:
    """A unified result combining diffs from multiple comparison results."""

    label: str
    sources: List[str] = field(default_factory=list)
    diffs: List[SchemaDiff] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.diffs) > 0

    @property
    def diff_count(self) -> int:
        return len(self.diffs)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MergedResult(label={self.label!r}, "
            f"sources={self.sources!r}, "
            f"diffs={self.diff_count})"
        )


def merge_results(
    results: List[ComparisonResult],
    label: str = "merged",
    deduplicate: bool = True,
) -> MergedResult:
    """Merge a list of ComparisonResults into a single MergedResult.

    Args:
        results: List of ComparisonResult objects to merge.
        label: A descriptive label for the merged result.
        deduplicate: If True, remove duplicate SchemaDiff entries.

    Returns:
        A MergedResult containing all diffs from the provided results.
    """
    sources: List[str] = []
    all_diffs: List[SchemaDiff] = []
    seen: set = set()

    for result in results:
        schema_name = getattr(result, "schema_name", "unknown")
        if schema_name not in sources:
            sources.append(schema_name)

        for diff in result.diffs:
            if deduplicate:
                key = (diff.diff_type, diff.table_name, diff.column_name)
                if key in seen:
                    continue
                seen.add(key)
            all_diffs.append(diff)

    return MergedResult(label=label, sources=sources, diffs=all_diffs)
