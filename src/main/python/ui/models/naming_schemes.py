from typing import Any, List

from PyQt5.QtGui import QStandardItem, QStandardItemModel

from configuration_manager import ConfigurationManager
from library.naming_scheme import NamingScheme


class NamingSchemesModel(QStandardItemModel):

    _schemes: List[NamingScheme]

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self._schemes = []

        self.reloadSchemes()

    def reloadSchemes(self) -> None:

        self.clear()

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Name", "Standalone book", "Series volume"])

        self._schemes = ConfigurationManager().namingSchemes
        scheme: NamingScheme

        for scheme in self._schemes:

            item: QStandardItem
            row: List[QStandardItem] = []

            item = QStandardItem(scheme.name)
            item.setEditable(False)
            row.append(item)

            item = QStandardItem(scheme.standalone.getResolved())
            item.setEditable(False)
            row.append(item)

            item = QStandardItem(scheme.volume.getResolved())
            item.setEditable(False)
            row.append(item)

            self.appendRow(row)
