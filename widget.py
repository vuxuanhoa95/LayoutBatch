import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets


class DragList(QtWidgets.QListWidget):

    on_dropped = QtCore.Signal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)

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
            links=[str(url.toLocalFile()) for url in event.mimeData().urls()]
            self.on_dropped.emit(links)

        else:
            super().dropEvent(event)

            