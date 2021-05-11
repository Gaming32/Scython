import ast
import argparse

from scy.backend import parse

parser = argparse.ArgumentParser('python -m scy')
parser.add_argument('script', type=argparse.FileType('r'))
parser.add_argument('-M', '--mode', choices=['auto', 'run', 'dump'], default='auto')


def main():
    args = parser.parse_args()
    print(args)
    if args.mode == 'auto':
        args.mode = 'dump'
    source = args.script.read()
    try:
        filename = args.script.name
    except Exception:
        filename = '<unknown>'
    # tree = parse(source, filename)
    tree = parse(source, filename, 'eval')
    print(ast.dump(tree, indent=4))


if __name__ == '__main__':
    main()
