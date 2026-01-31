"""Database driver adapters for migrations.

Each driver implements the MigrationDriver interface:
- get_field_type(field_def) -> str - SQL type for field
- apply_operations(conn, operations, graph) -> None - Execute migration ops
"""
