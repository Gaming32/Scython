import ast
from typing import Union

from scy.parser import parse_tree
from scy.tokens import Token
from scy.tokenizer import tokenize


def parse(source, filename: str = '<unknown>', mode: str = 'exec') -> Union[ast.Expression, ast.Module]:
    tokens: list[Token] = tokenize(source, filename)
    tree = parse_tree(tokens, mode, filename, source)
    return tree
