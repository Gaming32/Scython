def find_line(code: str, index: int) -> str:
    start = code.rfind('\n', 0, index) + 1
    code = code[start:]
    end = code.find('\n')
    if end == -1:
        end = len(code)
    print(repr(code[:end]))
    return code[:end]
