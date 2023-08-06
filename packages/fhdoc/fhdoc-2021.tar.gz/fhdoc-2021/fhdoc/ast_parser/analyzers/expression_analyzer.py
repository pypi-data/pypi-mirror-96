"""
AST analyzer for `ast.expr` records.
"""
from typing import TYPE_CHECKING

from fhdoc.utils.logger import get_logger
from fhdoc.ast_parser.analyzers.base_analyzer import BaseAnalyzer
from fhdoc.ast_parser.enums import RenderPart
import ast

if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional, List
    from fhdoc.ast_parser.type_defs import ASTIterable, DirtyRenderExpr


class ExpressionAnalyzer(BaseAnalyzer):
    """
    AST analyzer for `ast.expr` records.

    Prepares `parts` for `NodeRecord.render` method.
    """

    def __init__(self):
        # type: () -> None
        super(ExpressionAnalyzer, self).__init__()
        self._logger = get_logger()
        self.parts = []  # type: List[DirtyRenderExpr]

    # dummy value to replace unknown nodes and operators
    UNKNOWN = "..."

    # representation map for binary operators
    BINOP_SYMBOLS = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        ast.Mod: "%",
        ast.Pow: "**",
        ast.LShift: "<<",
        ast.RShift: ">>",
        ast.BitOr: "|",
        ast.BitXor: "^",
        ast.BitAnd: "&",
        ast.FloorDiv: "//",
    }

    # representation map for boolean operators
    BOOLOP_SYMBOLS = {ast.And: "and", ast.Or: "or"}

    # representation map for comparison operators
    CMPOP_SYMBOLS = {
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.Is: "is",
        ast.IsNot: "is not",
        ast.In: "in",
        ast.NotIn: "not in",
    }

    # representation map for unary operators
    UNARYOP_SYMBOLS = {ast.Invert: "~", ast.Not: "not", ast.UAdd: "+", ast.USub: "-"}

    def visit_Str(self, node):
        # type: (ast.Str) -> None
        """
        Parse info from `ast.Str` node and put it to `parts`.

        Examples::

            "my_string"

        Arguments:
            node -- AST node.
        """
        value = node.s
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        self.parts.append(repr(value))

    def visit_Bytes(self, node):
        # type: (ast.Bytes) -> None
        """
        Parse info from `ast.Bytes` node and put it to `parts`.

        Examples::

            b"my_string"

        Arguments:
            node -- AST node.
        """
        value = node.s
        self.parts.append(repr(value))

    def visit_Num(self, node):
        # type: (ast.Num) -> None
        """
        Parse info from `ast.Num` node and put it to `parts`.

        Examples::

            123
            123.456

        Arguments:
            node -- AST node.
        """
        value = node.n
        self.parts.append(repr(value))

    def visit_Name(self, node):
        # type: (ast.Name) -> None
        """
        Parse info from `ast.Name` node and put it to `parts`.

        Examples::

            my_value

        Arguments:
            node -- AST node.
        """
        self.parts.append(node.id)
        self.related_names.append(node.id)

    def visit_NameConstant(self, node):
        # type: (ast.NameConstant) -> None
        """
        Parse info from `ast.NameConstant` node and put it to `parts`.

        Examples::

            None
            True

        Arguments:
            node -- AST node.
        """
        self.parts.append(repr(node.value))

    def visit_Subscript(self, node):
        # type: (ast.Subscript) -> None
        """
        Parse info from `ast.Subscript` node and put it to `parts`.

        Type annotations are also matched by this method.

        Examples::

            Union[Name, bool]
            list[1:4]

        Arguments:
            node -- AST node.
        """
        self.parts.append(node.value)
        self.parts.append("[")
        if isinstance(node.slice, ast.Index) and isinstance(
            node.slice.value, ast.Tuple
        ):
            self._visit_iterable(node.slice.value)
        else:
            self.parts.append(node.slice)
        self.parts.append("]")

    def visit_Attribute(self, node):
        # type: (ast.Attribute) -> None
        """
        Parse info from `ast.Attribute` node and put it to `parts`.

        Examples::

            my_object.attribute

        Arguments:
            node -- AST node.
        """
        self.parts.append(node.value)
        self.parts.append(".")
        self.parts.append(node.attr)

    def _visit_iterable(self, node):
        # type: (ASTIterable) -> None
        """
        Parse info from an iterable node and put it to `parts`.

        Used for `ast.Tuple`, `ast.Subscript`, `ast.List`, `ast.Set`

        Examples::

            [1, 2, 3]
            {1, 2, 3}
            (1, 2, 3)
            Union[Text, bool]

        Arguments:
            node -- AST node.
        """
        args_count = 0
        if node.elts:
            self.parts.append(RenderPart.MULTI_LINE_INDENT)
            for element in node.elts:
                if args_count:
                    self.parts.append(",")
                    self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                    self.parts.append(RenderPart.MULTI_LINE_BREAK)
                args_count += 1
                self.parts.append(element)
            self.parts.append(RenderPart.MULTI_LINE_COMMA)
            self.parts.append(RenderPart.MULTI_LINE_UNINDENT)

    def visit_List(self, node):
        # type: (ast.List) -> None
        """
        Parse info from `ast.List` node and put it to `parts`.

        Examples::

            [1, 2, 3]

        Arguments:
            node -- AST node.
        """
        self.parts.append("[")
        self._visit_iterable(node)
        self.parts.append("]")

    def visit_Set(self, node):
        # type: (ast.Set) -> None
        """
        Parse info from `ast.Set` node and put it to `parts`.

        Examples::

            {1, 2, 3}

        Arguments:
            node -- AST node.
        """
        self.parts.append("{")
        self._visit_iterable(node)
        self.parts.append("}")

    def visit_Tuple(self, node):
        # type: (ast.Tuple) -> None
        """
        Parse info from `ast.Tuple` node and put it to `parts`.

        Examples::

            (1, 2, 3)

        Arguments:
            node -- AST node.
        """
        self.parts.append("(")
        self._visit_iterable(node)
        self.parts.append(")")

    def visit_Call(self, node):
        # type: (ast.Call) -> None
        """
        Parse info from `ast.Call` node and put it to `parts`.

        Arguments:
            node -- AST node.
        """
        self.parts.append(node.func)
        self.parts.append("(")
        self.parts.append(RenderPart.MULTI_LINE_INDENT)
        args_count = 0
        for element in node.args:
            if args_count:
                self.parts.append(",")
                self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                self.parts.append(RenderPart.MULTI_LINE_BREAK)
            args_count += 1
            self.parts.append(element)

        # FIXME: `AST2` ast.Call stores star argument in `starargs`
        starargs = getattr(node, "starargs", None)
        if starargs:
            if args_count:
                self.parts.append(",")
                self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                self.parts.append(RenderPart.MULTI_LINE_BREAK)
            args_count += 1
            self.parts.append("*")
            self.parts.append(starargs)

        for kwelement in node.keywords:
            if args_count:
                self.parts.append(",")
                self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                self.parts.append(RenderPart.MULTI_LINE_BREAK)
            args_count += 1
            self.parts.append(kwelement)

        # FIXME: `AST2` ast.Call stores kwarg argument in `kwargs`
        kwargs = getattr(node, "kwargs", None)
        if kwargs:
            if args_count:
                self.parts.append(",")
                self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                self.parts.append(RenderPart.MULTI_LINE_BREAK)
            args_count += 1
            self.parts.append("**")
            self.parts.append(kwargs)

        if args_count:
            self.parts.append(RenderPart.MULTI_LINE_COMMA)
        self.parts.append(RenderPart.MULTI_LINE_UNINDENT)
        self.parts.append(")")

    def visit_Starred(self, node):
        # type: (ast.Starred) -> None
        """
        Parse info from `ast.Starred` node and put it to `parts`.

        Examples::

            *arg

        Arguments:
            node -- AST node.
        """
        self.parts.append("*")
        self.parts.append(node.value)

    def visit_keyword(self, node):
        # type: (ast.keyword) -> None
        """
        Parse info from `ast.keyword` node and put it to `parts`.

        Examples::

            my_func(**{"kwarg": "value"})
            my_func(kwarg="value")

        Arguments:
            node -- AST node.
        """
        if not node.arg:
            self.parts.append("**")
            self.parts.append(node.value)
            return

        self.parts.append(node.arg)
        self.parts.append("=")
        self.parts.append(node.value)

    def visit_Dict(self, node):
        # type: (ast.Dict) -> None
        """
        Parse info from `ast.Dict` node and put it to `parts`.

        Arguments:
            node -- AST node.
        """
        self.parts.append("{")
        if node.keys:
            self.parts.append(RenderPart.MULTI_LINE_INDENT)
            key_count = 0
            for index, key in enumerate(node.keys):
                if key_count:
                    self.parts.append(",")
                    self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                    self.parts.append(RenderPart.MULTI_LINE_BREAK)
                key_count += 1
                self.parts.append(key)
                self.parts.append(": ")
                self.parts.append(node.values[index])
            self.parts.append(RenderPart.MULTI_LINE_COMMA)
            self.parts.append(RenderPart.MULTI_LINE_UNINDENT)
        self.parts.append("}")

    def visit_Compare(self, node):
        # type: (ast.Compare) -> None
        """
        Parse info from `ast.Compare` node and put it to `parts`.

        Examples::

            value < 5
            1 < weekday < 7

        Arguments:
            node -- AST node.
        """
        self.parts.append(node.left)
        for index, right in enumerate(node.comparators):
            operator_class = type(node.ops[index])
            self.parts.append(" ")
            operator = self.CMPOP_SYMBOLS.get(operator_class, self.UNKNOWN)
            if operator == self.UNKNOWN:
                self._logger.warning(
                    "Unknown omparison operator: {}".format(operator_class.__name__)
                )
            self.parts.append(operator)
            self.parts.append(" ")
            self.parts.append(right)

    def visit_BinOp(self, node):
        # type: (ast.BinOp) -> None
        """
        Parse info from `ast.BinOp` node and put it to `parts`.

        Examples::

            1 + 5
            value + 1

        Arguments:
            node -- AST node.
        """
        self.parts.append(node.left)
        self.parts.append(" ")
        operator = self.BINOP_SYMBOLS.get(type(node.op), self.UNKNOWN)
        if operator == self.UNKNOWN:
            self._logger.warning(
                "Unknown binary operator: {}".format(node.op.__class__.__name__)
            )
        self.parts.append(operator)
        self.parts.append(" ")
        self.parts.append(node.right)

    def visit_BoolOp(self, node):
        # type: (ast.BoolOp) -> None
        """
        Parse info from `ast.BoolOp` node and put it to `parts`.

        Examples::

            value or True
            a and b

        Arguments:
            node -- AST node.
        """
        operator = self.BOOLOP_SYMBOLS.get(type(node.op), self.UNKNOWN)
        if operator == self.UNKNOWN:
            self._logger.warning(
                "Unknown boolean operator: {}".format(node.op.__class__.__name__)
            )
        for index, value in enumerate(node.values):
            if index:
                self.parts.append(" ")
                self.parts.append(operator)
                self.parts.append(" ")
            self.parts.append(value)

    def visit_UnaryOp(self, node):
        # type: (ast.UnaryOp) -> None
        """
        Parse info from `ast.UnaryOp` node and put it to `parts`.

        Examples::

            +5
            -12
            ~1
            not True

        Arguments:
            node -- AST node.
        """
        operator = self.UNARYOP_SYMBOLS.get(type(node.op), self.UNKNOWN)
        if operator == self.UNKNOWN:
            self._logger.warning(
                "Unknown unary operator: {}".format(node.op.__class__.__name__)
            )
        self.parts.append(operator)
        if operator == "not":
            self.parts.append(" ")
        self.parts.append(node.operand)

    def visit_Lambda(self, node):
        # type: (ast.Lambda) -> None
        """
        Parse info from `ast.Lambda` node and put it to `parts`.

        Examples::

            lambda x: x + 5

        Arguments:
            node -- AST node.
        """
        self.parts.append("lambda ")
        self.parts.append(node.args)
        self.parts.append(": ")
        self.parts.append(node.body)

    def visit_arguments(self, node):
        # type: (ast.arguments) -> None
        """
        Parse info from `ast.arguments` node and put it to `parts`.

        Examples::

            def my_func(arg, *args, **kwargs)

        Arguments:
            node -- AST node.
        """
        arg_count = 0
        for index, arg in enumerate(node.args):
            if arg_count:
                self.parts.append(",")
                self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                self.parts.append(RenderPart.MULTI_LINE_BREAK)
            arg_count += 1
            default = None
            default_index = len(node.args) - len(node.defaults) + index
            if default_index < len(node.defaults):
                default = node.defaults[default_index]

            self.parts.append(arg)
            if default is not None:
                self.parts.append("=")
                self.parts.append(default)
        if node.vararg is not None:
            if arg_count:
                self.parts.append(",")
                self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                self.parts.append(RenderPart.MULTI_LINE_BREAK)

            arg_count += 1
            self.parts.append("*")
            self.parts.append(node.vararg)
        if node.kwarg is not None:
            if arg_count:
                self.parts.append(",")
                self.parts.append(RenderPart.SINGLE_LINE_SPACE)
                self.parts.append(RenderPart.MULTI_LINE_BREAK)

            arg_count += 1
            self.parts.append("**")
            self.parts.append(node.kwarg)

        if arg_count:
            self.parts.append(RenderPart.MULTI_LINE_COMMA)

    def visit_arg(self, node):
        # type: (ast.arg) -> None
        """
        Parse info from `ast.arg` node and put it to `parts`.

        Examples::

            def my_func(arg)
            def my_func(arg: Text)

        Arguments:
            node -- AST node.
        """
        self.parts.append(node.arg)
        if node.annotation:
            self.parts.append(": ")
            self.parts.append(node.annotation)

    def visit_Index(self, node):
        # type: (ast.Index) -> None
        """
        Parse info from `ast.Index` node and put it to `parts`.

        Examples::

            Union[Text, bool]
            Union[Text]

        Arguments:
            node -- AST node.
        """
        if isinstance(node.value, ast.Tuple):
            self._visit_iterable(node.value)
            return
        self.parts.append(node.value)

    def visit_Ellipsis(self, _node):
        # type: (ast.ASTEllipsis) -> None
        """
        Parse info from `ast.Ellipsis` node and put it to `parts`.

        Examples::

            ...

        Arguments:
            node -- AST node.
        """
        self.parts.append("...")

    def visit_Slice(self, node):
        # type: (ast.Slice) -> None
        """
        Parse info from `ast.Slice` node and put it to `parts`.

        Examples::

            [1:]
            [:2]
            [1:2]
            [1:2:-1]
            [::-1]

        Arguments:
            node -- AST node.
        """
        if node.lower:
            self.parts.append(node.lower)
        self.parts.append(":")
        if node.upper:
            self.parts.append(node.upper)
        if node.step:
            self.parts.append(":")
            self.parts.append(node.step)

    def visit_JoinedStr(self, node):
        # type: (ast.JoinedStr) -> None
        """
        Parse info from `ast.JoinedStr` node and put it to `parts`.

        Examples::

            f'str: {my_string}'

        Arguments:
            node -- AST node.
        """
        self.parts.append("f'")
        for value in node.values:
            if isinstance(value, (ast.Str, ast.Constant)):
                str_value = value.s
                if isinstance(str_value, bytes):
                    str_value = str_value.decode("utf-8")
                self.parts.append(str_value)
            else:
                self.parts.append(value)
        self.parts.append("'")

    def visit_FormattedValue(self, node):
        # type: (ast.FormattedValue) -> None
        """
        Parse info from `ast.FormattedValue` node and put it to `parts`.

        Examples::

            f"{formatted_value}"

        Arguments:
            node -- AST node.
        """
        self.parts.append("{")
        self.parts.append(node.value)
        self.parts.append("}")

    def visit_comprehension(self, node):
        # type: (ast.comprehension) -> None
        """
        Parse info from `ast.comprehension` node and put it to `parts`.

        Examples::

            for k in range(3) if k > 0 if True

        Arguments:
            node -- AST node.
        """
        self.parts.append("for ")
        self.parts.append(node.target)
        self.parts.append(" in ")
        self.parts.append(node.iter)
        for expr in node.ifs:
            self.parts.append(" if ")
            self.parts.append(expr)

    def visit_DictComp(self, node):
        # type: (ast.DictComp) -> None
        """
        Parse info from `ast.DictComp` node and put it to `parts`.

        Examples::

            {k: 1 for k in range(3)}

        Arguments:
            node -- AST node.
        """
        self.parts.append("{")
        self.parts.append(node.key)
        self.parts.append(": ")
        self.parts.append(node.value)
        self.parts.append(" ")
        for comprehension in node.generators:
            self.parts.append(comprehension)
        self.parts.append("}")

    def visit_ListComp(self, node):
        # type: (ast.ListComp) -> None
        """
        Parse info from `ast.ListComp` node and put it to `parts`.

        Examples::

            [k + 1 for k in range(3)]

        Arguments:
            node -- AST node.
        """
        self.parts.append("[")
        self.parts.append(node.elt)
        self.parts.append(" ")
        for comprehension in node.generators:
            self.parts.append(comprehension)
        self.parts.append("]")

    def visit_SetComp(self, node):
        # type: (ast.SetComp) -> None
        """
        Parse info from `ast.SetComp` node and put it to `parts`.

        Examples::

            {k + 1 for k in range(3)}

        Arguments:
            node -- AST node.
        """
        self.parts.append("{")
        self.parts.append(node.elt)
        self.parts.append(" ")
        for comprehension in node.generators:
            self.parts.append(comprehension)
        self.parts.append("}")

    def visit_GeneratorExp(self, node):
        # type: (ast.GeneratorExp) -> None
        """
        Parse info from `ast.GeneratorExp` node and put it to `parts`.

        Examples::

            (k + 1 for k in range(3))

        Arguments:
            node -- AST node.
        """
        self.parts.append("(")
        self.parts.append(node.elt)
        self.parts.append(" ")
        for comprehension in node.generators:
            self.parts.append(comprehension)
        self.parts.append(")")

    def visit_IfExp(self, node):
        # type: (ast.IfExp) -> None
        """
        Parse info from `ast.IfExp` node and put it to `parts`.

        Examples::

            5 if my_value else 6

        Arguments:
            node -- AST node.
        """
        self.parts.append(node.body)
        self.parts.append(" if ")
        self.parts.append(node.test)
        self.parts.append(" else ")
        self.parts.append(node.orelse)

    def visit_Await(self, node):
        # type: (ast.Await) -> None
        """
        Parse info from `ast.Await` node and put it to `parts`.

        Examples::

            await result

        Arguments:
            node -- AST node.
        """
        self.parts.append("await ")
        self.parts.append(node.value)

    def visit_Yield(self, node):
        # type: (ast.Yield) -> None
        """
        Parse info from `ast.Yield` node and put it to `parts`.

        Examples::

            yield
            yield value

        Arguments:
            node -- AST node.
        """
        self.parts.append("yield")
        if node.value:
            self.parts.append(" ")
            self.parts.append(node.value)

    def visit_YieldFrom(self, node):
        # type: (ast.YieldFrom) -> None
        """
        Parse info from `ast.YieldFrom` node and put it to `parts`.

        Examples::

            yield from my_generator

        Arguments:
            node -- AST node.
        """
        self.parts.append("yield from ")
        self.parts.append(node.value)

    def generic_visit(self, node):
        # type: (ast.AST) -> None
        """
        Parse info from an unknown `ast.AST` node and put `...` to `parts`.

        Logs warning with node class.

        Arguments:
            node -- AST node.
        """
        self._logger.warning(
            "Could not render node {}, replaced with `{}`".format(
                node.__class__.__name__, self.UNKNOWN
            )
        )
        self.parts.append(self.UNKNOWN)
