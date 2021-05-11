import ast
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional


class TokenType(Enum):
    # Single-character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    STAR = auto()

    # One or two character tokens.
    AMPERSAND = auto()
    AMPERSAND_AMPERSAND = auto()
    PIPE = auto()
    PIPE_PIPE = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    SLASH = auto()
    SLASH_SLASH = auto()

    # Literals.
    IDENTIFIER = auto()
    STRING = auto()
    INTEGER = auto()
    DECIMAL = auto()

    # Keywords.
    ASSERT = auto()
    ASYNC = auto()
    BREAK = auto()
    CATCH = auto()
    CLASS = auto()
    CONTINUE = auto()
    DEF = auto()
    DEL = auto()
    ELSE = auto()
    FALSE = auto()
    FINALLY = auto()
    FOR = auto()
    FROM = auto()
    GLOBAL = auto()
    IF = auto()
    IMPORT = auto()
    IN = auto()
    IS = auto()
    NONE = auto()
    NONLOCAL = auto()
    RAISE = auto()
    RETURN = auto()
    TRUE = auto()
    TRY = auto()
    WHILE = auto()
    WITH = auto()
    YIELD = auto()

    EOF = auto()


@dataclass(init=True, repr=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
    index: int
    literal: Any = None


class TokenGroup:
    SINGLE_COMPARISON = {
        TokenType.BANG_EQUAL,
        TokenType.EQUAL_EQUAL,
        TokenType.LESS,
        TokenType.LESS_EQUAL,
        TokenType.GREATER,
        TokenType.GREATER_EQUAL,
        TokenType.IS,
        TokenType.IN,
    }
    TERMS = {
        TokenType.MINUS,
        TokenType.PLUS,
    }
    FACTORS = {
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.SLASH_SLASH,
    }
    UNARY_LOW = {
        TokenType.MINUS,
        TokenType.PLUS,
    }
    LITERALS = {
        TokenType.INTEGER,
        TokenType.DECIMAL,
        TokenType.STRING,
    }


KEYWORDS: dict[str, Optional[TokenType]] = {
    'and':      None,
    'as':       None,
    'assert':   TokenType.ASSERT,
    'async':    TokenType.ASYNC,
    'break':    TokenType.BREAK,
    'class':    TokenType.CLASS,
    'continue': TokenType.CONTINUE,
    'def':      TokenType.DEF,
    'del':      TokenType.DEL,
    'elif':     None,
    'else':     TokenType.ELSE,
    'except':   None,
    'false':    TokenType.FALSE,
    'False':    TokenType.FALSE,
    'finally':  TokenType.FINALLY,
    'for':      TokenType.FOR,
    'from':     TokenType.FROM,
    'global':   TokenType.GLOBAL,
    'if':       TokenType.IF,
    'import':   TokenType.IMPORT,
    'in':       TokenType.IN,
    'is':       TokenType.IS,
    'lambda':   None,
    'None':     TokenType.NONE,
    'nonlocal': TokenType.NONLOCAL,
    'not':      None,
    'or':       None,
    'pass':     None,
    'raise':    TokenType.RAISE,
    'return':   TokenType.RETURN,
    'true':     TokenType.TRUE,
    'True':     TokenType.TRUE,
    'try':      TokenType.TRY,
    'while':    TokenType.WHILE,
    'with':     TokenType.WITH,
    'yield':    TokenType.YIELD,
}

COMPARISON_OPERATORS: dict[TokenType, ast.cmpop] = {
    TokenType.LESS:          ast.Lt,
    TokenType.LESS_EQUAL:    ast.LtE,
    TokenType.GREATER:       ast.Gt,
    TokenType.GREATER_EQUAL: ast.GtE,
    TokenType.EQUAL_EQUAL:   ast.Eq,
    TokenType.BANG_EQUAL:    ast.NotEq,
}

BINARY_OPERATORS: dict[TokenType, ast.operator] = {
    TokenType.STAR:  ast.Mult,
    TokenType.SLASH: ast.Div,
    TokenType.PLUS:  ast.Add,
    TokenType.MINUS: ast.Sub,
}

UNARY_OPERATORS: dict[TokenType, ast.operator] = {
    TokenType.PLUS:  ast.UAdd,
    TokenType.MINUS: ast.USub,
    TokenType.BANG:  ast.Not,
}
