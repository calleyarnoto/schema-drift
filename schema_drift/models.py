"""Core data models for representing database schema objects."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Column:
    """Represents a single column in a database table."""

    name: str
    data_type: str
    nullable: bool = True
    default: Optional[str] = None
    max_length: Optional[int] = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Column):
            return False
        return (
            self.name == other.name
            and self.data_type == other.data_type
            and self.nullable == other.nullable
            and self.default == other.default
            and self.max_length == other.max_length
        )

    def __repr__(self) -> str:
        parts = [f"{self.name} {self.data_type}"]
        if self.max_length is not None:
            parts[0] += f"({self.max_length})"
        parts.append("NULL" if self.nullable else "NOT NULL")
        if self.default is not None:
            parts.append(f"DEFAULT {self.default}")
        return " ".join(parts)


@dataclass
class Table:
    """Represents a database table with its columns."""

    name: str
    columns: list[Column] = field(default_factory=list)

    def get_column(self, name: str) -> Optional[Column]:
        """Return a column by name, or None if not found."""
        for col in self.columns:
            if col.name == name:
                return col
        return None

    @property
    def column_names(self) -> set[str]:
        return {col.name for col in self.columns}


@dataclass
class Schema:
    """Represents a full database schema (collection of tables)."""

    name: str
    tables: list[Table] = field(default_factory=list)

    def get_table(self, name: str) -> Optional[Table]:
        """Return a table by name, or None if not found."""
        for table in self.tables:
            if table.name == name:
                return table
        return None

    @property
    def table_names(self) -> set[str]:
        return {table.name for table in self.tables}
