"""
Wrapper for an `ast.Import` and `ast.ImportFrom` nodes.
"""
from typing import Text, Optional, List, TYPE_CHECKING

from fhdoc.ast_parser.node_records.node_record import NodeRecord
import ast
from fhdoc.utils.import_string import ImportString

if TYPE_CHECKING:  # pragma: no cover
    from fhdoc.ast_parser.type_defs import RenderExpr, ASTImport


class ImportRecord(NodeRecord):
    """
    Wrapper for an `ast.Import` and `ast.ImportFrom` nodes.

    Arguments:
        node -- AST node.
        alias -- AST node with import alias.
    """

    def __init__(self, node, alias):
        # type: (ASTImport, ast.alias) -> None
        super(ImportRecord, self).__init__(node)
        self.source = None
        if isinstance(node, ast.ImportFrom):
            self.name = alias.name
            self.source = node.module
            self.local_name = alias.asname or alias.name
        if isinstance(node, ast.Import):
            self.name = alias.name
            self.local_name = alias.asname or alias.name

    def get_import_string(self):
        # type: () -> ImportString
        """
        Get import string from a node.

        Returns:
            An absolute import string.
        """
        if self.source:
            return ImportString(self.source) + self.name

        return ImportString(self.name)

    def _render_parts(self, indent=0):
        # type: (int) -> List[RenderExpr]
        if self.source:
            if self.local_name != self.name:
                return [
                    "from {} import {} as {}".format(
                        self.source, self.name, self.local_name
                    )
                ]
            return ["from {} import {}".format(self.source, self.name)]

        if self.local_name != self.name:
            return ["import {} as {}".format(self.name, self.local_name)]

        return ["import {}".format(self.name)]

    def match(self, name):
        # type: (Text) -> Optional[ImportString]
        """
        Check if `name` matches or stats with a local name.

        Examples::

            import_node = ast.parse('from my_module import Name as LocalName')
            import_record = ImportRecord(import_node)

            import_record.match('LocalName')
            True

            import_record.match('LocalName.child')
            True

            import_record.match('OtherName')
            False

            import_record.match('LocalNameOther')
            False

        Returns:
            True if name is imported object itself on one of his children.
        """
        if name == self.local_name:
            return self.get_import_string()

        lookup = "{}.".format(self.local_name)
        if name.startswith(lookup):
            if self.source:
                trailing_import = name[len(lookup) :]
                return ImportString(
                    "{}.{}".format(self.get_import_string(), trailing_import)
                )

        return None

    def _parse(self):
        # type: () -> None
        return
