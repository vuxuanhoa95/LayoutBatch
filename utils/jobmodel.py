import logging
import os
import subprocess
import uuid

from PySide6.QtCore import QAbstractListModel, Signal, QProcess, QRect, Qt, QObject, QTimer
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QStyledItemDelegate

from utils import jobprocess

TEMP = r'D:\temp'
LOG_FILE = 'layoutBatch.log'

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

DEFAULT_STATE = {"progress": 0, "log": ''}


class Worker(QObject):
    finished = Signal()
    progress = Signal(int)
    log = Signal(str)

    def __init__(self, arguments, log_file=None):
        super().__init__()
        self.arguments = arguments
        log_file = log_file or LOG_FILE
        self.log_file = os.path.join(TEMP, log_file)

    def run(self):

        proc = subprocess.Popen(self.arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                creationflags=subprocess.CREATE_NEW_CONSOLE)

        def check_io():
            i = 0
            logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.INFO, filename=self.log_file,
                                format='%(message)s')
            while True:
                i += 1
                if i >= 100:
                    i = 1
                self.progress.emit(i)  # progress callback

                output = proc.stdout.readline().decode()
                if output:
                    logger.log(logging.INFO, output)
                    self.log.emit(output[:31])
                else:
                    break

        while proc.poll() is None:
            check_io()

        proc.wait()
        self.finished.emit()  # finished callback


class JobManager(QAbstractListModel):
    """
    Manager to handle active jobs and stdout, stderr
    and progress parsers.
    Also functions as a Qt data model for a view
    displaying progress for each process.
    """

    _jobs = {}
    _state = {}

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

    def execute_detach(self, arguments, parsers=None):
        """
        Execute a command by starting a new process.
        """
        def fwd_signal(target):
            return lambda *args: target(job_id, *args)

        job_id = uuid.uuid4().hex

        p = jobprocess.call(arguments, fwd_signal(self.done), fwd_signal(self.handle_progress),
                            fwd_signal(self.handle_log))

        # Set default status to waiting, 0 progress.
        self._state[job_id] = DEFAULT_STATE.copy()

        self._jobs[job_id] = p
        print("Starting process", job_id, p)
        p.start()

        self.layoutChanged.emit()

    def handle_progress(self, job_id, progress):
        self._state[job_id]["progress"] = progress
        self.layoutChanged.emit()

    def handle_log(self, job_id, log):
        self._state[job_id]["log"] = log
        self.layoutChanged.emit()

    def done(self, job_id, *arg):
        """
        Task/worker complete. Remove it from the active workers
        dictionary. We leave it in worker_state, as this is used to
        to display past/complete workers too.
        """
        print('Finished process', job_id)
        self._state[job_id]["progress"] = 100
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
        log = data["log"]

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
        painter.drawText(option.rect, Qt.AlignLeft, f'{job_id} | {status} | {log}')
