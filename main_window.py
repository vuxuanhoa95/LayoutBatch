"""Main module of widget gallery."""
import qdarktheme
from qdarktheme._util import get_qdarktheme_root_path
from PySide6.QtCore import QDir, Qt, Slot
from PySide6.QtGui import QAction, QActionGroup, QFont, QIcon, QCloseEvent
from PySide6.QtWidgets import (
    QColorDialog,
    QFileDialog,
    QFontDialog,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QToolButton,
    QWidget,
)

from main_window_ui import Ui_MainWindow
from task.task_manager import TaskManager


class _MainWindowUI(Ui_MainWindow):

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        # menu
        self.actions_theme = [QAction(theme, MainWindow) for theme in ["auto", "dark", "light"]]
        self.menuTheme.addActions(self.actions_theme)

        menu_maxProcesses = self.menuOptions.addMenu("&Max Processes")
        self.actions_maxProcesses = [QAction(str(n+1), MainWindow) for n in range(4)]
        menu_maxProcesses.addActions(self.actions_maxProcesses)

        max_group = QActionGroup(MainWindow)
        max_group.setExclusive(True)
        for a in self.actions_maxProcesses:
            a.setCheckable(True)
            max_group.addAction(a)
        self.actions_maxProcesses[-1].setChecked(True)


        # toolbar
        self.action_open_folder = QAction(QIcon("icons:folder_open_24dp.svg"), "Open folder dialog")
        self.toolbar = QToolBar("Toolbar")
        MainWindow.addToolBar(self.toolbar)

        self.toolbar.addActions(
            (self.action_open_folder,)
        )


        # activity bar
        activitybar = QToolBar("activitybar")
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, activitybar)

        self.actions_page = (
            QAction(QIcon("icons:widgets_24dp.svg"), "Move to widgets"),
            QAction(QIcon("icons:flip_to_front_24dp.svg"), "Move to dock"),
            QAction(QIcon("icons:crop_din_24dp.svg"), "Move to frame"),
            QAction(QIcon("icons:branding_watermark_24dp.svg"), "Move to mdi"),
            QAction(QIcon("icons:image_24dp.svg"), "Move to icons"),
        )
        activitybar.setMovable(False)
        activitybar.addActions(self.actions_page)

        spacer = QToolButton()
        spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        spacer.setEnabled(False)
        activitybar.addWidget(spacer)


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        """Initialize the WidgetGallery class."""
        super().__init__()
        QDir.addSearchPath("icons", f"{get_qdarktheme_root_path().as_posix()}/widget_gallery/svg")
        self._ui = _MainWindowUI()
        self._ui.setupUi(self)
        self._theme = "dark"
        self._corner_shape = "rounded"

        # menu theme
        for action in self._ui.actions_theme:
            action.triggered.connect(self._change_theme)

        # main widget
        self.taskManager = TaskManager(self)
        self._ui.stackedWidget.addWidget(self.taskManager)

    
    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        if self.taskManager.close():
            event.accept()
        # menu options
        

    @Slot()
    def _change_theme(self) -> None:
        self._theme = self.sender().text()  # type: ignore
        qdarktheme.setup_theme(self._theme, self._corner_shape)
