"""Semantic scope analysis for conditional variable declarations."""

from typing import Any, Optional, Set, Dict, List, Tuple


class VariableDeclaration:
    """Information about a variable declaration."""

    def __init__(self, name: str, line: int, column: int, type_annotation: Optional[str] = None):
        self.name = name
        self.line = line
        self.column = column
        self.type_annotation = type_annotation


class ScopeAnalyzer:
    """Analyzes variable declarations in conditional blocks."""

    @staticmethod
    def _collect_var_declarations(statements: List[Any]) -> Dict[str, VariableDeclaration]:
        """Collect all variable declarations in a statement list."""
        decls = {}
        if not statements:
            return decls

        for stmt in statements:
            if stmt is None:
                continue

            if type(stmt).__name__ == "VarDeclaration":
                name = getattr(stmt, "name", None)
                if name:
                    decls[name] = VariableDeclaration(
                        name=name,
                        line=getattr(stmt, "line", 0),
                        column=getattr(stmt, "column", 0),
                        type_annotation=getattr(stmt, "type_annotation", None)
                    )

        return decls

    @staticmethod
    def _uses_variable_before_declaration(name: str, statements: List[Any], decl_index: int) -> bool:
        """Check if a variable is used before its declaration in a statement list."""
        if decl_index == 0:
            return False

        for stmt in statements[:decl_index]:
            if ScopeAnalyzer._statement_references_variable(stmt, name):
                return True

        return False

    @staticmethod
    def _statement_references_variable(stmt: Any, name: str) -> bool:
        """Check if a statement references a specific variable."""
        if stmt is None:
            return False

        stmt_type = type(stmt).__name__

        if stmt_type == "Identifier":
            return getattr(stmt, "name", None) == name

        if stmt_type == "VarDeclaration":
            # Check the initialization value
            value = getattr(stmt, "value", None)
            return ScopeAnalyzer._statement_references_variable(value, name)

        if stmt_type == "Assignment":
            target = getattr(stmt, "target", None)
            value = getattr(stmt, "value", None)
            return (ScopeAnalyzer._statement_references_variable(target, name) or
                    ScopeAnalyzer._statement_references_variable(value, name))

        if stmt_type in ("BinaryOp", "UnaryOp", "CallExpression", "MemberExpression"):
            left = getattr(stmt, "left", None)
            right = getattr(stmt, "right", None)
            object_expr = getattr(stmt, "object", None)
            property_expr = getattr(stmt, "property", None)
            operand = getattr(stmt, "operand", None)
            arguments = getattr(stmt, "arguments", [])
            func = getattr(stmt, "func", None)

            if ScopeAnalyzer._statement_references_variable(left, name):
                return True
            if ScopeAnalyzer._statement_references_variable(right, name):
                return True
            if ScopeAnalyzer._statement_references_variable(object_expr, name):
                return True
            if ScopeAnalyzer._statement_references_variable(property_expr, name):
                return True
            if ScopeAnalyzer._statement_references_variable(operand, name):
                return True
            if ScopeAnalyzer._statement_references_variable(func, name):
                return True

            if arguments:
                for arg in arguments:
                    if ScopeAnalyzer._statement_references_variable(arg, name):
                        return True

        if stmt_type in ("IfStatement", "WhileStatement", "ForStatement"):
            condition = getattr(stmt, "condition", None)
            if ScopeAnalyzer._statement_references_variable(condition, name):
                return True

        if stmt_type == "ReturnStatement":
            value = getattr(stmt, "value", None)
            return ScopeAnalyzer._statement_references_variable(value, name)

        body = getattr(stmt, "body", None)
        statements_attr = getattr(stmt, "statements", None)
        then_stmt = getattr(stmt, "then_stmt", None)
        else_stmt = getattr(stmt, "else_stmt", None)

        for container in [body, statements_attr, then_stmt, else_stmt]:
            if container:
                if isinstance(container, list):
                    for item in container:
                        if ScopeAnalyzer._statement_references_variable(item, name):
                            return True
                else:
                    if ScopeAnalyzer._statement_references_variable(container, name):
                        return True

        return False

    @staticmethod
    def can_hoist_from_conditional(if_node: Any) -> Tuple[bool, Optional[Dict[str, VariableDeclaration]]]:
        """
        Determine if variables can be hoisted from conditional branches.
        
        Returns:
            (can_hoist, hoisted_vars) - whether hoisting is safe, and which vars to hoist
        """
        then_stmt = getattr(if_node, "then_stmt", None)
        else_stmt = getattr(if_node, "else_stmt", None)

        if not then_stmt or not else_stmt:
            return False, None

        then_decls = ScopeAnalyzer._collect_var_declarations(then_stmt)
        else_decls = ScopeAnalyzer._collect_var_declarations(else_stmt)

        if not then_decls or not else_decls:
            return False, None

        common_vars = set(then_decls.keys()) & set(else_decls.keys())

        if not common_vars:
            return False, None

        hoisted_vars = {}
        for var_name in common_vars:
            then_type = then_decls[var_name].type_annotation
            else_type = else_decls[var_name].type_annotation

            if then_type != else_type:
                continue

            hoisted_vars[var_name] = then_decls[var_name]

        return len(hoisted_vars) > 0, hoisted_vars if hoisted_vars else None

    @staticmethod
    def hoist_variables(if_node: Any, parent_statements: List[Any], if_index: int) -> Tuple[Any, List[Any]]:
        """
        Transform an if statement by hoisting variable declarations.
        
        Returns:
            (modified_if_node, modified_parent_statements)
        """
        can_hoist, hoisted_vars = ScopeAnalyzer.can_hoist_from_conditional(if_node)

        if not can_hoist or not hoisted_vars:
            return if_node, parent_statements

        hoisted_var_names = set(hoisted_vars.keys())

        from src.corplang.compiler.nodes import VarDeclaration, Literal

        hoisted_decls = []
        for var_name, var_info in hoisted_vars.items():
            null_literal = Literal(
                value=None,
                line=var_info.line,
                column=var_info.column,
                file_path=getattr(if_node, "file_path", None),
                parent=None
            )

            hoisted_decl = VarDeclaration(
                name=var_name,
                value=null_literal,
                type_annotation=var_info.type_annotation,
                line=var_info.line,
                column=var_info.column,
                file_path=getattr(if_node, "file_path", None),
                parent=None
            )
            hoisted_decls.append(hoisted_decl)
            null_literal.parent = hoisted_decl

        # Remove hoisted variables from both branches and replace with assignments
        modified_if = ScopeAnalyzer._remove_hoisted_declarations(if_node, hoisted_var_names)

        # Insert hoisted declarations before the if statement
        new_statements = parent_statements[:if_index] + hoisted_decls + parent_statements[if_index:]

        return modified_if, new_statements

    @staticmethod
    def _remove_hoisted_declarations(if_node: Any, hoisted_var_names: Set[str]) -> Any:
        """Remove hoisted variable declarations from both branches, replacing with assignments."""

        then_stmt = getattr(if_node, "then_stmt", None)
        else_stmt = getattr(if_node, "else_stmt", None)

        if then_stmt:
            then_stmt = ScopeAnalyzer._replace_declarations_with_assignments(then_stmt, hoisted_var_names)
            if_node.then_stmt = then_stmt

        if else_stmt:
            else_stmt = ScopeAnalyzer._replace_declarations_with_assignments(else_stmt, hoisted_var_names)
            if_node.else_stmt = else_stmt

        return if_node

    @staticmethod
    def _replace_declarations_with_assignments(statements: List[Any], hoisted_var_names: Set[str]) -> List[Any]:
        """Convert VarDeclarations to Assignments for hoisted variables."""
        from src.corplang.compiler.nodes import Assignment, Identifier

        if not statements:
            return statements

        result = []
        for stmt in statements:
            if stmt is None:
                continue

            if type(stmt).__name__ == "VarDeclaration":
                name = getattr(stmt, "name", None)
                if name in hoisted_var_names:
                    # Convert to assignment
                    target = Identifier(
                        name=name,
                        line=getattr(stmt, "line", 0),
                        column=getattr(stmt, "column", 0),
                        file_path=getattr(stmt, "file_path", None),
                        parent=None
                    )

                    assignment = Assignment(
                        target=target,
                        value=getattr(stmt, "value", None),
                        line=getattr(stmt, "line", 0),
                        column=getattr(stmt, "column", 0),
                        file_path=getattr(stmt, "file_path", None),
                        parent=None
                    )
                    target.parent = assignment
                    result.append(assignment)
                else:
                    result.append(stmt)
            else:
                result.append(stmt)

        return result


class BlockScopeHoister:
    """Applies hoisting transformation to blocks containing conditionals."""

    @staticmethod
    def apply_hoisting(statements: List[Any], parent: Any = None) -> List[Any]:
        """Apply hoisting to all if statements in a block."""
        if not statements:
            return statements

        # Don't hoist inside loops - each iteration needs fresh variables
        parent_type = type(parent).__name__ if parent else None
        if parent_type in ("ForStatement", "ForInStatement", "ForOfStatement", "WhileStatement"):
            return statements

        result = []
        i = 0
        while i < len(statements):
            stmt = statements[i]
            if stmt and type(stmt).__name__ == "IfStatement":
                modified_if, new_statements = ScopeAnalyzer.hoist_variables(stmt, statements, i)

                if len(new_statements) != len(statements):
                    return new_statements
                else:
                    result.append(modified_if)
            else:
                result.append(stmt)
            i += 1

        return result
