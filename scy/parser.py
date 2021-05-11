import ast
from scy.tokenizer import Tokenizer
from scy.utils import find_line

from scy.tokens import BINARY_OPERATORS, COMPARISON_OPERATORS, TokenGroup, TokenType, Token, UNARY_OPERATORS


class Parser:
    tokens: list[Token]
    filename: str
    source: str
    current: int

    def __init__(self, tokens: list[Token], filename: str, source: str) -> None:
        self.tokens = tokens
        self.filename = filename
        self.source = source
        self.current = 0

    def expression(self) -> ast.expr:
        return self.comparison()

    def comparison(self) -> ast.expr:
        left: ast.expr = self.term()
        operators: list[ast.cmpop] = []
        remaining: list[ast.expr] = []
        while self.match(*TokenGroup.SINGLE_COMPARISON):
            operator = COMPARISON_OPERATORS[self.previous().type]()
            right = self.term()
            operators.append(operator)
            remaining.append(right)
        if operators:
            return ast.Compare(left, operators, remaining)
        else:
            return left

    def term(self) -> ast.expr:
        left = self.factor()
        while self.match(*TokenGroup.TERMS):
            operator = BINARY_OPERATORS[self.previous().type]()
            right = self.factor()
            left = ast.BinOp(left, operator, right)
        return left

    def factor(self) -> ast.expr:
        left = self.unary()
        while self.match(*TokenGroup.FACTORS):
            operator = BINARY_OPERATORS[self.previous().type]()
            right = self.unary()
            left = ast.BinOp(left, operator, right)
        return left

    def unary(self) -> ast.expr:
        if self.match(*TokenGroup.UNARY_LOW):
            operator = UNARY_OPERATORS[self.previous().type]()
            right = self.unary()
            return ast.UnaryOp(operator, right)
        return self.primary()

    def primary(self) -> ast.expr:
        if self.match(TokenType.FALSE):
            return ast.Constant(False)
        elif self.match(TokenType.TRUE):
            return ast.Constant(True)
        elif self.match(TokenType.NONE):
            return ast.Constant(None)
        elif self.match(*TokenGroup.LITERALS):
            return ast.Constant(self.previous().literal)
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr

    def match(self, *types: TokenType) -> bool:
        if any(self.check(type) for type in types):
            self.advance()
            return True
        return False

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> SyntaxError:
        return SyntaxError(message, (self.filename, token.line,
                                     token.column - 1,
                           find_line(self.source, token.index)))

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def parse(self, mode: str = 'exec') -> ast.AST:
        return self.expression()


def parse_tree(tokens: list[Token], mode: str = 'exec', filename: str = '<unknown>', source: str = '') -> ast.AST:
    parser: Parser = Parser(tokens, filename, source)
    return parser.parse(mode)
