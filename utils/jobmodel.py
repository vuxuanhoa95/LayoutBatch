import os
import subprocess
import tempfile
import threading
import uuid
from io import TextIOWrapper
import sys

from PySide6.QtCore import QAbstractListModel, Signal, Slot, QProcess, QRect, Qt, QObject, QTimer, QRunnable, QThreadPool
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QStyledItemDelegate


from utils import temp_script as ts, maya_launcher as ml


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

DEFAULT_STATE = {"progress": 0, "log": '', 'logfile': None, 
                 'script': 'task', 
                 'file': 'empty'}


MAYAPY = {k: str(ml.mayapy(k)) for k in ml.installed_maya_versions()}


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
                    # sys.stdout.write(line)
                    on_log(line)  # log callback

                else:
                    break

        while proc.poll() is None:
            check_io()

        proc.wait()
        on_exit()  # exit callback

    thread = threading.Thread(target=run_in_thread, args=args)
    return thread


def simple_parser(line):
    if not line:
        return

    return line.startswith('PROGRESS:')


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    log = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, args, parser=None):
        super().__init__()

        self.args = args
        self.parser = parser
        self.signals = WorkerSignals()
        self.stdout = subprocess.STDOUT

    @Slot()
    def run(self):
        # proc = subprocess.Popen(self.args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        #                         creationflags=subprocess.CREATE_NEW_CONSOLE)

        proc = subprocess.Popen(self.args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        def check_io():
            progress = 0
            while True:
                line = proc.stdout.readline().decode()
                if self.parser is None:
                    progress += 1
                else:
                    if self.parser(line):
                        progress += 1
                if progress >= 100:
                    progress = 1
                self.signals.progress.emit(progress)  # progress callback

                if line:
                    self.signals.log.emit(line)  # log callback
                else:
                    break

        while proc.poll() is None:
            check_io()

        proc.wait()
        self.signals.finished.emit()  # exit callback


class JobManager(QAbstractListModel):
    """
    Manager to handle active jobs and stdout, stderr
    and progress parsers.
    Also functions as a Qt data model for a view
    displaying progress for each process.
    """

    _jobs = {}
    _state = {}
    _tempdir = tempfile.gettempdir()
    _modulepath = None
    _executor = None
    _maxinstance = 2

    status = Signal(str)
    result = Signal(str, object)
    progress = Signal(str, int)
    finished = Signal(object)

    def __init__(self):
        super().__init__()

        self.status_timer = QTimer()
        self.status_timer.setInterval(2000)
        self.status_timer.timeout.connect(self.notify_status)
        self.status_timer.start()

        self.threadpool = QThreadPool()
        self.set_max_instance(self._maxinstance)

        self.set_mayapy_version(ml.latest_maya_version())

    def set_max_instance(self, n: int):
        self._maxinstance = n
        self.threadpool.setMaxThreadCount(self._maxinstance)
        print('Set max thread', n)

    def notify_status(self):
        n_jobs = len(self._jobs)
        self.status.emit(f"{n_jobs} jobs")

    def execute_detach2(self, arguments, logfile=None, job_id=None):
        """
        Execute a command by starting a new process.
        """

        if not job_id:
            job_id = uuid.uuid4().hex

        # Pass the function to execute
        worker = Worker(arguments) # Any other args, kwargs are passed to the run function
        worker.signals.log.connect(lambda x: self.handle_log(job_id, x))
        worker.signals.progress.connect(lambda x: self.handle_progress(job_id, x))
        worker.signals.finished.connect(lambda: self.handle_finish(job_id))

        # Set default status to waiting, 0 progress.
        self._state[job_id] = DEFAULT_STATE.copy()
        if logfile:
            self._state[job_id]['logfile'] = open(logfile, 'w')
        
        self._jobs[job_id] = worker

        print("Starting process", job_id)
        self.threadpool.start(worker)

        self.layoutChanged.emit()

    def set_mayapy_version(self, version):
        self._executor = MAYAPY[version].replace('\\', '/')
        print('Set executor', self._executor)
    
    def execute_mayapy_script(self, script_path, maya_file, logfile=True):
        job_id = uuid.uuid4().hex
        
        basename = os.path.basename(script_path)
        temp_script = os.path.join(self._tempdir, f'batch.{job_id}.{basename}').replace('\\', '/')
        if logfile:
            logfile = f'{temp_script}.log'
        with open(script_path, mode='rt') as f:
            data = f.read()
        data = ts.convert_script_data(data, self._executor, temp_script, maya_file, self._modulepath)
        with open(temp_script, mode='wt') as f:
            f.write(data)

        arguments = ts.parse_script_to_arguments(temp_script)

        # Pass the function to execute
        worker = Worker(arguments) # Any other args, kwargs are passed to the run function
        worker.signals.log.connect(lambda x: self.handle_log(job_id, x))
        worker.signals.progress.connect(lambda x: self.handle_progress(job_id, x))
        worker.signals.finished.connect(lambda: self.handle_finish(job_id, out_log=logfile))

        # Set default status to waiting, 0 progress.
        self._state[job_id] = DEFAULT_STATE.copy()
        self._state[job_id]['script'] = basename
        self._state[job_id]['file'] = os.path.basename(maya_file)

        if logfile:
            self._state[job_id]['logfile'] = open(logfile, 'w')
        
        self._jobs[job_id] = worker

        print("Starting process", job_id, worker)
        self.threadpool.start(worker)

        self.layoutChanged.emit()

    def handle_progress(self, job_id, progress):
        self._state[job_id]["progress"] = progress
        self.layoutChanged.emit()

    def handle_log(self, job_id, log):
        if log.startswith('PROGRESS:'):
            self._state[job_id]["log"] = log.partition(':')[2]

        if isinstance(self._state[job_id]['logfile'], TextIOWrapper):
            self._state[job_id]['logfile'].write(log)
        self.result.emit(job_id, log)
        # self.layoutChanged.emit()

    def handle_finish(self, job_id, out_log=None):
        """
        Task/worker complete. Remove it from the active workers
        dictionary. We leave it in worker_state, as this is used to
        to display past/complete workers too.
        """
        print('Finished process', job_id)
        self._state[job_id]["progress"] = 100
        if isinstance(self._state[job_id]['logfile'], TextIOWrapper):
            self._state[job_id]['logfile'].close()
        
        try:
            self.threadpool.tryTake(self._jobs[job_id])
        except:
            pass
        del self._jobs[job_id]
        self.finished.emit(out_log)
        self.layoutChanged.emit()

    def cleanup(self):
        """
        Remove any complete/failed workers from worker_state.
        """
        for job_id, s in list(self._state.items()):

            if self._jobs.get(job_id):
                if self.threadpool.tryTake(self._jobs[job_id]):
                    del self._state[job_id]
                    del self._jobs[job_id]

            if self._state.get(job_id):
                if self._state[job_id]['progress'] == 100:
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
        
        if progress == 100:
            status = 'DONE'
        elif progress == 0:
            status = 'Starting...'
        else:
            status = 'Running...'
            status += data["log"]

        script = data['script']
        file = data['file']

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
        painter.drawText(option.rect, Qt.AlignLeft, f'{file} | {script} | {status}')
