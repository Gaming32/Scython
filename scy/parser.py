import ast
from typing import Any, Union
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

    def declaration(self) -> list[ast.stmt]:
        if self.check(TokenType.DEF):
            return [self.function('function', self.advance())]
        return self.statement()

    def function(self, kind: str, creator: Token) -> ast.FunctionDef:
        name = self.consume(TokenType.IDENTIFIER, f'Expect {kind} name.')
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        arguments = self.parse_args_def()
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return self.ast_token(name.lexeme, arguments, body, [],
            klass=ast.FunctionDef, first=creator, last=self.previous())

    def parse_args_def(self) -> ast.arguments:
        arguments = ast.arguments([], [], None, [], [], None, [])
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                self.consume(TokenType.IDENTIFIER, 'Expect argument name.')
                arguments.args.append(self.ast_token(self.previous().lexeme, klass=ast.arg))
                if not self.match_(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return arguments

    def statement(self) -> list[ast.stmt]:
        if self.match_(TokenType.FOR):
            return self.for_statement()
        elif self.match_(TokenType.IF):
            return [self.if_statement()]
        elif self.match_(TokenType.WHILE):
            return [self.while_statement()]
        return [self.expression_statement()]

    def for_statement(self) -> list[ast.stmt]:
        for_word = self.previous()
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.match_(TokenType.SEMICOLON):
            initializer = None
        else:
            initializer = self.expression_statement(
                (TokenType.SEMICOLON, TokenType.COLON),
                "Expect ';' or ':' after statement."
            )
            if self.previous().type == TokenType.COLON:
                if isinstance(initializer.value, ast.Name):
                    initializer.value.ctx = ast.Store()
                    return [self.for_in_statement(initializer.value, for_word)]
                else:
                    raise self.error(self.previous(), 'Invalid assignment target for iteration.')
        if self.check(TokenType.SEMICOLON):
            condition = None
            condition_tok = self.peek()
        else:
            condition = self.expression(False)
            condition_tok = None
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        if self.match_(TokenType.RIGHT_PAREN):
            increment = None
        else:
            increment = self.expression_statement(TokenType.RIGHT_PAREN,
                                                  "Expect ')' after for clauses")
        body = self.optional_block(increment is None)
        if increment is not None:
            body.append(increment)
        if condition is None:
            condition = self.ast_token(True, first=condition_tok)
        if self.match_(TokenType.ELSE):
            else_branch = self.optional_block()
        else:
            else_branch = []
        result = [self.ast_token(condition, body, else_branch,
                                 klass=ast.While, first=for_word, last=self.previous())]
        if initializer is not None:
            result.insert(0, initializer)
        return result

    def for_in_statement(self, target: ast.Name, for_word: Token) -> ast.For:
        iterable = self.expression(False)
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses")
        body = self.optional_block()
        if self.match_(TokenType.ELSE):
            else_branch = self.optional_block()
        else:
            else_branch = []
        return self.ast_token(target, iterable, body, else_branch,
                              klass=ast.For, first=for_word, last=self.previous())

    def if_statement(self) -> ast.If:
        if_word = self.previous()
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression(False)
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.optional_block()
        if self.match_(TokenType.ELSE):
            else_branch = self.optional_block()
        else:
            else_branch = []
        return self.ast_token(condition, then_branch, else_branch,
                              klass=ast.If, first=if_word, last=self.previous())

    def while_statement(self) -> ast.stmt:
        while_word = self.previous()
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression(False)
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition")
        body = self.optional_block()
        if self.match_(TokenType.ELSE):
            else_branch = self.optional_block()
        else:
            else_branch = []
        return self.ast_token(condition, body, else_branch,
                              klass=ast.While, first=while_word, last=self.previous())

    def expression_statement(self, end: Union[TokenType, tuple[TokenType]] = TokenType.SEMICOLON,
                                   error: str = "Expect ';' after statement.") -> Union[ast.Expr]:
        expr = self.expression()
        if self.match_(TokenType.EQUAL):
            if not isinstance(expr, ast.Name):
                raise self.error(self.previous(), 'Invalid assignment target.')
            extra = [expr, self.expression()]
            extra[0].ctx = ast.Store()
            while self.match_(TokenType.EQUAL):
                if isinstance(extra[-1], ast.Name):
                    extra[-1].ctx = ast.Store()
                else:
                    raise self.error(self.previous(), 'Invalid assignment target.')
                extra.append(self.expression())
            value = extra.pop()
            statement = ast.Assign(targets=extra, value=value, **self.get_loc(extra[0], value))
        else:
            statement = ast.Expr(expr, **self.get_loc(expr, expr))
        if isinstance(end, tuple):
            self.consume_any(end, error)
        else:
            self.consume(end, error)
        return statement

    def optional_block(self, fill_empty: bool = True) -> list[ast.stmt]:
        if self.match_(TokenType.LEFT_BRACE):
            result = self.block()
            if not result and fill_empty:
                result = [self.ast_token(klass=ast.Pass)]
            return result
        elif self.match_(TokenType.SEMICOLON):
            # This is done so that ast.unparse still generates valid syntax for empty blocks
            if fill_empty:
                return [self.ast_token(klass=ast.Pass)]
            return []
        return self.declaration()

    def block(self) -> list[ast.stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.extend(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression(self, toplevel: bool = True) -> ast.expr:
        if not toplevel:
            return self.assignment_expression()
        return self.or_()

    def assignment_expression(self) -> ast.expr:
        expr = self.or_()
        if self.match_(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment_expression()
            if isinstance(expr, ast.Name):
                expr.ctx = ast.Store()
                return ast.NamedExpr(expr, value, **self.get_loc(expr, value))
            raise self.error(equals, 'Invalid assignement target.')
        return expr

    def or_(self) -> ast.expr:
        left = self.and_()
        if self.match_(TokenType.PIPE_PIPE):
            values = [left, self.and_()]
            while self.match_(TokenType.PIPE_PIPE):
                values.append(self.and_())
            return ast.BoolOp(ast.Or(), values, **self.get_loc(left, values[-1]))
        return left

    def and_(self) -> ast.expr:
        left = self.not_()
        if self.match_(TokenType.AMPERSAND_AMPERSAND):
            values = [left, self.not_()]
            while self.match_(TokenType.AMPERSAND_AMPERSAND):
                values.append(self.not_())
            return ast.BoolOp(ast.And(), values, **self.get_loc(left, values[-1]))
        return left

    def not_(self) -> ast.expr:
        if self.match_(TokenType.BANG):
            right = self.comparison()
            return ast.UnaryOp(ast.Not(), right, **self.get_loc(right, right))
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
            return ast.Compare(left, operators, extra, **self.get_loc(left, extra[-1]))
        else:
            return left

    def bit_or(self):
        left = self.bit_xor()
        while self.match_(TokenType.PIPE):
            right = self.bit_xor()
            left = ast.BinOp(left, ast.BitOr(), right, **self.get_loc(left, right))
        return left

    def bit_xor(self):
        left = self.bit_and()
        while self.match_(TokenType.CARET):
            right = self.bit_and()
            left = ast.BinOp(left, ast.BitXor(), right, **self.get_loc(left, right))
        return left

    def bit_and(self):
        left = self.bit_shift()
        while self.match_(TokenType.AMPERSAND):
            right = self.bit_shift()
            left = ast.BinOp(left, ast.BitAnd(), right, **self.get_loc(left, right))
        return left

    def bit_shift(self):
        left = self.term()
        while self.match_(*TokenGroup.BIT_SHIFT):
            operator = BINARY_OPERATORS[self.previous().type]()
            right = self.term()
            left = ast.BinOp(left, operator, right, **self.get_loc(left, right))
        return left

    def term(self) -> ast.expr:
        left = self.factor()
        while self.match_(*TokenGroup.TERMS):
            operator = BINARY_OPERATORS[self.previous().type]()
            right = self.factor()
            left = ast.BinOp(left, operator, right, **self.get_loc(left, right))
        return left

    def factor(self) -> ast.expr:
        left = self.unary()
        while self.match_(*TokenGroup.FACTORS):
            operator = BINARY_OPERATORS[self.previous().type]()
            right = self.unary()
            left = ast.BinOp(left, operator, right, **self.get_loc(left, right))
        return left

    def unary(self) -> ast.expr:
        if self.match_(*TokenGroup.UNARY_LOW):
            operator = UNARY_OPERATORS[self.previous().type]()
            right = self.unary()
            return ast.UnaryOp(operator, right, **self.get_loc(right, right))
        return self.bit_invert()

    def bit_invert(self) -> ast.expr:
        if self.match_(TokenType.TILDE):
            right = self.unary()
            return ast.UnaryOp(ast.Invert(), right, **self.get_loc(right, right))
        return self.power()

    def power(self) -> ast.expr:
        left = self.call()
        while self.match_(TokenType.STAR_STAR):
            right = self.call()
            left = ast.BinOp(left, ast.Pow(), right, **self.get_loc(left, right))
        return left

    def call(self) -> ast.expr:
        expr = self.primary()
        while True:
            if self.match_(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def finish_call(self, callee: ast.expr) -> ast.expr:
        args, kwargs, paren = self.parse_args_call()
        return ast.Call(callee, args, kwargs,
            lineno=callee.lineno, end_lineno=paren.line,
            col_offset=callee.col_offset, end_col_offset=paren.column + 1
        )

    def parse_args_call(self) -> tuple[list[ast.expr], list[ast.keyword], Token]:
        args = []
        kwargs = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                args.append(self.expression(False))
                if not self.match_(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")
        return args, kwargs, paren

    def primary(self) -> ast.expr:
        if self.match_(TokenType.FALSE):
            return self.ast_token(False)
        elif self.match_(TokenType.TRUE):
            return self.ast_token(True)
        elif self.match_(TokenType.NONE):
            return self.ast_token(None)
        elif self.match_(*TokenGroup.LITERALS):
            return self.ast_token(self.previous().literal)
        elif self.match_(TokenType.IDENTIFIER):
            tok = self.previous()
            return self.ast_token(tok.lexeme, ast.Load(), klass=ast.Name)
        elif self.match_(TokenType.LEFT_PAREN):
            expr = self.expression(False)
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr
        else:
            raise self.error(self.peek(), "Expect expression.")

    def ast_token(self, *args, klass: type[ast.AST] = ast.Constant,
                  first: Token = None, last: Token = None) -> Any:
        if first is None:
            first = self.previous()
        if last is None:
            last = first
        result = klass(*args)
        result.lineno = first.line
        result.end_lineno = last.line
        result.col_offset = first.column
        result.end_col_offset = last.column + len(last.lexeme)
        return result

    def get_loc(self, left: ast.AST, right: ast.AST):
        return dict(
            lineno=left.lineno, end_lineno=right.end_lineno,
            col_offset=left.col_offset, end_col_offset=right.end_col_offset
        )

    def match_(self, *types: TokenType) -> bool:
        if any(self.check(type) for type in types):
            self.advance()
            return True
        return False

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def consume_any(self, types: tuple[TokenType], message: str) -> Token:
        if self.match_(*types):
            return self.peek()
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

    def parse(self, mode: str = 'exec') -> Union[ast.Expression, ast.Module]:
        if mode == 'eval':
            return ast.Expression(body=self.expression())
        elif mode == 'exec':
            statements = []
            while not self.is_at_end():
                statements.extend(self.declaration())
            return ast.Module(body=statements, type_ignores=[])
        raise ValueError(f'No such parse mode named {mode!r}')


def parse_tree(tokens: list[Token], mode: str = 'exec', filename: str = '<unknown>', source: str = '') -> Union[ast.Expression, ast.Module]:
    parser: Parser = Parser(tokens, filename, source)
    return parser.parse(mode)
