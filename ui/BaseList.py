import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets


class FileItem(QtWidgets.QListWidgetItem):

    def __init__(self, path, name=None):
        self.path = path.replace('\\', '/')
        if not name:
            self.name = path.rpartition("/")[2]
        else:
            self.name = name
        super().__init__(self.name)


class ListFile(QtWidgets.QListWidget):

    on_dropped = QtCore.Signal(list)

    def __init__(self, parent=None, default=False, **kwargs):
        super().__init__(parent, **kwargs)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.default = default

    def dragEnterEvent(self, event):

        if event.mimeData().hasUrls():
            event.acceptProposedAction() 
        else:
            super().dragEnterEvent(event)


    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)


    def dropEvent(self, event):

        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = [str(url.toLocalFile()) for url in event.mimeData().urls()]
            if self.default:
                for url in links:
                    self.add_file(url)
            self.on_dropped.emit(links)

        else:
            super().dropEvent(event)


    def add_file(self, path):
        self.listFiles.addItem(FileItem(path))


    def remove_file(self, item=None):
        if isinstance(item, QtWidgets.QListWidgetItem):
            self.takeItem(self.row(item))
            return

        selected_items = self.selectedItems()
        if not selected_items: return
        for item in selected_items:
            self.takeItem(self.row(item))
        