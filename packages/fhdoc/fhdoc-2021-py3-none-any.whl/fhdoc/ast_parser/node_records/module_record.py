"""
Wrapper for an `ast.Module` node with corresponding node info.
"""
import ast
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Text

from fhdoc.ast_parser.analyzers.module_analyzer import ModuleAnalyzer
from fhdoc.ast_parser.enums import RenderPart
from fhdoc.ast_parser.node_records.attribute_record import AttributeRecord
from fhdoc.ast_parser.node_records.class_record import ClassRecord
from fhdoc.ast_parser.node_records.function_record import FunctionRecord
from fhdoc.ast_parser.node_records.import_record import ImportRecord
from fhdoc.ast_parser.node_records.node_record import NodeRecord
from fhdoc.utils.import_string import ImportString
from fhdoc.utils.indent_trimmer import IndentTrimmer


class ModuleRecord(NodeRecord):
	"""
	Wrapper for an `ast.Module` node with corresponding node info.

	Responsible for parsing Python source as well.

	Arguments:
		node -- Result of `ast.parse`.
	"""
	def __init__(self, node):
		# type: (ast.Module) -> None
		super(ModuleRecord, self).__init__(node)
		self.all_names = [] # type: List[Text]
		self.class_records = [] # type: List[ClassRecord]
		self.function_records = [] # type: List[FunctionRecord]
		self.import_records = [] # type: List[ImportRecord]
		self.source_path = Path("")
		self.source_lines = [] # type: List[Text]
		self.name = "module"
		self.title = ""
		self.import_string = ImportString("")
		self.import_string_map = {} # type: Dict[ImportString, NodeRecord]
		self.docstring = self._get_docstring()

	@classmethod
	def create_from_source(cls, source_path, import_string):
		# type: (Path, ImportString) -> ModuleRecord
		"""
		Create new `ModuleRecord` from path.

		Arguments:
			source_path -- Path to a Python source file.
			import_string -- File absolute import string.

		Returns:
			New `ModuleRecord` instance.
		"""
		content = source_path.read_text(encoding="utf-8")
		node = ast.parse(content)
		if not isinstance(node, ast.Module):
			raise TypeError
		record = cls(node)
		record.import_string = import_string
		record.name = import_string.parts[-1]
		record.source_path = source_path
		record.source_lines = source_path.read_text(encoding="utf-8").split("\n")
		return record

	def find_record(self, import_string):
		# type: (ImportString) -> Optional[NodeRecord]
		"""
		Find child in the Module by an absolute or relative import string.

		Attributes:
			import_string -- record import string.

		Returns:
			Found child record on None.
		"""
		if import_string == self.import_string:
			return self

		result = self.import_string_map.get(import_string)
		if result:
			return result

		return None

	def iter_records(self):
		# type: () -> Generator[NodeRecord, None, None]
		"""
		Iterate over Module class, method and fucntion records.

		Yields:
			A child record.
		"""
		for class_record in self.class_records:
			if self.all_names and class_record.name not in self.all_names:
				continue

			yield class_record

			for class_child_record in class_record.iter_records():
				yield class_child_record

		for function_record in self.function_records:
			if self.all_names and function_record.name not in self.all_names:
				continue

			yield function_record

	def _set_import_strings(self):
		# type: () -> None
		for class_record in self.class_records:
			class_record.import_string = self.import_string + class_record.name
			self.import_string_map[class_record.import_string] = class_record

			for class_child_record in class_record.iter_records():
				class_child_record.import_string = (class_record.import_string
				+ class_child_record.name)

				self.import_string_map[
				class_child_record.import_string] = class_child_record

		for function_record in self.function_records:
			function_record.import_string = self.import_string + function_record.name
			self.import_string_map[function_record.import_string] = function_record

		for attribute_record in self.attribute_records:
			attribute_record.import_string = self.import_string + attribute_record.name
			self.import_string_map[attribute_record.import_string] = attribute_record

	def _render_parts(self, indent=0):
		# type: (int) -> List[Any]
		parts = [] # type: List[Any]
		if self.import_records:
			for import_record in self.import_records:
				parts.append(import_record)
				parts.append(RenderPart.LINE_BREAK)
			parts.append(RenderPart.LINE_BREAK)
		if self.class_records:
			for class_record in self.class_records:
				parts.append(class_record)
				parts.append(RenderPart.LINE_BREAK)
			parts.append(RenderPart.LINE_BREAK)
		for function_record in self.function_records:
			parts.append(function_record)
			parts.append(RenderPart.LINE_BREAK)

		return parts

	def build_children(self):
		# type: () -> None
		"""
		Collect full information about Module child records.

		Used only when doc for this ModuleRecord is building.
		"""
		analyzer = ModuleAnalyzer()
		analyzer.visit(self.node)

		self.all_names = analyzer.all_names

		for class_node in analyzer.class_nodes:
			self.class_records.append(ClassRecord(class_node))

		for function_node in analyzer.function_nodes:
			self.function_records.append(FunctionRecord(function_node, is_method=False))

		for attribute_node in analyzer.attribute_nodes:
			self.attribute_records.append(AttributeRecord(attribute_node))

		for import_node in analyzer.import_nodes:
			for alias in import_node.names:
				self.import_records.append(ImportRecord(import_node, alias))

		self.class_records.sort(key=lambda x: x.name)
		self.function_records.sort(key=lambda x: x.name)

		main_class_lookup_name = self.name.replace("_", "")
		for class_record in self.class_records:
			class_record.parse()
			# find real title
			if class_record.name.lower() == main_class_lookup_name:
				self.title = class_record.name

		self._set_import_strings()

	def _parse(self):
		# type: () -> None

		for attribute_record in self.attribute_records:
			attribute_record.docstring = self._get_comment_docstring(attribute_record)

		for class_record in self.class_records:
			class_record.parse()
			for attribute_record in class_record.attribute_records:
				attribute_record.docstring = self._get_comment_docstring(attribute_record)

			for method_record in class_record.method_records:
				method_record.parse()
				if method_record.is_classmethod or method_record.is_staticmethod:
					method_record.title = "{}.{}".format(class_record.name,
					method_record.name)
				else:
					method_record.title = "{}().{}".format(class_record.name,
					method_record.name)
				function_lines = self._get_function_def_lines(method_record)
				method_record.parse_type_comments(function_lines)

		for function_record in self.function_records:
			function_record.parse()
			function_lines = self._get_function_def_lines(function_record)
			function_record.parse_type_comments(function_lines)

	def _get_function_def_lines(self, function_record):
		# type: (FunctionRecord) -> List[Text]
		"""
		Get all function definition lines for comment type
		hints lookup.

		Removes indentation.

		Arguments:
			function_record -- Function record for source lookup.

		Returns:
			Function definition lines as an array.
		"""
		if not isinstance(function_record.node,
		(ast.AsyncFunctionDef, ast.FunctionDef)):
			raise TypeError

		result = [] # type: List[Text]
		start_index = function_record.line_number - 1
		end_index = function_record.node.body[0].lineno - 1
		result = self.source_lines[start_index:end_index]
		result = [i.rstrip("\n") for i in result]
		result = IndentTrimmer.trim_lines(result)
		return result

	def _get_comment_docstring(self, node_record):
		# type: (NodeRecord) -> Text
		"""
		Get comment docstring preceding the object from the source code.

		Returns only lines starting with `#`, lines joined with a single space.

		Arguments:
			node_record -- Node record for source lookup.

		Returns:
			A docstring as a string.
		"""
		if not isinstance(node_record.node, ast.Assign):
			raise TypeError

		result = [] # type: List[Text]
		start_index = node_record.node.lineno - 2

		try:
			start_line = self.source_lines[start_index].strip()
		except IndexError:
			return ""

		while start_index >= 0 and start_line.startswith("#"):
			line = start_line[1:].strip()
			if not line.startswith("FIXME") and not line.startswith("TODO"):
				result.append(line)
			start_index -= 1
			start_line = self.source_lines[start_index].strip()

		result.reverse()
		return "\n  ".join(result)
