import ast


class NodeCounter(ast.NodeVisitor):
    count: int

    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def visit(self, node: ast.AST) -> None:
        self.generic_visit(node)
        self.count += 1


def find_line(code: str, index: int) -> str:
    start = code.rfind('\n', 0, index) + 1
    code = code[start:]
    end = code.find('\n')
    if end == -1:
        end = len(code)
    print(repr(code[:end]))
    return code[:end]


def count_nodes(tree: ast.AST) -> int:
    counter = NodeCounter()
    counter.visit(tree)
    return counter.count
