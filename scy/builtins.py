import os
from types import CodeType
from typing import Any, Mapping, Optional, Union

from scy.backend import parse


__all__ = ['scy_compile', 'scy_eval', 'scy_exec']


def scy_compile(
    source: str,
    filename: Union[str, os.PathLike],
    mode: str,
    flags: int = 0,
    dont_inherit: int = False,
    optimize: int = -1) -> CodeType:
    filename = os.fspath(filename)
    tree = parse(source, filename, mode)
    return compile(tree, filename, mode, flags, dont_inherit, optimize)


def scy_eval(
    expression: Union[str, CodeType],
    globals: Optional[dict[str, Any]] = None,
    locals: Optional[Mapping[str, Any]] = None) -> Any:
    if not isinstance(expression, CodeType):
        expression = scy_compile(expression, '<string>', 'eval')
    return eval(expression, globals, locals)


def scy_exec(
    expression: Union[str, CodeType],
    globals: Optional[dict[str, Any]] = None,
    locals: Optional[Mapping[str, Any]] = None) -> Any:
    if not isinstance(expression, CodeType):
        expression = scy_compile(expression, '<string>', 'exec')
    return exec(expression, globals, locals)
