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
        return self.or_()

    def or_(self) -> ast.expr:
        left = self.and_()
        if self.match_(TokenType.PIPE_PIPE):
            values = [left, self.and_()]
            while self.match_(TokenType.PIPE_PIPE):
                values.append(self.and_())
            return ast.BoolOp(ast.Or(), values)
        return left

    def and_(self) -> ast.expr:
        left = self.not_()
        if self.match_(TokenType.AMPERSAND_AMPERSAND):
            values = [left, self.not_()]
            while self.match_(TokenType.AMPERSAND_AMPERSAND):
                values.append(self.not_())
            return ast.BoolOp(ast.And(), values)
        return left

    def not_(self) -> ast.expr:
        if self.match_(TokenType.BANG):
            right = self.comparison()
            return ast.UnaryOp(ast.Not(), right)
        return self.comparison()

    def comparison(self) -> ast.expr:
        left: ast.expr = self.bit_or()
        operators: list[ast.cmpop] = []
        extra: list[ast.expr] = []
        while self.match_(*TokenGroup.SINGLE_COMPARISON, TokenType.NOT):
            if self.previous().type == TokenType.IS:
                if self.match_(TokenType.NOT):
                    operator = ast.IsNot()
                else:
                    operator = ast.Is()
            elif self.previous().type == TokenType.NOT:
                self.consume(TokenType.IN, "'in' must follow 'not' in comparison.")
                operator = ast.NotIn()
            else:
                operator = COMPARISON_OPERATORS[self.previous().type]()
            right = self.bit_or()
            operators.append(operator)
            extra.append(right)
        if operators:
            return ast.Compare(left, operators, extra)
        else:
            return left

    def bit_or(self):
        left = self.bit_xor()
        while self.match_(TokenType.PIPE):
            right = self.bit_xor()
            left = ast.BinOp(left, ast.BitOr(), right)
        return left

    def bit_xor(self):
        left = self.bit_and()
        while self.match_(TokenType.CARET):
            right = self.bit_and()
            left = ast.BinOp(left, ast.BitXor(), right)
        return left

    def bit_and(self):
        left = self.bit_shift()
        while self.match_(TokenType.AMPERSAND):
            right = self.bit_shift()
            left = ast.BinOp(left, ast.BitAnd(), right)
        return left

    def bit_shift(self):
        left = self.term()
        while self.match_(*TokenGroup.BIT_SHIFT):
            operator = BINARY_OPERATORS[self.previous().type]()
            right = self.term()
            left = ast.BinOp(left, operator, right)
        return left

    def term(self) -> ast.expr:
        left = self.factor()
        while self.match_(*TokenGroup.TERMS):
            operator = BINARY_OPERATORS[self.previous().type]()
            right = self.factor()
            left = ast.BinOp(left, operator, right)
        return left

    def factor(self) -> ast.expr:
        left = self.unary()
        while self.match_(*TokenGroup.FACTORS):
            operator = BINARY_OPERATORS[self.previous().type]()
            right = self.unary()
            left = ast.BinOp(left, operator, right)
        return left

    def unary(self) -> ast.expr:
        if self.match_(*TokenGroup.UNARY_LOW):
            operator = UNARY_OPERATORS[self.previous().type]()
            right = self.unary()
            return ast.UnaryOp(operator, right)
        return self.bit_invert()

    def bit_invert(self) -> ast.expr:
        if self.match_(TokenType.TILDE):
            right = self.unary()
            return ast.UnaryOp(ast.Invert(), right)
        return self.power()

    def power(self) -> ast.expr:
        left = self.primary()
        while self.match_(TokenType.STAR_STAR):
            right = self.primary()
            left = ast.BinOp(left, ast.Pow(), right)
        return left

    def primary(self) -> ast.expr:
        if self.match_(TokenType.FALSE):
            return ast.Constant(False)
        elif self.match_(TokenType.TRUE):
            return ast.Constant(True)
        elif self.match_(TokenType.NONE):
            return ast.Constant(None)
        elif self.match_(*TokenGroup.LITERALS):
            return ast.Constant(self.previous().literal)
        elif self.match_(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr
        else:
            raise self.error(self.peek(), "Expect expression.")

    def match_(self, *types: TokenType) -> bool:
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
        if mode == 'eval':
            return ast.Expression(body=self.expression())
        raise ValueError(f'No such parse mode named {mode!r}')


def parse_tree(tokens: list[Token], mode: str = 'exec', filename: str = '<unknown>', source: str = '') -> ast.AST:
    parser: Parser = Parser(tokens, filename, source)
    return parser.parse(mode)
