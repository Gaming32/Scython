import ast
import argparse
from typing import Optional
from scy.utils import count_nodes
import time

from scy.backend import parse

parser = argparse.ArgumentParser('python -m scy')
parser.add_argument('script', type=argparse.FileType('r'))
parser.add_argument('-M', '--mode', choices=['auto', 'run', 'dump', 'py', 'compile_only'], default='auto')


def main():
    args = parser.parse_args()
    if args.mode == 'auto':
        args.mode = 'run'
    source = args.script.read()
    try:
        filename = args.script.name
    except Exception:
        filename = '<unknown>'
    tree = parse(source, filename)
    if args.mode == 'dump':
        print(ast.dump(tree, indent=4))
    elif args.mode == 'run':
        compiled = compile(tree, filename, 'exec')
        exec(compiled)
    elif args.mode == 'py':
        print(ast.unparse(tree))
    elif args.mode == 'compile_only':
        error: None
        start = time.process_time_ns()
        try:
            compile(tree, filename, 'exec')
        except SyntaxError as e:
            error = e
        end = time.process_time_ns()
        if error is None:
            print(f'Successfully compiled "{filename}" (AST had {count_nodes(tree)} nodes) in {end - start}ns.')
        else:
            print(f'Failed to compile "{filename}" (AST had {count_nodes(tree)} nodes) in {end - start}ns.')
            import traceback
            traceback.print_exception(SyntaxError, error, error.__traceback__, 0)


if __name__ == '__main__':
    main()
