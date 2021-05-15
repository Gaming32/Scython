import ast
import argparse
import builtins
import sys
from typing import Optional
import time

from scy.backend import parse
from scy.utils import count_nodes

parser = argparse.ArgumentParser('python -m scy')
parser.add_argument('script', type=argparse.FileType('r'))
parser.add_argument('-M', '--mode', choices=['auto', 'run', 'dump', 'py', 'compile_only'], default='auto')


# This was copied from the runpy module
# It's copied here just in case it's removed from runpy
def _run_code(code, run_globals, init_globals=None,
              mod_name=None, mod_spec=None,
              pkg_name=None, script_name=None):
    """Helper to run code in nominated namespace"""
    if init_globals is not None:
        run_globals.update(init_globals)
    if mod_spec is None:
        loader = None
        fname = script_name
        cached = None
    else:
        loader = mod_spec.loader
        fname = mod_spec.origin
        cached = mod_spec.cached
        if pkg_name is None:
            pkg_name = mod_spec.parent
    run_globals.update(__name__ = mod_name,
                       __file__ = fname,
                       __cached__ = cached,
                       __doc__ = None,
                       __loader__ = loader,
                       __package__ = pkg_name,
                       __spec__ = mod_spec)
    exec(code, run_globals)
    return run_globals


def main() -> int:
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
        print(ast.dump(tree, indent=3, include_attributes=True))
    elif args.mode == 'run':
        compiled = compile(tree, filename, 'exec')
        _run_code(compiled, {
            '__builtins__': builtins
        }, mod_name='__main__', script_name=filename)
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
            return 1


if __name__ == '__main__':
    sys.exit(main())
