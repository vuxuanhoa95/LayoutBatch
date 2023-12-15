from typing import Optional
import uuid
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from task.task_worker import Worker
from utils import maya_launcher

from qdarktheme._style_loader import load_palette, load_stylesheet


def create_icon_by_color(color):
    pixmap = QPixmap(256, 256)
    pixmap.fill(color)
    return QIcon(pixmap)


class _TaskUI:


    def setupUi(self, mdi_window: QMdiSubWindow):

        # main widget
        self.mainWidget = QWidget(mdi_window)
        mdi_window.setWidget(self.mainWidget)

        # layout
        v_layout = QVBoxLayout(self.mainWidget)

        # # execute
        # self.button_exec = QPushButton("Execute")
        # v_layout.addWidget(self.button_exec)

        self.labelError = QLabel(mdi_window)
        v_layout.addWidget(self.labelError)

        self.progressBar = QProgressBar(mdi_window)
        self.progressBar.setTextVisible(True)
        v_layout.addWidget(self.progressBar)

        # terminal
        self.outLog = QTextEdit(mdi_window)
        self.outLog.setReadOnly(True)
        v_layout.addWidget(self.outLog)


class TitleProxyStyle(QProxyStyle):
    def drawComplexControl(self, control, option, painter, widget=None):
        if control == QStyle.CC_TitleBar:
            if hasattr(widget, "titleColor"):
                color = widget.titleColor
                if color.isValid():
                    option.palette.setBrush(
                        QPalette.Highlight, QColor(color)
                    )
            option.icon = create_icon_by_color(QColor("transparent"))
        super(TitleProxyStyle, self).drawComplexControl(
            control, option, painter, widget
        )


class Task(QMdiSubWindow):

    STATE = ["NotRunning", "Starting", "Running"]
    ERROR = ["FailedToStart", "Crashed", "Timedout", "WriteError", "ReadError", "UnknownError"]
    LEVEL = ["info", "notify", "alert"]

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        # self.setWindowIcon(QIcon("icons:branding_watermark_24dp.svg"))
        self.setWindowIcon(create_icon_by_color(QColor("transparent")))

        self._ui = _TaskUI()
        self._ui.setupUi(self)

        self.taskId = uuid.uuid4().hex

        self.setWindowTitle(self.taskId)

        self.process = Worker(self)
        self.process.on_stdout.connect(lambda x: self._on_log(x, level="info"))
        self.process.on_stderr.connect(lambda x: self._on_log(x, level="alert"))
        self.process.on_state_changed.connect(self._on_state)
        self.process.on_error_occurred.connect(self._on_error)
        self.process.on_finished.connect(self._on_finished)

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        if self.process.state().value != 0:
            result = QMessageBox.question(self, "Confirm Exit...", "Are you sure you want to kill process?")
            if result == QMessageBox.Yes:
                self.process.kill()
                self.process.waitForFinished()
                event.accept()
        else:
            event.accept()

    def run(self):
        mayapy = maya_launcher.mayapy(2024)
        python = "python"
        script = r'D:\Github\LayoutBatch\preset\test_maya_standalone.py'
        print(mayapy, script)
        # self.worker.setProgram(str(mayapy))
        # self.worker.setArguments(f'"{script}"')
        self.process.startCommand(f'"{mayapy}" "{script}"')
        pass

    def kill(self):
        self.process.kill()

    def _on_log(self, log: str, level="info"):
        self._ui.outLog.verticalScrollBar().setValue(self._ui.outLog.verticalScrollBar().maximum())
        if level == self.LEVEL[2]:
            line = f'<font color=\"DeepPink\">{log}</font><br>'
            self._ui.outLog.insertHtml(line)
        else:
            self._ui.outLog.insertPlainText(log)

        progress = self._ui.progressBar.value() + 1
        if progress >= 100:
            self._ui.progressBar.setValue(1)
        else:
            self._ui.progressBar.setValue(progress)

    def _on_state(self, state: int):
        print(self.taskId, self.process.error())
        self.setWindowTitle(f"{self.taskId} - {self.STATE[state]}")

    def _on_error(self, error: int):
        print(self.taskId, self.process.error())
        self._ui.labelError.setText(self.ERROR[error])

    def _on_finished(self, end_time):
        self._ui.labelError.setText(f"Execution time: {end_time:.03f} sec")
        self.setWindowTitle(f"{self.taskId} - Finished")
        self._ui.progressBar.setValue(100)
        

class _TaskManagerUI:
    """The ui class of mdi window."""

    def setupUi(self, widget: QWidget) -> None:
        """Set up ui."""
        main_layout = QVBoxLayout(widget)
        splitter = QSplitter()
        main_layout.addWidget(splitter)

        self.stackedWidget = QStackedWidget(widget)
        splitter.addWidget(self.stackedWidget)

        self.container = QWidget()
        splitter.addWidget(self.container)

        v_main_layout = QVBoxLayout(self.container)

        self.mdi_area = QMdiArea()
        v_main_layout.addWidget(self.mdi_area)

        h_layout = QHBoxLayout()
        v_main_layout.addLayout(h_layout)

        self.buttonNew = QPushButton("Add new")
        self.buttonCascade = QPushButton("Cascade")
        self.buttonTiled = QPushButton("Tiled")
        h_layout.addWidget(self.buttonNew)
        h_layout.addWidget(self.buttonCascade)
        h_layout.addWidget(self.buttonTiled)


class TaskManager(QWidget):


    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._ui = _TaskManagerUI()
        self._ui.setupUi(self)

        self._ui.buttonNew.pressed.connect(lambda: self.add_window())
        self._ui.buttonCascade.pressed.connect(self._ui.mdi_area.cascadeSubWindows)
        self._ui.buttonTiled.pressed.connect(self._ui.mdi_area.tileSubWindows)
        self._ui.buttonNew.setDefault(True)

    
    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        running_tasks = []
        for t in self.tasks:
            if t.process.state().value != 0:
                running_tasks.append(t)

        if running_tasks:
            message = "Some processes are running:\n"
            for t in running_tasks:
                message += f"{t.taskId}: {t.process.state()}\n"

            result = QMessageBox.question(self, "Confirm Exit...", f"{message}.\nAre you sure to close?")
            if result == QMessageBox.Yes:
                for t in self.tasks:
                    t.process.kill()
                    t.process.waitForFinished()
                event.accept()
        else:
            event.accept()

    @property
    def tasks(self) -> list[Task]:
        return [w for w in self._ui.mdi_area.subWindowList() if isinstance(w, Task)]


    def add_window(self):
        window = Task(self._ui.container)

        self._ui.mdi_area.addSubWindow(window)
        window.show()
        window.run()
