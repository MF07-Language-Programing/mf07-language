from typing import List, Optional, Any
from src.corplang.compiler.lexer import Token, TokenType
from src.corplang.compiler.nodes import Program
import src.corplang.compiler.constants as constant
from src.corplang.core.config import config_manager, get_logger
from src.corplang.core.ui.terminal import ui


from src.corplang.compiler.sampler import ParserSampler


class Parser(ParserSampler):
    """
    Main entry point for the Corplang Parser.
    Uses specialized parsers from the constants namespace.
    """

    def __init__(self, tokens: List[Token], source_file: Optional[str] = None):
        self.stream = constant.TokenStream(tokens)
        self.source_file = source_file
        self.ctx = constant.PositionTracker(self.stream, source_file=source_file)
        self.logger = get_logger(__name__)
        self.compiler_view = config_manager.get("interpreter", {}).get("compiler_view", False)
        self._setup_context()

    def _log_node_creation(self, node_type: str, tok: Token):
        if self.compiler_view:
            msg = f"Creating {node_type} at line {tok.line}, col {tok.column} ('{tok.value}')"
            self.logger.debug(f"🔨 [NODE] {msg}")
            ui.status("Node", f"{node_type} {ui.theme.dim}(line {tok.line}){ui.theme.reset}", color=ui.theme.secondary)

    def _setup_context(self):
        """Wires up the context with specialized parser functions."""
        self.ctx.parse_type = lambda p=None: constant.parse_type_annotation(self.ctx, p)
        self.ctx.format_type = constant.format_type_annotation
        self.ctx.parse_expression = lambda p=None: constant.parse_expression(self.ctx, p)
        self.ctx.parse_statement = lambda p=None: constant.parse_statement(self.ctx, p)

    def parse(self) -> Program:
        """Parses the entire token stream into a Program node."""
        statements = []
        docstring = None
        if ui.enabled:
            ui.status("Starting", f"Compilation of {self.ctx.source_file or 'stream'}")
        if self.compiler_view:
            self.logger.debug("🚀 [PARSER] Starting compilation...")

        # Check for module docstring
        if self.stream.current and self.stream.current.type == TokenType.DOCSTRING:
            docstring = self.stream.current.value
            if self.compiler_view:
                self.logger.debug(f"📝 [DOC] Module docstring found: {repr(docstring[:50])}...")
            self.stream.advance()

        program = Program(
            statements=statements, 
            docstring=docstring, 
            line=1, 
            column=1,
            file_path=self.ctx.source_file
        )

        while not self.stream.eof():
            start_pos = self.stream.pos
            try:
                stmt = self.parse_top_level(program)
                if stmt:
                    if self.compiler_view:
                        self.logger.debug(f"✅ [STMT] Added top-level statement: {type(stmt).__name__}")
                    statements.append(stmt)
                elif self.stream.current and self.stream.current.type == TokenType.RBRACE:
                    if self.compiler_view:
                        self.logger.error(f"❌ [ERROR] Unexpected '}}' at {self.stream.current.line}:{self.stream.current.column}")
                    self.stream.advance()
            except constant.SyntaxException as e:
                self.ctx.error(str(e))
                if self.compiler_view:
                    self.logger.error(f"❌ [SYNTAX] {str(e)}")
                if self.stream.pos == start_pos:
                    self.stream.advance()
            except Exception as e:
                self.ctx.error(f"Unexpected error: {str(e)}")
                if self.compiler_view:
                    self.logger.error(f"💥 [FATAL] {str(e)}")
                if self.stream.pos == start_pos:
                    self.stream.advance()

            # Safeguard against infinite loops
            if self.stream.pos == start_pos and not self.stream.eof():
                if self.compiler_view:
                    self.logger.warn(f"⚠️ [WARN] Parser stuck at {self.stream.current}. Advancing...")
                self.stream.advance()

        if self.compiler_view:
            self.logger.debug(f"🏁 [PARSER] Compilation finished. Total nodes: {len(statements)}")
        if ui.enabled:
            ui.success(f"Compilation finished. Total nodes: {len(statements)}")

        self._program = program
        return program

    def parse_top_level(self, parent: Optional[Any] = None) -> Any:
        """Dispatches to specialized top-level declarations or statements."""
        # Skip blank lines/newlines to align on real tokens
        while self.stream.current and self.stream.current.type == TokenType.NEWLINE:
            self.stream.advance()
        tok = self.stream.current
        if not tok:
            return None

        if self.compiler_view:
            self.logger.debug(f"🔍 [PARSE] Dispatching top-level token: {tok.type} ('{tok.value}')")

        # Handle modifiers
        modifiers = []
        while self.stream.current and self.stream.current.type in (
            TokenType.PUBLIC, TokenType.PRIVATE, TokenType.STATIC, TokenType.ABSTRACT, TokenType.ASYNC
        ):
            modifiers.append(self.stream.advance())

        tok = self.stream.current
        if not tok: return None

        is_async = any(m.type == TokenType.ASYNC for m in modifiers)
        is_static = any(m.type == TokenType.STATIC for m in modifiers)
        is_private = any(m.type == TokenType.PRIVATE for m in modifiers)
        is_abstract = any(m.type == TokenType.ABSTRACT for m in modifiers)

        if tok.type in (TokenType.FUNCTION, TokenType.FN):
            self._log_node_creation("FunctionDeclaration", tok)
            return constant.parse_function_declaration(self.ctx, parent, is_async=is_async)
        elif tok.type == TokenType.CLASS:
            self._log_node_creation("ClassDeclaration", tok)
            return constant.parse_class_declaration(self.ctx, parent)
        elif tok.type == TokenType.AGENT:
            self._log_node_creation("AgentDefinition", tok)
            return constant.parse_agent_statement(self.ctx, parent)
        elif tok.type == TokenType.IMPORT:
            self._log_node_creation("ImportDeclaration", tok)
            return constant.parse_import_declaration(self.ctx, parent)
        elif tok.type == TokenType.FROM:
            self._log_node_creation("FromImportDeclaration", tok)
            return constant.parse_from_import_declaration(self.ctx, parent)
        elif tok.type == TokenType.INTERFACE:
            self._log_node_creation("InterfaceDeclaration", tok)
            return constant.parse_interface_declaration(self.ctx, parent)
        elif tok.type == TokenType.CONTRACT:
            self._log_node_creation("ContractDeclaration", tok)
            return constant.parse_contract_declaration(self.ctx, parent)
        elif tok.type == TokenType.DRIVER:
            self._log_node_creation("ClassDeclaration", tok)
            # Use parse_class_declaration for drivers since they are classes
            # We might need a specialized parse_driver_declaration later
            return constant.parse_class_declaration(self.ctx, parent)
        elif tok.type == TokenType.MODEL:
            self._log_node_creation("ModelDeclaration", tok)
            return constant.parse_model_declaration(self.ctx, parent)
        elif tok.type == TokenType.MIGRATION:
            self._log_node_creation("MigrationDeclaration", tok)
            return constant.parse_migration_declaration(self.ctx, parent)
        
        return constant.parse_statement(self.ctx, parent)
