import os
import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from ui import BaseList, BaseInput


class BaseSidePanel(QWidget):


    def __init__(self, parent: QWidget):
        super().__init__(parent)

        verticalLayout = QVBoxLayout(self)
        verticalLayout.setContentsMargins(3, 3, 3, 3)

        # label
        self.label = QLabel("Base Side Panel", self)
        verticalLayout.addWidget(self.label)
        
        # list files
        self.listFiles = BaseList.ListFile(self, default=True)
        self.listFiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        verticalLayout.addWidget(self.listFiles)
        self.listFiles.installEventFilter(self)

        # output dir
        self.outputFile = BaseInput.InputFilePath(self)
        verticalLayout.addWidget(self.outputFile)


    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        event_type = event.type()
        if event_type == QEvent.ContextMenu:
            menu = QMenu()
            if source == self.listFiles:
                a = QAction('Add files', self)
                a.triggered.connect(lambda: self.load_file())
                menu.addAction(a)
                menu.addSeparator()
                item = source.itemAt(event.pos())
                if item:
                    a = QAction('Remove files', self)
                    a.triggered.connect(lambda: self.remove_file())
                    menu.addAction(a)
            menu.exec(QCursor.pos())
            del menu

        return super().eventFilter(source, event)
