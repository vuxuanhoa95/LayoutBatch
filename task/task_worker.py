from io import TextIOWrapper
import re
import time

from PySide6.QtCore import QProcess, Signal, QObject


class Worker(QProcess):

    on_log = Signal(str)
    on_stdout = Signal(str)
    on_stderr = Signal(str)

    on_progress = Signal(int, int)
    on_finished = Signal(float)
    on_state_changed = Signal(int)
    on_error_occurred = Signal(int)

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)

        self.readyReadStandardOutput.connect(self.handle_stdout)
        self.readyReadStandardError.connect(self.handle_stderr)

        self.started.connect(self.handle_started)
        self.finished.connect(self.handle_finished)
        self.stateChanged.connect(self.handle_state)
        self.errorOccurred.connect(self.handle_error)

        self.timer = None
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
        self.timer = time.time()
        if self.logfile:
            try:
                self.logfileIO = open(self.logfile, 'w')
            except:
                pass

    def handle_finished(self):
        end_time = time.time()
        self.on_finished.emit(end_time - self.timer)
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
                

                