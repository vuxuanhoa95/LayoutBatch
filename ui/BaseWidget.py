import os
import sys
from typing import Optional

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from ui import BaseList, BaseInput


class BaseSidePanel(QWidget):


    def __init__(self, parent: QWidget):
        super().__init__(parent)

        verticalLayout = QVBoxLayout(self)

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

        # execute
        self.buttonExec = QPushButton("Execute", self)
        self.buttonExec.clicked.connect(self.execute)
        verticalLayout.addWidget(self.buttonExec)


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
    

    def execute(self):
        print("Execute ne")


class BaseMdiSubWindow(QMdiSubWindow):


    def __init__(self, parent: QWidget, **kwargs) -> None:
        super().__init__(parent, **kwargs)

        self.setAttribute(Qt.WA_DeleteOnClose)

        sub_win_main_widget = QWidget(self)
        v_layout = QVBoxLayout(sub_win_main_widget)
        v_layout.addWidget(QTextEdit("Sub window"))

        self.setWidget(sub_win_main_widget)


class BaseMdiUI:
    """The ui class of mdi window."""

    def _make_mdi_area_test_widget(self, enable_tab_mode=False):
        # Widgets
        self.container = QWidget()
        self.mdi_area = QMdiArea()
        label_test_name = QLabel()
        cascade_button = QPushButton("Cascade")
        new_button = QPushButton("Add new")
        tiled_button = QPushButton("Tiled")

        # Setup widgets
        if enable_tab_mode:
            self.mdi_area.setViewMode(QMdiArea.ViewMode.TabbedView)
            self.mdi_area.setTabsClosable(True)
            self.mdi_area.setTabsMovable(True)
            label_test_name.setText("QMdiArea(QMdiArea.viewMode = TabbedView)")
        else:
            label_test_name.setText("QMdiArea(QMdiArea.viewMode = SubWindowView)")

        new_button.pressed.connect(lambda: self.add_window(BaseMdiSubWindow(self.container)))
        cascade_button.pressed.connect(self.mdi_area.cascadeSubWindows)
        tiled_button.pressed.connect(self.mdi_area.tileSubWindows)
        new_button.setDefault(True)

        # Layout
        h_layout = QHBoxLayout()
        h_layout.addWidget(new_button)
        h_layout.addWidget(cascade_button)
        h_layout.addWidget(tiled_button)

        v_main_layout = QVBoxLayout(self.container)
        v_main_layout.addWidget(label_test_name)
        v_main_layout.addLayout(h_layout)
        v_main_layout.addWidget(self.mdi_area)
        return self.container
    
    def add_window(self, window: QMdiSubWindow):
        self.mdi_area.addSubWindow(window)
        window.show()

    def setup_ui(self, win: QWidget) -> None:
        """Set up ui."""
        # Widgets
        splitter = QSplitter()

        # Setup widgets
        # mdi_area = self._make_mdi_area_test_widget()
        mdi_area_with_tab = self._make_mdi_area_test_widget(enable_tab_mode=True)

        # Layout
        # splitter.addWidget(mdi_area)
        splitter.addWidget(mdi_area_with_tab)

        main_layout = QVBoxLayout(win)
        main_layout.addWidget(splitter)