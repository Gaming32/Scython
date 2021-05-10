from typing import Any

from scy.tokens import TokenType, Token
from scy.utils import find_line


class Tokenizer:
    source: str
    filename: str
    tokens: list[Token]
    start: int
    current: int
    line: int
    column: int

    def __init__(self, source: str, filename: str = '<unknown>') -> None:
        self.source = source
        self.filename = filename
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan()
        
        self.tokens.append(Token(TokenType.EOF, '', self.line))
        return self.tokens

    def error(self, text: str) -> SyntaxError:
        return SyntaxError(text, (self.filename, self.line, self.column - 1,
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
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c == '/':
            self.add_token(TokenType.SLASH_SLASH if self.match('/') else TokenType.SLASH)
        elif c == '#':
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()
        
        elif c in ' \r\t':
            pass

        elif c == '\n':
            self.line += 1
            self.column = 1

        elif c in '"\'':
            self.string(c)

        elif self.is_digit(c):
            self.number()

        else:
            raise self.error('Unexpected character.')

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
            return self.add_token_literal(TokenType.DECIMAL, float(self.source[self.start:self.current]))
        self.add_token_literal(TokenType.INTEGER, int(self.source[self.start:self.current]))

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
                raise self.error(f'Invalid hex string: {data!r}.') from None
        elif code == 'u':
            self.advance()
            data = self.advance()
            for _ in range(2):
                data += self.advance()
            data += self.peek()
            try:
                return chr(int(data, 16))
            except ValueError:
                raise self.error(f'Invalid hex string: {data!r}.') from None
        elif code == 'U':
            self.advance()
            data = self.advance()
            for _ in range(6):
                data += self.advance()
            data += self.peek()
            try:
                return chr(int(data, 16))
            except ValueError:
                raise self.error(f'Invalid hex string: {data!r}.') from None

    def string(self, end: str) -> None:
        result = ''
        while self.peek() != end and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
                result += '\n'
            elif self.peek() == '\\':
                result += self.escape()
            else:
                result += self.peek()
            self.advance()
        if self.is_at_end():
            raise self.error('Unterminated string.')
        self.advance()
        self.add_token_literal(TokenType.STRING, result)

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        self.column += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        if self.is_at_end():
            raise self.error('Unexpected EOF.')
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def add_token(self, type: TokenType) -> None:
        self.add_token_literal(type, None)

    def add_token_literal(self, type: TokenType, literal: Any) -> None:
        text: str = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, self.line, literal))


def tokenize(source: str, filename: str = '<unknown>') -> list[Token]:
    tokenizer = Tokenizer(source, filename)
    return tokenizer.tokenize()
