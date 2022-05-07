from typing import TYPE_CHECKING, Any, cast

from PyQt5.QtCore import QModelIndex, QStringListModel, Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QVBoxLayout,
)

from library.library import Library
from ui.models.grouped_books.groups import Groups

if TYPE_CHECKING:
    from library.manager import LibraryManager


class GroupsDialog(QDialog):

    library: Library
    library_manager: "LibraryManager"

    available_groups_label: QLabel
    available_groups_model: QStringListModel
    available_groups_view: QListView
    button_box: QDialogButtonBox
    move_down_button: QPushButton
    move_up_button: QPushButton
    selected_groups_label: QLabel
    selected_groups_model: QStringListModel
    selected_groups_view: QListView

    def __init__(
        self,
        library_manager: "LibraryManager",
        library: Library,
        *args: Any,
        **kwargs: Any
    ) -> None:

        super().__init__(*args, **kwargs)

        self.library = library
        self.library_manager = library_manager

        layout = QVBoxLayout()

        h_layout = QHBoxLayout()

        self.available_groups_label = QLabel("Available groups:", self)
        h_layout.addWidget(self.available_groups_label)

        self.available_groups_model = QStringListModel(self)
        self.available_groups_model.setStringList(
            [g for g in Groups.keys() if g not in library.getGroups()]
        )

        self.available_groups_view = QListView(self)
        self.available_groups_view.setModel(self.available_groups_model)
        self.available_groups_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.available_groups_view.activated.connect(self.select_group)
        h_layout.addWidget(self.available_groups_view)
        self.available_groups_label.setBuddy(self.available_groups_view)

        self.selected_groups_label = QLabel("Selected groups:", self)
        h_layout.addWidget(self.selected_groups_label)

        self.selected_groups_model = QStringListModel(self)
        self.selected_groups_model.setStringList(library.getGroups())

        self.selected_groups_view = QListView(self)
        self.selected_groups_view.setModel(self.selected_groups_model)
        self.selected_groups_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.selected_groups_view.activated.connect(self.deselect_group)
        h_layout.addWidget(self.selected_groups_view)
        self.selected_groups_label.setBuddy(self.selected_groups_view)

        button_layout = QVBoxLayout()

        self.move_up_button = QPushButton("Move up", self)
        self.move_up_button.pressed.connect(self.move_selected_group_up)
        button_layout.addWidget(self.move_up_button)

        self.move_down_button = QPushButton("Move down", self)
        self.move_down_button.pressed.connect(self.move_selected_group_down)
        button_layout.addWidget(self.move_down_button)

        h_layout.addLayout(button_layout)

        layout.addLayout(h_layout)

        self.button_box = QDialogButtonBox(
            cast(
                QDialogButtonBox.StandardButton,
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            ),
            self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def select_group(self, index: QModelIndex) -> None:

        selected = self.available_groups_model.data(index, Qt.DisplayRole)

        self.available_groups_model.removeRows(index.row(), 1)

        self.selected_groups_model.insertRows(self.selected_groups_model.rowCount(), 1)
        self.selected_groups_model.setData(
            self.selected_groups_model.index(
                self.selected_groups_model.rowCount() - 1, 0
            ),
            selected,
            Qt.DisplayRole,
        )

    def accept(self) -> None:

        if not self.button_box.button(QDialogButtonBox.Ok).hasFocus():
            return

        self.library.setGroups(self.selected_groups_model.stringList())
        self.library_manager.save(self.library)
        self.library_manager.libraryUpdated.emit(self.library)

        super().accept()

    def deselect_group(self, index: QModelIndex) -> None:

        self.selected_groups_model.removeRows(index.row(), 1)

        self.available_groups_model.setStringList(
            [
                g
                for g in Groups.keys()
                if g not in self.selected_groups_model.stringList()
            ]
        )

    def move_selected_group_up(self) -> None:

        index: QModelIndex = self.selected_groups_view.currentIndex()

        if index.row() == 0:
            return

        self.selected_groups_model.moveRows(
            QModelIndex(), index.row(), 1, QModelIndex(), index.row() - 1
        )

    def move_selected_group_down(self) -> None:

        index: QModelIndex = self.selected_groups_view.currentIndex()

        if index.row() == self.selected_groups_model.rowCount():
            return

        self.selected_groups_model.moveRows(
            QModelIndex(), index.row(), 1, QModelIndex(), index.row() + 1
        )
