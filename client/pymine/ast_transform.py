#!/usr/bin/python3

# provides an AST transform which overwrites the unary invert (~) operator
# to create a pymine Relative object.
# meant to be called at runtime.

import ast
import inspect
import logging
import re
import traceback
import sys

from pprint import pformat
from typing import Type, cast, Optional
from types import TracebackType


logging.basicConfig()
log = logging.getLogger("ast_transform")
log.setLevel(logging.DEBUG if "--debug" in sys.argv else logging.WARN)


# pymine initialisation hook
# provides a global variable which points to a Relative class.
# overwrites ~ operator to provide a Relative coordinate
INIT_HOOK_CODE = """
def __pymine_init_function__():
    __import__("pymine").initialised = True

__import__("pymine").init = __pymine_init_function__

__pymine_relative_constructor__ = __import__("pymine").Relative
"""


class InvertOperatorASTTransformer(ast.NodeTransformer):
    """
    Transforms all unary Invert operators (the tilde, ~, which either compiles down to a constant
     or calls .__invert__()), into pymine.Relative() function calls.

     This is because Minecraft uses ~number for relative coordinates. Furthermore, most beginners
     probably will never use the binary invert, so this change shouldn't be too harmful.
    """

    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Invert):
            return ast.copy_location(
                ast.Call(
                    func=ast.copy_location(
                        ast.Name(id="__pymine_relative_constructor__", ctx=ast.Load()),
                        node,
                    ),
                    args=[self.visit(node.operand)],
                    keywords=[],
                ),
                node,
            )

        node = self.generic_visit(node)
        return node

    def visit_Call(self, node):
        log.debug("Call", ast.dump(node, indent=2))

        assert isinstance(node.args, list)

        node.args = [self.visit(x) for x in node.args]
        return node


def get_caller_filename() -> str:
    "Gets the name of the file which has just imported pymine."

    try:
        log.debug("Filenames:")
        [log.debug(x.filename) for x in inspect.stack()]

        filename = next(
            filter(
                lambda x: not x.filename.startswith("<")
                # meant to catch the <frozen importlib._bootstrap...> filenames
                # _technically_ < is a valid filename on linux; however, anecdotally, it
                # would seem like filename is always absolute and thus would always
                # start with a /.
                #
                #
                and (not re.search(r"pymine[/\\]\w+\.py\w?$", x.filename)),
                # meant to catch the pymine/ast_transform.py and pymine/__init__.py
                #
                #
                inspect.stack()[1:],
            )
        ).filename

    except IndexError:
        filename = __file__

    return filename


def format_traceback(
    type: Type[BaseException], value: BaseException, tb: TracebackType
) -> str:
    """
    Accepts the output of sys.exc_info() and formats the traceback.
    Will remove the first two stack objects, so this file will not show up.
    """

    log.debug(traceback.format_exc())

    extracted_tb = traceback.extract_tb(tb)[1:]
    formatted_tb = (
        ["Traceback (most recent call last):\n"]
        + traceback.format_list(extracted_tb)
        + traceback.format_exception_only(type, value)
    )

    return "".join(formatted_tb)


def transform_AST(tree: ast.AST) -> ast.AST:
    "Applies the appropriate operations to the AST."

    transformer = InvertOperatorASTTransformer()
    return transformer.visit(tree)


def decompile_AST(tree: ast.AST) -> str:
    "Decompiles the AST back to readable Python code. Used in debugging."
    from ast_decompiler import decompile

    return decompile(tree)


def run_transform(filename: Optional[str] = None) -> int:
    "Perform the transform, meant to be done when a file imports pymine. Returns the error code."

    global log

    if filename is None:
        filename = get_caller_filename()

    # if 1 + 2 == 3:
    #     raise Exception

    log.info("Reading source file from %s...", filename)
    with open(filename) as source:
        text = source.read()
        tree = ast.parse(text)

    log.info("Transforming tree...")
    transformed_tree = transform_AST(tree)
    log.debug(decompile_AST(transformed_tree))

    log.info("Executing init hook...")
    exec(INIT_HOOK_CODE, globals())

    log.info("Executing transformed AST...")

    exec_globals = {}
    exec_locals = {}

    exec_globals.update({"__file__": filename, "__name__": "__main__"})

    try:
        exec(compile(transformed_tree, filename, "exec"), exec_globals, exec_locals)
    except Exception as err:
        if isinstance(err, SystemExit):
            raise

        uncast_exc_info = sys.exc_info()

        # fix sys.exc_info() has no type data using manual casts
        exc_info = (
            cast(Type[BaseException], uncast_exc_info[0]),
            cast(BaseException, uncast_exc_info[1]),
            cast(TracebackType, uncast_exc_info[2]),
        )

        print(
            format_traceback(*exc_info),
            end="",
            file=sys.stderr,
        )
        return 1

    return 0


def main():
    sys.exit(run_transform())


# if __name__ == "__main__":
#     raise Exception("Import this file as part of pymine, to perform AST manipulation.")
# else:
#     sys.exit(__pymine_transformer_main())

# EXAMPLE_TEXT = """
# import pprint
# from pymine import *
# __import__("pymine").Relative(7)
# pymine.init()
# init()
# print(~i)
# re = ~(-777777777777)
# re5 = -(~777)
# hello = ~int(~str("777"))
# test = ~-8
# aaa = pprint.pprint.pprint(42000000000000000000000)
# # __pymine_relative_constructor__(7)
# """
