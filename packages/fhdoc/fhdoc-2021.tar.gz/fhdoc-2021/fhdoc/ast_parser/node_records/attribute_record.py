"""
Wrapper for an `ast.Assign` node of a module or class attribute.
"""
from typing import List, Text, Set, Optional, TYPE_CHECKING

from fhdoc.ast_parser.node_records.node_record import NodeRecord
from fhdoc.ast_parser.node_records.expression_record import ExpressionRecord
import ast

if TYPE_CHECKING:  # pragma: no cover
	from fhdoc.ast_parser.type_defs import RenderExpr


class AttributeRecord(NodeRecord):
	"""
	Wrapper for an `ast.Assign` node of a module or class attribute.

	Arguments:
		node -- AST node.
	"""

	def __init__(self, node):
		# type: (ast.Assign) -> None
		super(AttributeRecord, self).__init__(node)
		self.default = None  # type: Optional[ExpressionRecord]
		first_target = node.targets[0]
		if not isinstance(first_target, ast.Name):
			raise Exception
		self.name = first_target.id
		self.title = self.name
		self.value = ExpressionRecord(node.value)

	@property
	def related_names(self):
		# type: () -> Set[Text]
		result = set()  # type: Set[Text]
		if self.value:
			result.update(self.value.related_names)

		return result

	def _render_parts(self, indent=0):
		# type: (int) -> List[RenderExpr]
		parts = []  # type: List[RenderExpr]
		parts.append(self.name)
		parts.append(" = ")
		parts.append(self.value)
		return parts

	def _parse(self):
		# type: () -> None
		if self.value:
			self.value.parse()
