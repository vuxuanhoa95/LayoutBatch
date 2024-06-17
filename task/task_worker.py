from io import TextIOWrapper
import re
import time

import uuid

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from utils import maya_launcher


def create_icon_by_color(color):
    pixmap = QPixmap(256, 256)
    pixmap.fill(color)
    return QIcon(pixmap)


class _Worker(QProcess):

    on_log = Signal(str)
    on_stdout = Signal(str)
    on_stderr = Signal(str)

    on_progress = Signal(int, int)
    on_finished = Signal(int)
    on_state_changed = Signal(int)
    on_error_occurred = Signal(int)

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)

        self.id = uuid.uuid4().hex

        self.readyReadStandardOutput.connect(self.handle_stdout)
        self.readyReadStandardError.connect(self.handle_stderr)

        self.started.connect(self.handle_started)
        self.finished.connect(self.handle_finished)
        self.stateChanged.connect(self.handle_state)
        self.errorOccurred.connect(self.handle_error)

        self.start_time = 0
        self.end_time = 0
        self.logfile = None
        self.logfileIO = None
        self.real_progress = False
        self.progress = 0
        self.progress_count = 100

    def handle_state(self, state: QProcess.ProcessState):
        self.on_state_changed.emit(state.value)

    def handle_error(self, error: QProcess.ProcessError):
        self.on_error_occurred.emit(error.value)

    def handle_started(self):
        self.start_time = time.time()
        if self.logfile:
            try:
                self.logfileIO = open(self.logfile, 'w')
            except:
                pass

    def handle_finished(self):
        self.end_time = time.time()
        self.on_finished.emit(self.exitCode())
        if isinstance(self.logfileIO, TextIOWrapper):
            self.logfileIO.close()

    def handle_stderr(self):
        data = self.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.on_stderr.emit(stderr)
        if isinstance(self.logfileIO, TextIOWrapper):
            self.on_log.emit(stderr)
            self.logfileIO.write(stderr)

    def handle_stdout(self):
        data = self.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.on_stdout.emit(stdout)
        # self.handle_progress(stdout)
        if isinstance(self.logfileIO, TextIOWrapper):
            self.on_log.emit(stdout)
            self.logfileIO.write(stdout)

    def handle_progress(self, data):
        if not self.real_progress:
            pattern_0 = r'(?:PROGRESSCOUNT:)(\d+)'
            match_0 = re.search(pattern_0, data)
            if match_0:
                self.real_progress = True
                self.progress_count = int(match_0.group(1))
                self.progress = 0
                print('set progresscount', self.progress_count)
                self.on_progress.emit(self.progress, self.progress_count)
                return
            
            else:
                self.progress += 1
                if self.progress >= 100:
                    self.progress = 1
                self.on_progress.emit(self.progress, self.progress_count)
                return
        
        else:
            pattern_1 = r'(?:PROGRESS:)(\d+)'
            match_1 = re.search(pattern_1, data)
            if match_1:
                self.progress = int(match_1.group(1))
                # self.progress += 1
                print('set progress', self.progress)
                self.on_progress.emit(self.progress, self.progress_count)
                

class _TaskViewerUI:


    def setupUi(self, mdi_window: QMdiSubWindow):

        # main widget
        self.mainWidget = QWidget(mdi_window)
        mdi_window.setWidget(self.mainWidget)

        # layout
        v_layout = QVBoxLayout(self.mainWidget)

        # execute
        self.btn_stop = QPushButton("Stop")
        v_layout.addWidget(self.btn_stop)

        self.labelError = QLabel(mdi_window)
        v_layout.addWidget(self.labelError)

        self.progressBar = QProgressBar(mdi_window)
        self.progressBar.setTextVisible(True)
        v_layout.addWidget(self.progressBar)

        # terminal
        self.outLog = QTextEdit(mdi_window)
        self.outLog.setReadOnly(True)
        v_layout.addWidget(self.outLog)


class TaskViewer(QMdiSubWindow):

    STATE = ["NotRunning", "Starting", "Running", "Pending"]
    ERROR = ["FailedToStart", "Crashed", "Timedout", "WriteError", "ReadError", "UnknownError"]
    EXIT = ["Finished", "Crashed"]
    LEVEL = ["info", "notify", "alert"]

    finished = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(create_icon_by_color(QColor("transparent")))

        self._ui = _TaskViewerUI()
        self._ui.setupUi(self)

        self._ui.btn_stop.clicked.connect(self.kill)

        # setup worker
        self.worker: _Worker = _Worker(self)
        self.worker.on_stdout.connect(lambda x: self._on_log(x, level="info"))
        self.worker.on_stderr.connect(lambda x: self._on_log(x, level="alert"))
        self.worker.on_state_changed.connect(self._on_state)
        self.worker.on_error_occurred.connect(self._on_error)
        self.worker.on_finished.connect(self._on_finished)

        self._on_state(-1)
        self.setWindowTitle(self.worker.id)

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        if self.worker.state().value != 0:
            result = QMessageBox.question(self, "Confirm Close...", "Are you sure you want to kill process?")
            if result == QMessageBox.Yes:
                self.worker.kill()
                self.worker.waitForFinished()
                event.accept()
        else:
            self.finished.emit()
            event.accept()

    def run(self):
        mayapy = maya_launcher.mayapy(2024)
        python = "python"
        script = r'D:\Github\LayoutBatch\preset\test_count.py'
        print(mayapy, script)
        # self.worker.setProgram(str(mayapy))
        # self.worker.setArguments(f'"{script}"')
        self.worker.startCommand(f'"{python}" "{script}"')
        pass

    def kill(self):
        if self.worker.state() != QProcess.NotRunning:
            result = QMessageBox.question(self, "Confirm Stop...", "Are you sure you want to kill process?")
            if result == QMessageBox.Yes:
                self.worker.kill()
        else:
            self.worker.kill()
            self.worker.waitForFinished()
            self._on_finished(0)

    def _on_log(self, log: str, level="info"):
        self._ui.outLog.verticalScrollBar().setValue(self._ui.outLog.verticalScrollBar().maximum())
        if level == self.LEVEL[2]:
            line = f'<font color=\"Red\">{log}</font><br>'
            self._ui.outLog.insertHtml(line)
        else:
            self._ui.outLog.insertPlainText(log)

        progress = self._ui.progressBar.value() + 1
        if progress >= 100:
            self._ui.progressBar.setValue(1)
        else:
            self._ui.progressBar.setValue(progress)

    def _on_state(self, state: int):
        self._ui.labelError.setText(self.STATE[state])

    def _on_error(self, error: int):
        self._ui.labelError.setText(self.ERROR[error])

    def _on_finished(self, exitCode):
        total_time = self.worker.end_time - self.worker.start_time
        exit_status = self.worker.exitStatus()
        self._ui.labelError.setText(f"{self.EXIT[exit_status.value]} - {total_time:.03f} sec")
        self._ui.progressBar.setValue(100)

        result = f'<font color=\"Orange\">--RESULT--</font><br>'
        result += f'<font color=\"Orange\">{self.worker.error()}</font><br>'
        result += f'<font color=\"Orange\">{exit_status}: {exitCode}</font><br>'
        result += f'<font color=\"Orange\">Execution time: {total_time:.03f} sec</font><br>'
        self._ui.outLog.insertHtml(result)

        self.finished.emit()
            