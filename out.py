from ast import *
Module(
    body=[
        FunctionDef(
            name='myfn',
            args=arguments(
                posonlyargs=[],
                args=[
                    arg(arg='i')],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]),
            body=[
                Expr(
                    value=Call(
                        func=Name(id='print', ctx=Load()),
                        args=[
                            Call(
                                func=Name(id='int', ctx=Load()),
                                args=[
                                    Name(id='i', ctx=Load())],
                                keywords=[])],
                        keywords=[]))],
            decorator_list=[]),
        For(
            target=Name(id='i', ctx=Store()),
            iter=Call(
                func=Name(id='range', ctx=Load()),
                args=[
                    Constant(value=10)],
                keywords=[]),
            body=[
                Expr(
                    value=Call(
                        func=Name(id='print', ctx=Load()),
                        args=[
                            Name(id='i', ctx=Load())],
                        keywords=[]))],
            orelse=[])],
    type_ignores=[])
