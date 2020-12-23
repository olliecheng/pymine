import inspect


import gc
from forbiddenfruit import curse
from pprint import pprint
import ast
import traceback

try:
    filename = inspect.stack()[1].filename
    filename = next(
        filter(lambda x: not x.filename.startswith("<"), inspect.stack()[1:])
    ).filename
except IndexError:
    filename = __file__

pprint(inspect.stack())
print(filename)

# gc.get_referents(int.__dict__)[0]["__invert__"] = lambda self: 420

text = """

import pprint

from pymine import *

__import__("pymine").Relative(7)
pymine.init()

init()

print(~i)

re = ~(-777777777777)

re5 = -(~777)

hello = ~int(~str("777"))

test = ~-8

aaa = pprint.pprint.pprint(42000000000000000000000)

# __pymine_relative_constructor__(7)
"""

INIT_HOOK = """
# pymine initialisation hook
# overwrites ~ operator to provide a Relative coordinate

def __pymine_init_function__():
    __import__("pymine").initialised = True

__import__("pymine").init = __pymine_init_function__

__pymine_relative_constructor__ = __import__("pymine").Relative
"""


class AnalysisNodeVisitor(ast.NodeTransformer):
    # @staticmethod
    def visit_UnaryOp(self, node):
        # print("Node type: UnaryOp and fields: ", node._fields)
        # print(isinstance(node.op, ast.Invert), node.operand.value)
        # ast.NodeVisitor.generic_visit(self, node)

        if isinstance(node.op, ast.Invert):
            return ast.copy_location(
                ast.Call(
                    # func=ast.Name(id="__pymine_relative_constructor__", ctx=ast.Load()),
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
        # print("Node type: Call", node.func)
        # print(ast.literal_eval(node.func))
        # print(ast.dump(node, indent=2))

        print("Call", node.args)

        assert isinstance(node.args, list)

        node.args = [self.visit(x) for x in node.args]
        # for i in node.args:
        #     print(ast.dump(i, indent=2))
        #     print(ast.dump(self.visit(i), indent=2))
        print("done", node.args)
        return node


INIT_TREE = ast.parse(INIT_HOOK)

with open(filename) as source:
    text = source.read()
    tree = ast.parse(text)
    # print(ast.dump(tree, indent=2))

# tree.body = INIT_TREE.body + tree.body
v = AnalysisNodeVisitor()
new_node = v.visit(tree)

print(ast.dump(new_node, indent=2, include_attributes=True))

from ast_decompiler import decompile

print(decompile(new_node))

exec(INIT_HOOK)
try:
    exec(compile(new_node, filename, "exec"))
except Exception as err:
    # tb = traceback.extract_stack()[2:]
    # print(tb)
    # for i in traceback.format_list(tb):
    #     print(i)
    import sys

    # traceback.print_exc()

    type, value, tb = sys.exc_info()
    tb = traceback.extract_tb(tb)[1:]
    formatted_tb = (
        ["Traceback (most recent call last):\n"]
        + traceback.format_list(tb)
        + traceback.format_exception_only(type, value)
    )

    for x in formatted_tb:
        print(x, end="", file=sys.stderr)

    sys.exit(1)

    # traceback.print_exc(limit=-2)
    # raise
    # raise tb
# import astunparse

# print(astunparse.unparse(new_node))

import sys

sys.exit()
