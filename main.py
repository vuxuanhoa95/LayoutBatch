import os
import re
import sys

from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QCursor, QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMenu, QListWidgetItem)

from utils import jobmodel


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


RESOURCE = resource_path('Resources') + '\\'
MAIN_UI = resource_path('utils') + '\\main.ui'

MAYA_LOCATION = r'C:\Program Files\Autodesk\Maya2018'
MAYA_BATCH = os.path.join(MAYA_LOCATION, 'bin', 'mayabatch.exe')
MAYA_RENDER = os.path.join(MAYA_LOCATION, 'bin', 'render.exe')
MAYA_PY = os.path.join(MAYA_LOCATION, 'bin', 'mayapy.exe')

TEMP = r'D:\temp'
MAYA_SCRIPT = os.path.join(TEMP, 'test.py').replace("\\", "/")
# COMMAND = "python(\\\"execfile(\\'{}\\')\\\")".format(
#         MAYA_SCRIPT.replace("\\", "/")
#     )
COMMAND = f'python("exec(open(\'{MAYA_SCRIPT}\').read())")'
LOG_FILE = os.path.join(TEMP, 'test.log')

PRESET_TASKS = {
    'Help': {
        'args': ['help'],
        'kwargs': {},
    },
    'Archive': {
        'args': ['noAutoloadPlugins'],
        'kwargs': {'archive': '%FILE%', 'log': LOG_FILE},
    },
    'Test': {
        'args': ['noAutoloadPlugins'],
        'kwargs': {'command': COMMAND, 'log': LOG_FILE},
    },
    'Playblast': {
        'args': [],
        'kwargs': {},
    },
}


PATTERN = re.compile(r'((\w:)|(\.))((/(?!/)(?!/)|\\{2})[^\n?"|></\\:*]+)+')


def gen_args(preset: dict = None, *args, **kwargs):

    arguments = []
    if preset:
        args = list(args)
        args.extend(preset.get('args', []))

        kwargs.update(preset.get('kwargs', {}))

    for k, v in kwargs.items():
        arguments.extend([f'-{k}', v])

    for a in args:
        if not a.startswith('-'):
            a = f'-{a}'
        arguments.append(a)

    return arguments


class TaskItem(QListWidgetItem):

    def __init__(self, name, preset=None):
        super().__init__(name)
        self.preset = preset
        self.log = None
        self.arguments = []

    def help(self):
        self.preset = {
            'args': ['help'],
        }
        self.arguments = [MAYA_BATCH, '-help']

    def archive(self, path):
        self.log = f'{path}.log'
        self.preset = {
            'args': ['noAutoloadPlugins'],
            'kwargs': {'archive': path, 'log': self.log},
        }
        self.arguments = [MAYA_BATCH, '-archive', path, '-log', self.log, 'noAutoloadPlugins']

    def render(self, path):
        self.log = f'{path}.log'
        self.arguments = [MAYA_BATCH, '-r', 'hw2', '-s', '1.0', '-e', '10.0', '-of', '.png', '-keepMel', '-log', self.log, path]


class FileItem(QListWidgetItem):

    def __init__(self, name, path):
        super().__init__(name)
        self.path = path.replace('\\', '/')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui = QUiLoader()
        self.ui = ui.load(MAIN_UI)

        self.job = jobmodel.JobManager()
        self.ui.lv_progress.setModel(self.job)
        delegate = jobmodel.ProgressBarDelegate()
        self.ui.lv_progress.setItemDelegate(delegate)

        self.connect_event()
        self.add_presets()
        self.add_file(r"\\vnnas\projects\PAC\11_ProjectSpace\03_Workflow\Shots\CIN.DLC1.M1.PRE-Shot0050\Scenefiles\anm\Animation\shot_CIN.DLC1.M1.PRE-Shot0050_anm_Animation_v0035_Anim_vdo_.mb")
        self.ui.show()

    def connect_event(self):
        self.ui.pte_log.setReadOnly(True)
        self.job.status.connect(self.ui.statusbar.showMessage)
        self.job.result.connect(self.display_result)
        self.ui.b_execute.pressed.connect(self.run_command)
        self.ui.b_clear.pressed.connect(self.job.cleanup)
        self.ui.b_test.pressed.connect(self.test)

        self.ui.lw_files.installEventFilter(self)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        event_type = event.type()
        if event_type == QEvent.ContextMenu:
            menu = QMenu()
            if source == self.ui.lw_files:
                a = QAction('Add files', self)
                a.triggered.connect(lambda: self.load_file())
                menu.addAction(a)
                menu.addSeparator()
                item = source.itemAt(event.pos())
                if item:
                    a = QAction('Remove files', self)
                    a.triggered.connect(lambda: self.load_file())
                    menu.addAction(a)

            menu.exec(QCursor.pos())

        return super().eventFilter(source, event)

    def test(self):
        self.job.execute_detach(['python', 'test.py'])

    # tag::startJob[]
    def run_command(self):
        for i in range(self.ui.lw_files.count()):
            f = self.ui.lw_files.item(i)
            t = self.ui.lw_tasks.currentItem()
            task = t.text()

            if task == 'Archive':
                t.archive(f.path)
                args = t.arguments
            elif task == 'Help':
                t.help()
                args = t.arguments
            elif task == 'Playblast':
                t.render(f.path)
                args = t.arguments
            else:
                kwargs = t.preset.get('kwargs', {})
                kwargs.update({'file': f.path})
                args = gen_args(t.preset)
                args.insert(0, MAYA_BATCH)

            # args.insert(0, MAYA_BATCH)
            print(args)
            self.job.execute_detach(args)

    # end::startJob[]
    def display_result(self, job_id, data):
        if data:
            self.ui.pte_log.appendPlainText("WORKER %s: %s" % (job_id, data))

    def display_log(self, data):
        if data:
            self.ui.pte_log.appendPlainText(data)

    def load_file(self):
        files, _ = QFileDialog.getOpenFileUrls(self, filter="Maya Files (*.ma *.mb);; All files (*)")
        for f in files:
            f = f.toLocalFile()
            self.add_file(f)

    def add_file(self, path):
        if os.path.exists(path):
            lw = self.ui.lw_files
            basename = os.path.basename(path)
            # name, ext = os.path.splitext(basename)
            item = FileItem(basename, path)
            lw.addItem(item)
            print('Added', basename)

    def add_presets(self, presets: dict = None):
        if not presets:
            presets = PRESET_TASKS

        lw = self.ui.lw_tasks
        for k, v in presets.items():
            item = TaskItem(k, v)
            lw.addItem(item)
            print(item.preset)
            # print(item.data(Qt.UserRole))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec())
