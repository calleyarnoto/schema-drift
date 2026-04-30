"""Load database schemas from various sources into schema_drift models."""

import json
from pathlib import Path
from typing import Union

from schema_drift.models import Column, Table, Schema


def load_schema_from_dict(data: dict) -> Schema:
    """Parse a dictionary representation into a Schema object."""
    tables = {}
    for table_name, table_data in data.get("tables", {}).items():
        columns = []
        for col_data in table_data.get("columns", []):
            column = Column(
                name=col_data["name"],
                data_type=col_data["data_type"],
                nullable=col_data.get("nullable", True),
                max_length=col_data.get("max_length"),
                default=col_data.get("default"),
                primary_key=col_data.get("primary_key", False),
            )
            columns.append(column)
        tables[table_name] = Table(
            name=table_name,
            columns=columns,
        )
    return Schema(name=data.get("name", "unnamed"), tables=tables)


def load_schema_from_json(source: Union[str, Path]) -> Schema:
    """Load a schema from a JSON file path or JSON string."""
    path = Path(source)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.loads(str(source))
    return load_schema_from_dict(data)


def schema_to_dict(schema: Schema) -> dict:
    """Serialize a Schema object back to a plain dictionary."""
    tables = {}
    for table_name, table in schema.tables.items():
        columns = [
            {
                "name": col.name,
                "data_type": col.data_type,
                "nullable": col.nullable,
                "max_length": col.max_length,
                "default": col.default,
                "primary_key": col.primary_key,
            }
            for col in table.columns
        ]
        tables[table_name] = {"columns": columns}
    return {"name": schema.name, "tables": tables}
