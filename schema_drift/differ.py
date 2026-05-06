"""Column-level diff utilities for generating human-readable change descriptions."""

from dataclasses import dataclass
from typing import Optional

from schema_drift.models import Column


@dataclass
class ColumnChange:
    """Represents a single attribute change on a column."""
    attribute: str
    old_value: Optional[object]
    new_value: Optional[object]

    def __repr__(self) -> str:
        return (
            f"ColumnChange(attribute={self.attribute!r}, "
            f"old={self.old_value!r}, new={self.new_value!r})"
        )

    def to_description(self) -> str:
        """Return a human-readable one-line description of this change."""
        old = "null" if self.old_value is None else repr(self.old_value)
        new = "null" if self.new_value is None else repr(self.new_value)
        return f"{self.attribute}: {old} -> {new}"


def diff_columns(old: Column, new: Column) -> list[ColumnChange]:
    """Compare two columns with the same name and return a list of attribute changes."""
    changes: list[ColumnChange] = []

    if old.data_type != new.data_type:
        changes.append(ColumnChange("data_type", old.data_type, new.data_type))

    if old.nullable != new.nullable:
        changes.append(ColumnChange("nullable", old.nullable, new.nullable))

    if old.default != new.default:
        changes.append(ColumnChange("default", old.default, new.default))

    if old.max_length != new.max_length:
        changes.append(ColumnChange("max_length", old.max_length, new.max_length))

    if old.primary_key != new.primary_key:
        changes.append(ColumnChange("primary_key", old.primary_key, new.primary_key))

    return changes


def describe_column_diffs(old: Column, new: Column) -> list[str]:
    """Return a list of human-readable change strings for a modified column."""
    return [change.to_description() for change in diff_columns(old, new)]
