import os
from typing import Optional, Dict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.corplang.compiler.lexer import Lexer

class LexerSampler:
    """
    Mixin class that provides sampling and reporting capabilities for the Lexer.
    """

    @property
    def __tokens__(self) -> str:
        """
        Formats a list of tokens into an elegant, detailed report.
        """
        # This assumes 'self' will be an instance of Lexer
        # We access self.tokens and self.text
        tokens = getattr(self, "tokens", [])
        source_code = getattr(self, "text", "")

        if not tokens:
            return "No tokens found."

        # Statistics
        stats: Dict[str, int] = {}
        for t in tokens:
            stats[t.type.name] = stats.get(t.type.name, 0) + 1

        report = "### Token Statistics\n"
        report += f"{'Type':<20} | {'Count':<10}\n"
        report += "-" * 33 + "\n"
        for t_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            report += f"{t_type:<20} | {count:<10}\n"
        report += "\n"

        report += "### Detailed Token Stream\n"
        header = f"{'Type':<20} | {'Value':<30} | {'Line':<5} | {'Col':<5}"
        report += header + "\n"
        report += "-" * len(header) + "\n"

        # Group tokens by line for context if a source is provided
        lines = source_code.splitlines() if source_code else []
        current_line_idx = -1

        for token in tokens:
            if source_code and token.line != current_line_idx:
                current_line_idx = token.line
                if 1 <= current_line_idx <= len(lines):
                    report += f"\n[Line {current_line_idx}]: {lines[current_line_idx-1]}\n"
                    report += "~" * (len(lines[current_line_idx-1]) + 11) + "\n"

            val = repr(token.value)
            report += f"{token.type.name:<20} | {val:<30} | {token.line:<5} | {token.column:<5}\n"

        return report

    def as_view(self, output_path: Optional[str] = None) -> str:
        """
        Generates an elegant report for the current Lexer instance.
        If output_path is provided, saves the report to a file.
        """
        # This assumes 'self' will be an instance of Lexer
        if not getattr(self, "tokens", []) and hasattr(self, "tokenize"):
            self.tokenize()

        formatted = self.__tokens__
        
        report = "Lexer Elegant Instance Report\n"
        report += "=" * 30 + "\n\n"
        report += formatted

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report

    @classmethod
    def from_file(cls, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Utility to tokenize a single file and return/save its report.
        """
        from src.corplang.compiler.lexer import Lexer
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lexer = Lexer(content)
            # Lexer now inherits from LexerSampler, so it has as_view
            report_header = f"Lexer Elegant Sample for: {file_path}\n"
            report_header += "=" * (26 + len(file_path)) + "\n\n"
            
            report = report_header + lexer.as_view()

            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
            
            return report
        except Exception as e:
            return f"Error sampling file {file_path}: {str(e)}"

    @classmethod
    def from_directory(cls, dir_path: str, extension: str = ".corp", output_path: Optional[str] = None) -> str:
        """
        Tokenizes all files with the given extension in a directory.
        """
        reports = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(extension):
                    full_path = os.path.join(root, file)
                    reports.append(cls.from_file(full_path))
        
        combined_report = "\n\n" + ("#" * 50) + "\n\n"
        final_report = combined_report.join(reports)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_report)
        
        return final_report


class ParserSampler:
    """
    Mixin class that provides sampling and reporting capabilities for the Parser.
    """

    def _format_node(self, node: Any, indent: int = 0, field_name: Optional[str] = None, is_last: bool = True, prefix: str = "") -> str:
        """
        Recursively formats an AST node into a professional, compact tree structure.
        """
        from dataclasses import is_dataclass, fields
        from src.corplang.core.ui.terminal import ui

        # Colors and symbols
        T = ui.theme
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        # Build the current line prefix (field name + connector)
        line_start = prefix + connector
        field_part = f"{T.secondary}{field_name}{T.reset}=" if field_name else ""

        # Handle None
        if node is None:
            return f"{line_start}{field_part}{T.dim}None{T.reset}\n"

        # Handle Lists
        if isinstance(node, list):
            if not node:
                return f"{line_start}{field_part}[]\n"
            
            res = f"{line_start}{field_part}\n"
            for i, item in enumerate(node):
                last_item = i == len(node) - 1
                res += self._format_node(item, indent + 1, is_last=last_item, prefix=child_prefix)
            return res

        # Handle non-dataclass (primitives)
        if not is_dataclass(node):
            val_repr = repr(node)
            if isinstance(node, str):
                val_repr = f"{T.success}{val_repr}{T.reset}"
            elif isinstance(node, (int, float)):
                val_repr = f"{T.warning}{val_repr}{T.reset}"
            elif isinstance(node, bool):
                val_repr = f"{T.primary}{val_repr}{T.reset}"
            return f"{line_start}{field_part}{val_repr}\n"

        # Handle AST Nodes
        node_name = f"{T.bold}{T.primary}{type(node).__name__}{T.reset}"
        
        # Determine fields to show
        node_fields = fields(node)
        display_fields = [f for f in node_fields if f.name not in ('parent', 'line', 'column', 'file_path')]
        
        # Optimization: Compact representation for nodes with only one or two simple fields
        # (e.g. Literal(value=1), Name(id='x'))
        simple_values = []
        is_simple = True
        for f in display_fields:
            val = getattr(node, f.name)
            if is_dataclass(val) or isinstance(val, list):
                is_simple = False
                break
            simple_values.append(f"{T.secondary}{f.name}{T.reset}={repr(val)}")
        
        if is_simple and len(simple_values) <= 2:
            fields_str = ", ".join(simple_values)
            return f"{line_start}{field_part}{node_name}({fields_str})\n"

        # Detailed view for complex nodes
        res = f"{line_start}{field_part}{node_name}\n"
        
        # Filter out some noise: only show None if it's not a common optional metadata
        visible_fields = []
        for f in display_fields:
            val = getattr(node, f.name)
            if val is None and f.name in ('docstring', 'type_annotation', 'finally_block', 'target', 'is_async'):
                continue
            visible_fields.append((f.name, val))

        for i, (name, val) in enumerate(visible_fields):
            last_field = i == len(visible_fields) - 1
            res += self._format_node(val, indent + 1, field_name=name, is_last=last_field, prefix=child_prefix)
        
        return res

    def as_view(self, output_path: Optional[str] = None) -> str:
        """
        Generates a professional AST report for the current Parser instance.
        """
        from src.corplang.core.ui.terminal import ui
        T = ui.theme
        
        program = getattr(self, "_program", None)
        if program is None and hasattr(self, "parse"):
            program = self.parse()
        
        if program is None:
            return f"{T.error}No program parsed.{T.reset}"

        header = f"{T.bold}{T.primary}Corplang Professional AST View{T.reset}\n"
        header += f"{T.dim}{'=' * 40}{T.reset}\n"
        
        # Start formatting from the Program node
        # We use a custom initial call to avoid the first '└── ' if possible, or just let it be.
        # Let's make it look like a root.
        ast_tree = self._format_node(program, is_last=True, prefix="")
        
        report = header + ast_tree

        if output_path:
            # Strip ANSI codes for file output
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            clean_report = ansi_escape.sub('', report)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(clean_report)
        
        return report

    @classmethod
    def from_file(cls, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Parses a single file and returns/saves its AST report.
        """
        from src.corplang.compiler.lexer import Lexer
        from src.corplang.compiler.parser import Parser
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lexer = Lexer(content)
            tokens = lexer.tokenize()
            parser = Parser(tokens, source_file=file_path)
            
            report_header = f"Parser Elegant Sample for: {file_path}\n"
            report_header += "=" * (27 + len(file_path)) + "\n\n"
            
            report = report_header + parser.as_view()

            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
            
            return report
        except Exception as e:
            import traceback
            from src.corplang.tools.diagnostics import safe_message
            return f"Error sampling file {file_path}: {safe_message(e)}\n{traceback.format_exc()}"

    @classmethod
    def from_directory(cls, dir_path: str, extension: str = ".mp", output_path: Optional[str] = None) -> str:
        """
        Parses all files with the given extension in a directory.
        """
        reports = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(extension):
                    full_path = os.path.join(root, file)
                    reports.append(cls.from_file(full_path))
        
        combined_report = "\n\n" + ("#" * 50) + "\n\n"
        final_report = combined_report.join(reports)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_report)
        
        return final_report
