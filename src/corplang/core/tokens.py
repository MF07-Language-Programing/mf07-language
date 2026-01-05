from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """
    Enum representing all possible token types in the Corplang language.
    """
    # JSON Structures
    NULL = "NULL"
    ARRAY = "ARRAY"
    OBJECT = "OBJECT"

    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    DOCSTRING = "DOCSTRING"
    FSTRING = "FSTRING"
    BOOLEAN = "BOOLEAN"

    # Identifiers
    IDENTIFIER = "IDENTIFIER"

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"

    # Comparison
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"

    # Logical
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # Assignment
    ASSIGN = "ASSIGN"

    # Keywords
    VAR = "VAR"
    FUNCTION = "FUNCTION"
    FN = "FN"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    IN = "IN"
    OF = "OF"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    TRY = "TRY"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    THROW = "THROW"

    # OOP
    CLASS = "CLASS"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    INTERFACE = "INTERFACE"
    ABSTRACT = "ABSTRACT"
    SUPER = "SUPER"
    STATIC = "STATIC"
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    CONTRACT = "CONTRACT"
    DRIVER = "DRIVER"
    PROTOCOL = "PROTOCOL"
    NEW = "NEW"
    THIS = "THIS"

    # Context Manager
    WITH = "WITH"

    # Corporate Data / AI
    DATASET = "DATASET"
    MODEL = "MODEL"
    PREDICT = "PREDICT"
    TRAIN = "TRAIN"
    ANALYZE = "ANALYZE"
    MIGRATION = "MIGRATION"
    IMPORT = "IMPORT"
    FROM = "FROM"
    AS = "AS"
    ASYNC = "ASYNC"
    AWAIT = "AWAIT"
    AGENT = "AGENT"
    RUN = "RUN"
    INTELLIGENCE = "INTELLIGENCE"
    CONTEXT = "CONTEXT"
    EXECUTION = "EXECUTION"
    ALLOW = "ALLOW"
    DENY = "DENY"
    PROVIDER = "PROVIDER"
    CAPABILITY = "CAPABILITY"
    HALLUCINATION = "HALLUCINATION"
    LOOP = "LOOP"
    USING = "USING"
    SERVE = "SERVE"
    STOP = "STOP"
    DELETE = "DELETE"
    GET = "GET"
    SET = "SET"
    AUTHENTICATION = "AUTHENTICATION"
    PROTECTED = "PROTECTED"

    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    QUESTION = "QUESTION"
    COMMA = "COMMA"
    DOT = "DOT"

    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    WHITESPACE = "WHITESPACE"


@dataclass(frozen=True)
class Token:
    """
    Represents a single token produced by the Lexer.

    Attributes:
        type (TokenType): The category of the token.
        value (str): The raw text value of the token.
        line (int): The line number where the token appears.
        column (int): The column number where the token starts.
    """
    type: TokenType
    value: str
    line: int
    column: int


__all__ = ["TokenType", "Token"]