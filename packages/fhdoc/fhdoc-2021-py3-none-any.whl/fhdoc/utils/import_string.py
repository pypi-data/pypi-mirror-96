"""
Wrapper for python import strings.
"""
from typing import Text, List


class ImportStringError(Exception):
	"""
	Main error for `ImportString`.
	"""


class ImportString:
	"""
	Wrapper for python import strings.

	Arguments:
		value -- Import string.
	"""

	def __init__(self, value):
		# type: (Text) -> None
		self.value = value

	def __str__(self):
		# type: () -> Text
		"""
		Get string value.

		Examples::

			str(ImportString("my_module"))
			"my_module"

		Returns:
			Original import string.
		"""
		return self.value

	def __hash__(self):
		# type: () -> int
		return hash(self.value)

	def __add__(self, other):
		# type: (Text) -> ImportString
		"""
		Add new import part.

		Examples::

			ImportString("my_module") + "MyClass"
			ImportString("my_module.MyClass")

			ImportString("") + "MyClass"
			ImportString("MyClass")

		Arguments:
			other -- Import string part.

		Returns:
			A new `ImportString` instance.
		"""
		if self.value:
			return ImportString("{}.{}".format(self.value, other))

		return ImportString(other)

	def __bool__(self):
		# type: () -> bool
		"""
		Check if not empty.

		Examples::

			bool(ImportString("my_module"))
			True

			bool(ImportString(""))
			False

		Returns:
			True if not empty.
		"""
		return bool(self.value)

	def __eq__(self, other):
		# type: (object) -> bool
		"""
		Compare to another `ImportString` or a string.

		Examples::

			ImportString("my_module.MyClass") == ImportString("my_module.MyClass")
			True

			ImportString("my_module.MyClass") == ImportString("my_module.OtherClass")
			False

			ImportString("my_module.MyClass") == "my_module.MyClass"
			True

			ImportString("my_module.MyClass") == "my_module"
			False

			ImportString("my_module.MyClass") == b"my_module.MyClass"
			False

		Arguments:
			other - ImportString instance or a string.

		Returns:
			True if import strings are equal.
		"""
		if isinstance(other, str):
			return self.value == other

		if isinstance(other, ImportString):
			return self.value == other.value

		return False

	@property
	def parts(self):
		# type: () -> List[Text]
		"""
		Parts of import string splitted by dots.

		Examples::

			ImportString("my_module.MyClass")
			["my_module", "MyClass"]

			ImportString("")
			[]

		Returns:
			A list of import string parts.
		"""
		return self.value.split(".")

	def is_top_level(self):
		# type: () -> bool
		"""
		Check if import string has no parents.

		Returns:
			True if it has no parents.
		"""
		return "." not in self.value

	@property
	def parent(self):
		# type: () -> ImportString
		"""
		Parent import string.

		Returns:
			A new `ImportString` instance.
		"""
		if self.is_top_level():
			raise ImportStringError("Import string is top level and has no parents.")

		parent_import_string_parts = self.value.split(".")[:-1]
		return ImportString(".".join(parent_import_string_parts))

	def startswith(self, import_string):
		# type: (ImportString) -> bool
		"""
		Check if it starts with `import_string`.

		Returns:
			True if it is a child.
		"""
		return self.value.startswith("{}.".format(import_string))
