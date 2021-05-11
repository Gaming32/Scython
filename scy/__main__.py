import ast
import argparse

from scy.backend import parse

parser = argparse.ArgumentParser('python -m scy')
parser.add_argument('script', type=argparse.FileType('r'))
parser.add_argument('-M', '--mode', choices=['auto', 'run', 'dump', 'py'], default='auto')


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


if __name__ == '__main__':
    main()
