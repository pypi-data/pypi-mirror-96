"""
Different AST-related types collection.
"""
from typing import Union, Text

from fhdoc.ast_parser.node_records.node_record import NodeRecord
import ast
from fhdoc.ast_parser.enums import RenderPart

# Ready for render expression
RenderExpr = Union[NodeRecord, Text, RenderPart]

# AST node or text
Node = Union[Text, ast.AST]

# Not ready for render expression, AST has to be wrapped
DirtyRenderExpr = Union[ast.AST, Text, RenderPart]

# Iterable AST types
ASTIterable = Union[ast.List, ast.Set, ast.Tuple]

# AST import node
ASTImport = Union[ast.Import, ast.ImportFrom]

# AST import node
ASTFunctionDef = Union[ast.FunctionDef, ast.AsyncFunctionDef]
