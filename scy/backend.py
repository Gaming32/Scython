import ast
from pprint import pprint

from scy.tokens import Token
from scy.tokenizer import tokenize


def parse(source, filename='<unknown>', mode='exec') -> ast.AST:
    tokens: list[Token] = tokenize(source, filename)
    pprint(tokens)
