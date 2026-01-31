"""
Tree visualization utilities for database migrations.
Renders hierarchical data as ASCII trees (Django-style, no emojis).
"""
from typing import List, Dict, Any, Optional


class TreeNode:
    """Represents a node in a tree structure."""
    
    def __init__(self, label: str, is_last: bool = False):
        self.label = label
        self.is_last = is_last
        self.children: List[TreeNode] = []
    
    def add_child(self, label: str) -> "TreeNode":
        child = TreeNode(label, False)
        self.children.append(child)
        if self.children:
            self.children[-1].is_last = True
        if len(self.children) > 1:
            self.children[-2].is_last = False
        return child
    
    def render(self, prefix: str = "", is_root: bool = True) -> str:
        """Render tree as string with proper indentation."""
        if is_root:
            lines = [self.label]
        else:
            connector = "└── " if self.is_last else "├── "
            lines = [prefix + connector + self.label]
        
        if self.children:
            for i, child in enumerate(self.children):
                is_last_child = (i == len(self.children) - 1)
                if is_root:
                    new_prefix = ""
                else:
                    new_prefix = prefix + ("    " if self.is_last else "│   ")
                
                child_lines = child._render_internal(new_prefix, is_last_child)
                lines.extend(child_lines)
        
        return "\n".join(lines)
    
    def _render_internal(self, prefix: str = "", is_last: bool = False) -> List[str]:
        """Internal render helper."""
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + self.label]
        
        if self.children:
            for i, child in enumerate(self.children):
                is_last_child = (i == len(self.children) - 1)
                new_prefix = prefix + ("    " if is_last else "│   ")
                child_lines = child._render_internal(new_prefix, is_last_child)
                lines.extend(child_lines)
        
        return lines


def render_models_tree(models_info: Dict[str, Dict[str, Any]]) -> str:
    """Render models discovery tree (Django-style).
    
    Args:
        models_info: {
            "models.mp": {
                "models": {
                    "User": {
                        "table": "users",
                        "fields": {
                            "id": {"type": "AutoField"},
                            "name": {"type": "CharField"},
                            ...
                        }
                    }
                }
            }
        }
    """
    root = TreeNode("Models Discovered")
    
    for file_path, file_data in sorted(models_info.items()):
        file_node = root.add_child(f"File: {file_path}")
        
        models = file_data.get("models", {})
        for model_name, model_data in sorted(models.items()):
            table_name = model_data.get("table", model_name.lower())
            model_node = file_node.add_child(f"Model: {model_name} -> table '{table_name}'")
            
            fields = model_data.get("fields", {})
            for field_name, field_data in sorted(fields.items()):
                field_type = field_data.get("type", "Unknown")
                constraints = []
                
                if field_data.get("primary_key"):
                    constraints.append("primary_key=True")
                if field_data.get("null"):
                    constraints.append("null=True")
                if field_data.get("unique"):
                    constraints.append("unique=True")
                
                constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
                model_node.add_child(f"{field_name}: {field_type}{constraint_str}")
    
    return root.render()


def render_migration_operations(ops: List[Dict[str, Any]]) -> str:
    """Render migration operations tree (Django-style).
    
    Args:
        ops: List of operation dicts. Can be raw dicts or with 'op' key.
             Each dict might have: type/op, model, table, field_name, fields, etc.
    """
    root = TreeNode("Migration Operations")
    
    if not ops:
        root.add_child("(no operations)")
        return root.render()
    
    # Group by operation type
    op_groups: Dict[str, List[Dict]] = {}
    for op in ops:
        # Support both 'type' and 'op' keys
        op_type = op.get("type") or op.get("op", "Unknown")
        if op_type not in op_groups:
            op_groups[op_type] = []
        op_groups[op_type].append(op)
    
    # Render by type
    type_labels = {
        "CreateTable": "Create Table",
        "create_model": "Create Table",
        "AddColumn": "Add Column",
        "add_column": "Add Column",
        "AlterColumn": "Alter Column",
        "alter_column": "Alter Column",
        "DropColumn": "Drop Column",
        "drop_column": "Drop Column",
        "DropModel": "Drop Table",
        "drop_model": "Drop Table",
        "CreateIndex": "Create Index",
        "create_index": "Create Index",
        "DropIndex": "Drop Index",
        "drop_index": "Drop Index",
        "add_fk": "Add Foreign Key",
        "drop_fk": "Drop Foreign Key",
        "create_enum": "Create Enum",
        "alter_enum": "Alter Enum",
    }
    
    for op_type in sorted(op_groups.keys()):
        type_label = type_labels.get(op_type, op_type)
        type_node = root.add_child(type_label)
        
        for op in op_groups[op_type]:
            model_name = op.get("model", "?")
            table_name = op.get("table", model_name.lower() if model_name != "?" else "?")
            
            # Create Table operations
            if op_type in ("CreateTable", "create_model"):
                model_node = type_node.add_child(f"Table: '{table_name}' (model {model_name})")
                fields = op.get("fields", {})
                
                # Handle fields as dict or list
                if isinstance(fields, dict):
                    for field_name, field_data in sorted(fields.items()):
                        if isinstance(field_data, dict):
                            field_type = field_data.get("type", "Unknown")
                            constraints = []
                            if field_data.get("primary_key"):
                                constraints.append("primary_key=True")
                            if field_data.get("null"):
                                constraints.append("null=True")
                            constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
                            model_node.add_child(f"{field_name}: {field_type}{constraint_str}")
                        else:
                            model_node.add_child(f"{field_name}: {field_data}")
                elif isinstance(fields, list):
                    for field in fields:
                        if isinstance(field, dict):
                            fname = field.get("name", "?")
                            ftype = field.get("type", "Unknown")
                            model_node.add_child(f"{fname}: {ftype}")
                        else:
                            model_node.add_child(f"- {field}")
            
            # Add Column operations
            elif op_type in ("AddColumn", "add_column"):
                field_name = op.get("field_name") or op.get("name", "?")
                field_def = op.get("field_def") or op.get("field_type") or {}
                
                if isinstance(field_def, dict):
                    field_type = field_def.get("type", "?")
                else:
                    field_type = field_def
                
                field_node = type_node.add_child(f"Table '{table_name}' - Field '{field_name}'")
                field_node.add_child(f"type: {field_type}")
                
                if isinstance(field_def, dict):
                    if field_def.get("null"):
                        field_node.add_child("null: True")
                    if field_def.get("default") is not None:
                        field_node.add_child(f"default: {field_def.get('default')}")
            
            # Alter Column operations
            elif op_type in ("AlterColumn", "alter_column"):
                field_name = op.get("field_name") or op.get("name", "?")
                old_def = op.get("old_def", {})
                new_def = op.get("new_def", {})
                field_node = type_node.add_child(f"Table '{table_name}' - Field '{field_name}'")
                
                if isinstance(old_def, dict) and isinstance(new_def, dict):
                    old_type = old_def.get("type", "?")
                    new_type = new_def.get("type", "?")
                    if old_type != new_type:
                        field_node.add_child(f"type: {old_type} → {new_type}")
                    
                    old_null = old_def.get("null", False)
                    new_null = new_def.get("null", False)
                    if old_null != new_null:
                        field_node.add_child(f"null: {old_null} → {new_null}")
                else:
                    changes = op.get("changes", {})
                    if isinstance(changes, dict):
                        for change_key, change_val in changes.items():
                            field_node.add_child(f"{change_key}: {change_val}")
                    else:
                        field_node.add_child(str(changes))
            
            # Drop Column operations
            elif op_type in ("DropColumn", "drop_column"):
                field_name = op.get("field_name") or op.get("name", "?")
                type_node.add_child(f"Table '{table_name}' - Field '{field_name}'")
            
            # Drop Table operations
            elif op_type in ("DropModel", "drop_model"):
                type_node.add_child(f"Table '{table_name}' (model {model_name})")
            
            # Index operations
            elif op_type in ("CreateIndex", "create_index"):
                index_name = op.get("index_name") or op.get("name", "?")
                columns = op.get("columns", [])
                idx_node = type_node.add_child(f"Index '{index_name}'")
                if columns:
                    idx_node.add_child(f"columns: {', '.join(columns) if isinstance(columns, list) else columns}")
            
            elif op_type in ("DropIndex", "drop_index"):
                index_name = op.get("index_name") or op.get("name", "?")
                type_node.add_child(f"Index '{index_name}'")
            
            # Foreign Key operations
            elif op_type == "add_fk":
                from_model = op.get("from", "?")
                from_field = op.get("field", "?")
                to_model = op.get("to", "?")
                fk_node = type_node.add_child(f"Model '{from_model}.{from_field}' → '{to_model}'")
            
            elif op_type == "drop_fk":
                from_model = op.get("from", "?")
                from_field = op.get("field", "?")
                to_model = op.get("to", "?")
                fk_node = type_node.add_child(f"Model '{from_model}.{from_field}' (was {to_model})")
            
            # Enum operations
            elif op_type == "create_enum":
                enum_name = op.get("name", "?")
                values = op.get("values", [])
                enum_node = type_node.add_child(f"Enum '{enum_name}'")
                if values:
                    for val_tuple in values:
                        if isinstance(val_tuple, (tuple, list)):
                            val_name = val_tuple[0] if val_tuple else "?"
                            enum_node.add_child(f"- {val_name}")
                        else:
                            enum_node.add_child(f"- {val_tuple}")
            
            elif op_type == "alter_enum":
                enum_name = op.get("name", "?")
                values = op.get("values", [])
                enum_node = type_node.add_child(f"Enum '{enum_name}'")
                if values:
                    for val_tuple in values:
                        if isinstance(val_tuple, (tuple, list)):
                            val_name = val_tuple[0] if val_tuple else "?"
                            enum_node.add_child(f"- {val_name}")
                        else:
                            enum_node.add_child(f"- {val_tuple}")
            
            else:
                # Generic rendering
                op_summary = str(op)[:80]
                type_node.add_child(f"{model_name}: {op_summary}...")
    
    return root.render()


def render_comparison_tree(before: Dict[str, Any], after: Dict[str, Any]) -> str:
    """Render side-by-side comparison of schema before and after.
    
    Args:
        before: Schema snapshot before migration
        after: Schema snapshot after migration
    """
    root = TreeNode("Schema Comparison")
    
    all_tables = set(before.get("tables", {}).keys()) | set(after.get("tables", {}).keys())
    
    for table_name in sorted(all_tables):
        before_table = before.get("tables", {}).get(table_name, {})
        after_table = after.get("tables", {}).get(table_name, {})
        
        if not before_table and after_table:
            # New table
            table_node = root.add_child(f"NEW Table: {table_name}")
            for field_name in sorted(after_table.get("fields", {}).keys()):
                table_node.add_child(f"- {field_name}")
        
        elif before_table and not after_table:
            # Dropped table
            table_node = root.add_child(f"DROPPED Table: {table_name}")
            for field_name in sorted(before_table.get("fields", {}).keys()):
                table_node.add_child(f"- {field_name}")
        
        else:
            # Modified table
            before_fields = set(before_table.get("fields", {}).keys())
            after_fields = set(after_table.get("fields", {}).keys())
            
            added = after_fields - before_fields
            removed = before_fields - after_fields
            common = before_fields & after_fields
            
            has_changes = bool(added or removed or common)
            if has_changes:
                table_node = root.add_child(f"Table: {table_name}")
                
                if added:
                    add_node = table_node.add_child("Added fields")
                    for field in sorted(added):
                        add_node.add_child(f"+ {field}")
                
                if removed:
                    rem_node = table_node.add_child("Removed fields")
                    for field in sorted(removed):
                        rem_node.add_child(f"- {field}")
                
                if common:
                    # Check for modifications in common fields
                    mod_fields = []
                    for field in common:
                        if before_table.get("fields", {}).get(field) != after_table.get("fields", {}).get(field):
                            mod_fields.append(field)
                    
                    if mod_fields:
                        mod_node = table_node.add_child("Modified fields")
                        for field in sorted(mod_fields):
                            before_def = before_table.get("fields", {}).get(field)
                            after_def = after_table.get("fields", {}).get(field)
                            mod_node.add_child(f"~ {field}: {before_def} -> {after_def}")
    
    return root.render()
