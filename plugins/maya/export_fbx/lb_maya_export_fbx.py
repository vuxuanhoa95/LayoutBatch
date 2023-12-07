import os
import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from main import MainWindow, FileItem
from widget import DragList
from ui import BaseWidget


plugin = None


def load(core):
    global plugin
    if not plugin:
        # plugin = LB_Maya_Export_FBX(core)
        plugin = MayaExportFBX(core)

    return plugin


def run():
    if plugin:
        plugin.run()


class MayaExportFBX(BaseWidget.BaseSidePanel):

    def __init__(self, core):
        self.core: MainWindow = core
        super().__init__(self.core)
        print('Initializing...', self.__class__)

        self.label.setText("Export FBX")


class LB_Maya_Export_FBX(QObject):


    def __init__(self, core):
        super().__init__()
        print('Initializing...', self.__class__)
        self.core: MainWindow = core

        # init ui
        Form = QWidget()
        verticalLayout = QVBoxLayout(Form)

        # label
        verticalLayout.addWidget(QLabel("Export FBX", Form))

        # list files
        self.listFiles = DragList(Form)
        self.listFiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
        verticalLayout.addWidget(self.listFiles)
        self.listFiles.on_dropped.connect(self.handle_drop)
        self.listFiles.installEventFilter(self)

        # output dir
        self.lineEdit = QLineEdit(Form)
        verticalLayout.addWidget(self.lineEdit)

        self.widget = Form


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

    def handle_drop(self, links):
        for url in links:
            if os.path.exists(url):
                self.add_file(url)

    def add_file(self, path):
        if os.path.exists(path):
            item = FileItem(os.path.basename(path), path)
            self.listFiles.addItem(item)
            print('Added file', path)

    def run(self):
        pass
        # self.core.job.queue_process(t.path, f)
