from typing import Any

from scy import exceptions
from scy.tokens import KEYWORDS, Token, TokenType
from scy.utils import find_line


class Tokenizer:
    source: str
    filename: str
    tokens: list[Token]
    start: int
    current: int
    line: int
    start_column: int
    column: int

    def __init__(self, source: str, filename: str = '<unknown>') -> None:
        self.source = source
        self.filename = filename
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.start_column = 0
        self.column = 0

    def tokenize(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.start_column = self.column
            self.scan()

        self.tokens.append(Token(TokenType.EOF, '', self.line, self.start_column, self.current))
        return self.tokens

    def error(self, text: str) -> SyntaxError:
        return SyntaxError(text, (self.filename, self.line, self.start_column + 1,
                           find_line(self.source, self.current)))

    def scan(self) -> None:
        c: str = self.advance()
        if c == '(': # I can't wait for Python 3.10 to have match..case lol
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == '~':
            self.add_token(TokenType.TILDE)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '%':
            self.add_token(TokenType.PERCENT)
        elif c == '^':
            self.add_token(TokenType.CARET)
        elif c == ':':
            self.add_token(TokenType.COLON)
        elif c == '@':
            self.add_token(TokenType.AT)
        elif c == '.':
            self.ellipsis()
        elif c == '*':
            self.add_token(TokenType.STAR_STAR if self.match_('*') else TokenType.STAR)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match_('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match_('=') else TokenType.EQUAL)
        elif c == '<':
            if self.match_('='):
                tok = TokenType.LESS_EQUAL
            elif self.match_('<'):
                tok = TokenType.LESS_LESS
            else:
                tok = TokenType.LESS
            self.add_token(tok)
        elif c == '>':
            if self.match_('='):
                tok = TokenType.GREATER_EQUAL
            elif self.match_('>'):
                tok = TokenType.GREATER_GREATER
            else:
                tok = TokenType.GREATER
            self.add_token(tok)
        elif c == '/':
            self.add_token(TokenType.SLASH_SLASH if self.match_('/') else TokenType.SLASH)
        elif c == '&':
            self.add_token(TokenType.AMPERSAND_AMPERSAND if self.match_('&') else TokenType.AMPERSAND)
        elif c == '|':
            self.add_token(TokenType.PIPE_PIPE if self.match_('|') else TokenType.PIPE)
        elif c == '#':
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()

        elif c in ' \r\t':
            pass

        elif c == '\n':
            self.line += 1
            self.column = 0

        elif c in '"\'':
            self.string(c)

        elif self.is_digit(c):
            self.number()
        elif self.is_alpha(c):
            self.identifier()

        else:
            raise self.error(exceptions.UNEXPECTED_CHARACTER)

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        text: str = self.source[self.start:self.current]
        type: TokenType = KEYWORDS.get(text, TokenType.IDENTIFIER)
        if type is None:
            raise self.error(exceptions.RESERVED_KEYWORD % text)
        self.add_token(type)

    def ellipsis(self) -> None:
        count = 1
        while count < 3 and self.peek() == '.':
            count += 1
            self.advance()
        if count == 3:
            self.add_token(TokenType.ELLIPSIS)
        else:
            for _ in range(count):
                self.add_token(TokenType.DOT)

    def number(self) -> None:
        base = 10
        if self.previous() == '0':
            modifier = self.advance().lower()
            if modifier == 'x':
                base = 16
            elif modifier == 'b':
                base = 2
            elif modifier == 'o':
                base = 8
            else:
                raise self.error(exceptions.INVALID_BASE_MODIFIER % modifier)
        while self.is_digit(self.peek()) or self.peek() == '_':
            self.advance()
        if self.peek() == '.':
            if base != 10:
                raise self.error(exceptions.ALTERNATE_BASE_FLOAT)
            self.advance()
            if self.is_digit(self.peek()):
                while self.is_digit(self.peek()) or self.peek() == '_':
                    self.advance()
            if self.previous() == '_':
                raise self.error(exceptions.UNDERSCORE_ENDED_NUMBER)
            return self.add_token_literal(TokenType.DECIMAL, float(self.source[self.start:self.current]))
        if self.previous() == '_':
            raise self.error(exceptions.UNDERSCORE_ENDED_NUMBER)
        self.add_token_literal(TokenType.INTEGER, int(self.source[self.start:self.current], base))

    def escape(self) -> str:
        self.advance()
        code = self.peek()
        if code == 'n':
            return '\n'
        elif code == 't':
            return '\t'
        elif code == '"':
            return '"'
        elif code == "'":
            return "'"
        elif code == 'x':
            self.advance()
            data = self.advance() + self.peek()
            try:
                return chr(int(data, 16))
            except ValueError:
                raise self.error(exceptions.INVALID_HEX_STRING % data) from None
        elif code == 'u':
            self.advance()
            data = self.advance()
            for _ in range(2):
                data += self.advance()
            data += self.peek()
            try:
                return chr(int(data, 16))
            except ValueError:
                raise self.error(exceptions.INVALID_HEX_STRING % data) from None
        elif code == 'U':
            self.advance()
            data = self.advance()
            for _ in range(6):
                data += self.advance()
            data += self.peek()
            try:
                return chr(int(data, 16))
            except ValueError:
                raise self.error(exceptions.INVALID_HEX_STRING % data) from None

    def string(self, end: str) -> None:
        result = ''
        while self.peek() != end and not self.is_at_end():
            if self.peek() == '\n':
                raise self.error(exceptions.MULTILINE_STRINGS_NOT_SUPPORTED)
            elif self.peek() == '\\':
                result += self.escape()
            else:
                result += self.peek()
            self.advance()
        if self.is_at_end():
            raise self.error(exceptions.EOF_DURING_STRING)
        self.advance()
        self.add_token_literal(TokenType.STRING, result)

    def match_(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        self.column += 1
        return True

    def previous(self) -> str:
        return self.source[self.current - 1]

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def is_alpha(self, c: str) -> bool:
        return ((c >= 'a' and c <= 'z')
             or (c >= 'A' and c <= 'Z')
             or c == '_')

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        if self.is_at_end():
            raise self.error(exceptions.UNEXPECTED_EOF)
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def add_token(self, type: TokenType) -> None:
        self.add_token_literal(type, None)

    def add_token_literal(self, type: TokenType, literal: Any) -> None:
        text: str = self.source[self.start:self.current]
        self.tokens.append(Token(
            type,
            text,
            self.line,
            self.start_column,
            self.current,
            literal
        ))


def tokenize(source: str, filename: str = '<unknown>') -> list[Token]:
    tokenizer = Tokenizer(source, filename)
    return tokenizer.tokenize()
