"""Tagging module: attach user-defined labels to schema diffs for triage and tracking."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from schema_drift.comparator import ComparisonResult, SchemaDiff


@dataclass
class TaggedDiff:
    """A schema diff decorated with one or more string tags."""

    diff: SchemaDiff
    tags: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"TaggedDiff(table={self.diff.table_name!r}, tags={self.tags!r})"

    def has_tag(self, tag: str) -> bool:
        """Return True if *tag* is present (case-insensitive)."""
        return tag.lower() in (t.lower() for t in self.tags)


@dataclass
class TaggedResult:
    """Wraps a ComparisonResult and exposes its diffs with tags applied."""

    source_name: str
    target_name: str
    tagged_diffs: List[TaggedDiff] = field(default_factory=list)

    def filter_by_tag(self, tag: str) -> List[TaggedDiff]:
        """Return only the TaggedDiff entries that carry *tag*."""
        return [td for td in self.tagged_diffs if td.has_tag(tag)]

    def all_tags(self) -> List[str]:
        """Return a sorted, deduplicated list of every tag in this result."""
        seen: set = set()
        for td in self.tagged_diffs:
            seen.update(t.lower() for t in td.tags)
        return sorted(seen)


def tag_result(
    result: ComparisonResult,
    tag_map: Optional[Dict[str, List[str]]] = None,
) -> TaggedResult:
    """Convert a *ComparisonResult* into a *TaggedResult*.

    Args:
        result:  The comparison result to annotate.
        tag_map: Optional mapping of ``table_name -> [tag, ...]``.  Diffs
                 whose table name appears in the map receive those tags;
                 all others receive an empty tag list.

    Returns:
        A :class:`TaggedResult` containing one :class:`TaggedDiff` per diff.
    """
    tag_map = tag_map or {}
    tagged: List[TaggedDiff] = [
        TaggedDiff(diff=d, tags=list(tag_map.get(d.table_name, [])))
        for d in result.diffs
    ]
    return TaggedResult(
        source_name=result.source_name,
        target_name=result.target_name,
        tagged_diffs=tagged,
    )
