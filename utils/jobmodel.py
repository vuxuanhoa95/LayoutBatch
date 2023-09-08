import os
import subprocess
import threading
import uuid
from io import TextIOWrapper
import sys

from PySide6.QtCore import QAbstractListModel, Signal, QProcess, QRect, Qt, QObject, QTimer
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QStyledItemDelegate


TEMP = r'C:\Dev\temp'
LOG_FILE = 'mayabatch.log'

STATUS_COLORS = {
    QProcess.NotRunning: "#b2df8a",
    QProcess.Starting: "#fdbf6f",
    QProcess.Running: "#33a02c",
}

STATES = {
    QProcess.NotRunning: "Not running",
    QProcess.Starting: "Starting...",
    QProcess.Running: "Running...",
}

DEFAULT_STATE = {"progress": 0, "log": '', 'logfile': None}


def call(*args):

    def run_in_thread(arguments, on_exit, on_progress, on_log):

        # proc = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        #                         creationflags=subprocess.CREATE_NEW_CONSOLE)

        proc = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        def check_io():
            progress = 0
            while True:
                progress += 1
                if progress >= 100:
                    progress = 1
                on_progress(progress)  # progress callback
                
                line = proc.stdout.readline().decode()
                if line:
                    sys.stdout.write(line)
                    on_log(line)  # log callback

                else:
                    break

        while proc.poll() is None:
            check_io()

        proc.wait()
        on_exit()  # exit callback

    thread = threading.Thread(target=run_in_thread, args=args)
    return thread


class JobManager(QAbstractListModel):
    """
    Manager to handle active jobs and stdout, stderr
    and progress parsers.
    Also functions as a Qt data model for a view
    displaying progress for each process.
    """

    _jobs = {}
    _state = {}
    _logs = {}

    status = Signal(str)
    result = Signal(str, object)
    progress = Signal(str, int)

    def __init__(self):
        super().__init__()

        self.status_timer = QTimer()
        self.status_timer.setInterval(2000)
        self.status_timer.timeout.connect(self.notify_status)
        self.status_timer.start()

        # Internal signal, to trigger update of progress via parser.
        self.worker = None
        self.thread = None

    def notify_status(self):
        n_jobs = len(self._jobs)
        self.status.emit(f"{n_jobs} jobs")

    def execute_detach(self, arguments, logfile=None, job_id=None):
        """
        Execute a command by starting a new process.
        """
        def fwd_signal(target):
            return lambda *args: target(job_id, *args)

        if not job_id:
            job_id = uuid.uuid4().hex

        p = call(arguments, fwd_signal(self.done), fwd_signal(self.handle_progress),
                            fwd_signal(self.handle_log))

        # Set default status to waiting, 0 progress.
        self._state[job_id] = DEFAULT_STATE.copy()
        if logfile:
            self._state[job_id]['logfile'] = open(logfile, 'w')
        
        self._jobs[job_id] = p

        print("Starting process", job_id, p)
        p.start()

        self.layoutChanged.emit()

    def handle_progress(self, job_id, progress):
        self._state[job_id]["progress"] = progress
        self.layoutChanged.emit()

    def handle_log(self, job_id, log):
        self._state[job_id]["log"] = log
        if isinstance(self._state[job_id]['logfile'], TextIOWrapper):
            self._state[job_id]['logfile'].write(log)
        self.result.emit(job_id, log)
        # self.layoutChanged.emit()

    def done(self, job_id, *arg):
        """
        Task/worker complete. Remove it from the active workers
        dictionary. We leave it in worker_state, as this is used to
        to display past/complete workers too.
        """
        print('Finished process', job_id)
        self._state[job_id]["progress"] = 100
        if isinstance(self._state[job_id]['logfile'], TextIOWrapper):
            self._state[job_id]['logfile'].close()
        
        del self._jobs[job_id]
        self.layoutChanged.emit()

    def cleanup(self):
        """
        Remove any complete/failed workers from worker_state.
        """
        for job_id, s in list(self._state.items()):
            del self._state[job_id]
        self.layoutChanged.emit()

    # Model interface
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the data structure.
            job_ids = list(self._state.keys())
            job_id = job_ids[index.row()]
            return job_id, self._state[job_id]

    def rowCount(self, index):
        return len(self._state)


class ProgressBarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # data is our status dict, containing progress, id, status
        job_id, data = index.model().data(index, Qt.DisplayRole)

        progress = data["progress"]
        # log = data["log"]

        if progress == 100:
            status = 'DONE'
        elif progress == 0:
            status = 'Starting...'
        else:
            status = 'Running...'

        if progress > 0:
            color = QColor(STATUS_COLORS[QProcess.Running])

            brush = QBrush()
            brush.setColor(color)
            brush.setStyle(Qt.SolidPattern)

            width = option.rect.width() * progress / 100

            rect = QRect(
                option.rect
            )  # Copy of the rect, so we can modify.
            rect.setWidth(width)

            painter.fillRect(rect, brush)

        pen = QPen()
        pen.setColor(Qt.black)
        painter.drawText(option.rect, Qt.AlignLeft, f'{job_id} | {status}')
