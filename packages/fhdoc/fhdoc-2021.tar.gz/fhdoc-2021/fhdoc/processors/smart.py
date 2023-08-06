"""
# Smart Docstring Processor

Docstring processor that selects a `DocstringProcessor` based on a docstring content:

- `fhdoc.processors.pep257.PEP257DocstringProcessor`
- `fhdoc.processors.rst.RSTDocstringProcessor`
"""

from typing import Text, TYPE_CHECKING

from fhdoc.processors.rst import RSTDocstringProcessor
from fhdoc.processors.pep257 import PEP257DocstringProcessor
from fhdoc.processors.base import BaseDocstringProcessor

if TYPE_CHECKING:  # pragma: no cover
	from fhdoc.processors.section_map import SectionMap


class SmartDocstringProcessor(BaseDocstringProcessor):
	"""
	Docstring processor that selects a `DocstringProcessor` based on a docstring content.
	"""

	def __init__(self):
		# type: () -> None
		self._pep257_processor = PEP257DocstringProcessor()
		self._rst_processor = RSTDocstringProcessor()
		super(SmartDocstringProcessor, self).__init__()

	def _parse_line(self, line):
		# type: (Text) -> None
		pass

	def build_sections(self, content):
		# type: (Text) -> SectionMap
		"""
		Parse docstring and split it to sections with arrays of strings.

		Arguments:
			content -- Object docstring.

		Returns:
			A dictionary where key is a section name and value is a list of string sof this
			section.
		"""
		stripped_lines = content.split("\n")

		pep257_keywords = self._pep257_processor.section_name_map.keys()
		for keyword in pep257_keywords:
			if keyword in stripped_lines:
				return self._pep257_processor.build_sections(content)

		return self._rst_processor.build_sections(content)
