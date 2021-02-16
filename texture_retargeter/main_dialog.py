import os
import pymel.core as pm
import pymel.api as pma
from PySide2 import QtWidgets
from shiboken2 import wrapInstance


def maya_main_window():
    main_window_ptr = pma.MQtUtil_mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)  # noqa: F821


class MainDialog(QtWidgets.QDialog):

    INSTANCE = None  # type: MainDialog

    def __init__(self, parent=maya_main_window()):
        super(MainDialog, self).__init__(parent)

        self.setWindowTitle("Texture retargeter")
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.update_nodes_list()

    @classmethod
    def display(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = cls()
        if cls.INSTANCE.isHidden():
            cls.INSTANCE.show()
        else:
            cls.INSTANCE.raise_()
            cls.INSTANCE.activateWindow()

    def create_widgets(self):
        self.new_dir_widget = DirectoryWidget(default_dir="", label="Path:")
        self.file_nodes_list = QtWidgets.QListWidget()
        self.file_nodes_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.refresh_list_button = QtWidgets.QPushButton("Update list")
        self.retarget_button = QtWidgets.QPushButton("Retarget")

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.new_dir_widget)
        self.main_layout.addWidget(self.file_nodes_list)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.refresh_list_button)
        self.main_layout.addWidget(self.retarget_button)

    def create_connections(self):
        self.refresh_list_button.clicked.connect(self.update_nodes_list)
        self.retarget_button.clicked.connect(self.retarget_nodes)

    def update_nodes_list(self):
        self.file_nodes_list.clear()
        file_nodes = pm.ls(type="file")
        for fnode in file_nodes:
            file_path = fnode.fileTextureName.get()
            if not file_path:
                continue
            list_item = QtWidgets.QListWidgetItem(fnode.name())
            list_item.setData(1, file_path)
            list_item.setToolTip(file_path)
            self.file_nodes_list.addItem(list_item)

    def retarget_nodes(self):
        list_items = self.file_nodes_list.selectedItems()
        if not list_items:
            list_items = self.qlist_all_items(self.file_nodes_list)
        for file_item in list_items:
            try:
                file_node = pm.PyNode(file_item.data(0))
            except Exception:
                pm.warning("Node {0} no longer exists, skipping".format(file_item.data(0)))
                continue
            new_path = self.get_new_path(file_item.data(1), self.new_dir_widget.line_edit.text())
            file_node.fileTextureName.set(new_path)

    def get_new_path(self, old_path, new_dir):
        file_name = os.path.basename(old_path)
        if file_name in os.listdir(new_dir):
            new_path = os.path.join(new_dir, file_name)
        else:
            new_path = old_path
        return new_path

    def qlist_all_items(self, qlist):
        if not isinstance(qlist, QtWidgets.QListWidget):
            raise TypeError("Invalid widget type. Must be QListWidget")
        items = []
        for index in range(qlist.count()):
            items.append(qlist.item(index))
        return items


class DirectoryWidget(QtWidgets.QGroupBox):
    def __init__(self, parent=None, default_dir="", label="Destination", browse_title="Select directory"):
        super(DirectoryWidget, self).__init__(parent)
        self.default_dir = default_dir
        self.label_text = label
        self.browse_title = browse_title

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.label = QtWidgets.QLabel(self.label_text)
        self.line_edit = QtWidgets.QLineEdit(self.default_dir)
        self.browse_button = QtWidgets.QPushButton("Browse...")

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.addWidget(self.browse_button)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.browse_button.clicked.connect(self.browse_path)

    def browse_path(self):
        """Get directory path from QFileDialog"""
        path = QtWidgets.QFileDialog.getExistingDirectory(self, self.browse_title, self.line_edit.text())
        if path:
            self.line_edit.setText(path)


if __name__ == "__main__":
    MainDialog.display()
