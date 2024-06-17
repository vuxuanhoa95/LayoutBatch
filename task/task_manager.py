import importlib
import os
import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from task.task_worker import TaskViewer


def load_module(modname, fname):
    print("loading module", modname)
    spec = importlib.util.spec_from_file_location(modname, fname)
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module

def relative_path(path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, path)


class _TaskManagerUI:
    """The ui class of mdi window."""

    def setupUi(self, widget: QWidget) -> None:
        """Set up ui."""
        main_layout = QVBoxLayout(widget)
        splitter = QSplitter()
        main_layout.addWidget(splitter)

        # plugin ui area
        self.containerPlugin = QWidget()
        splitter.addWidget(self.containerPlugin)
        v_layout = QVBoxLayout(self.containerPlugin)

        self.comboPlugin = QComboBox(self.containerPlugin)
        v_layout.addWidget(self.comboPlugin)

        self.stackPlugin = QStackedWidget(self.containerPlugin)
        v_layout.addWidget(self.stackPlugin)

        # manager ui area
        self.containerManager = QWidget()
        splitter.addWidget(self.containerManager)
        v_main_layout = QVBoxLayout(self.containerManager)

        self.mdi_area = QMdiArea()
        v_main_layout.addWidget(self.mdi_area)

        h_layout = QHBoxLayout()
        v_main_layout.addLayout(h_layout)

        self.buttonNew = QPushButton("Add new")
        self.buttonCascade = QPushButton("Cascade")
        self.buttonTiled = QPushButton("Tiled")
        self.buttonCloseFinished = QPushButton("Close Finished")
        h_layout.addWidget(self.buttonNew)
        h_layout.addWidget(self.buttonCascade)
        h_layout.addWidget(self.buttonTiled)
        h_layout.addWidget(self.buttonCloseFinished)

        self.labelQueueStatus = QLabel()
        v_main_layout.addWidget(self.labelQueueStatus)


class TaskManager(QWidget):

    MAX_INSTANCE = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._ui = _TaskManagerUI()
        self._ui.setupUi(self)

        self._ui.buttonNew.pressed.connect(lambda: self.add_to_queue())
        self._ui.buttonCascade.pressed.connect(self._ui.mdi_area.cascadeSubWindows)
        self._ui.buttonTiled.pressed.connect(self._ui.mdi_area.tileSubWindows)
        self._ui.buttonCloseFinished.pressed.connect(self.close_finished_tasks)
        self._ui.buttonNew.setDefault(True)

        self._ui.comboPlugin.currentTextChanged.connect(self.load_plugin)

        self._running: list[str] = []
        self._finished: list[str] = []

        self._plugins: dict[str, str] = {}

        self.scan_for_module(relative_path("agents"))

    
    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        running_tasks: list[TaskViewer] = []
        for t in self.tasks:
            if t.worker.state().value != 0:
                running_tasks.append(t)

        if running_tasks:
            message = "Some processes are running:\n"
            for t in running_tasks:
                message += f"{t.worker.id}: {t.worker.state()}\n"

            result = QMessageBox.question(self, "Confirm Exit...", f"{message}.\nAre you sure to close?")
            if result == QMessageBox.Yes:
                for t in self.tasks:
                    t.worker.kill()
                    t.worker.waitForFinished()
                event.accept()
        else:
            event.accept()

    @property
    def tasks(self) -> list[TaskViewer]:
        return [w for w in self._ui.mdi_area.subWindowList() if isinstance(w, TaskViewer)]
    

    def close_finished_tasks(self):
        for t in self.tasks:
            if t.worker.id in self._finished:
                t.close()


    def add_to_queue(self):
        task = TaskViewer(self._ui.containerManager)
        task.finished.connect(lambda: self.on_task_finished(task.worker.id))

        self._ui.mdi_area.addSubWindow(task)
        task.show()
        self.start_queue()
        # window.run()

    def start_queue(self):

        counter = 0
        for task in self.tasks:
            counter += 1
            task_id = task.worker.id

            if task_id in self._running or task_id in self._finished:
                counter -= 1
                continue

            if len(self._running) >= self.MAX_INSTANCE:
                continue

            if task.worker.state() == QProcess.NotRunning:
                task.run()
                self._running.append(task_id)
                counter -= 1

        print("Running", self._running)
        print("Finished", self._finished)
        self._ui.labelQueueStatus.setText(f'Pending {counter}; Running {len(self._running)}; Finished {len(self._finished)}')

    def on_task_finished(self, task_id):
        if task_id in self._running:
            self._running.remove(task_id)
        
        if task_id not in self._finished:
            self._finished.append(task_id)

        self.start_queue()

    def scan_for_module(self, directory):
        self._ui.comboPlugin.clear()

        for plugin in os.listdir(directory):
            plugin_path = os.path.join(directory, plugin, f"task_{plugin}.py")
            if not os.path.isfile(plugin_path):
                continue
            
            self._plugins[plugin] = plugin_path
            self._ui.comboPlugin.addItem(plugin)
            print(f'Added plugin {plugin}')

    def load_plugin(self, plugin):
        print("Load", self._plugins.get(plugin))

