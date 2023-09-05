from functools import partial
import os
import re
import sys
import time
import logging

from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QCursor, QAction, QActionGroup
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMenu, QListWidgetItem)

from utils import jobmodel


file_handler = logging.FileHandler(filename='tmp.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger('LOGGER_NAME')


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


MAIN_UI = resource_path('utils') + '\\main.ui'
PRESET_PATH = resource_path('preset') + '\\'

MAYA_LOCATION = r'C:\Program Files\Autodesk\Maya2024'
MAYA_BATCH = os.path.join(MAYA_LOCATION, 'bin', 'mayabatch.exe')
MAYA_RENDER = os.path.join(MAYA_LOCATION, 'bin', 'render.exe')
MAYA_PY = os.path.join(MAYA_LOCATION, 'bin', 'mayapy.exe')

TEMP = r'C:\Dev\temp'
# MAYA_SCRIPT = os.path.join(TEMP, 'test.py').replace("\\", "/")
# # COMMAND = "python(\\\"execfile(\\'{}\\')\\\")".format(
# #         MAYA_SCRIPT.replace("\\", "/")
# #     )
# COMMAND = f'python("exec(open(\'{MAYA_SCRIPT}\').read())")'
LOG_FILE = 'test.log'

PRESET_TASKS = {
    'Help': {
        'args': ['help'],
        'kwargs': {},
    },
    'Archive': {
        'args': ['noAutoloadPlugins'],
        'kwargs': {'archive': '', 'log': LOG_FILE},
    },
    'Playblast': {
        'args': [],
        'kwargs': {},
    },
}


def is_valid_path(string: str):
    pattern = re.compile(r'((\w:)|(\.))((/(?!/)(?!/)|\\{2})[^\n?"|></\\:*]+)+')
    if string and isinstance(string, str) and pattern.match(string):
        return True
    return False


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


def gen_presets(path=PRESET_PATH):
    scripts = []
    for f in os.listdir(os.path.dirname(__file__)):
        if f == '__init__.py':
            continue
        scripts.append(f)
    return scripts


def set_log_for_file(file):
    basename = os.path.basename(file)
    return os.path.join(TEMP, f'{basename}.log')


class MayaBatch(object):

    maya_version = 2024
    maya_location = f'C:/Program Files/Autodesk/Maya{maya_version}/bin'
    maya_batch = 'mayabatch'
    maya_executor = None

    def __init__(self, *args, **kwargs):

        self.file = None
        self.script = None
        self.log = 'layoutBatch.log'

        self.args = []
        self.build_args()
        self.add_args(*args)
        self.add_kwargs(**kwargs)

    @classmethod
    def set_executor(cls, executor: str=None, version: int=None, path=None):
        if executor in ['mayabatch', 'mayapy', 'render']:
            cls.maya_batch = executor
        if version:
            cls.maya_version = version
            cls.maya_location = f'C:/Program Files/Autodesk/Maya{version}/bin'
        if path:
            if not path.endswith('.exe'):
                print('Invalid executable path!')
                return
        else:
            path = os.path.join(cls.maya_location, f'{cls.maya_batch}.exe')

        cls.maya_executor = path.replace('\\','/')
        print(f'Set executor: {cls.maya_executor}')
        # logger.info(f'Set executor: {cls.maya_executor}')
        return cls.maya_executor

    def build_args(self):
        self.set_executor()
        self.args = [self.maya_executor]
        return self.args

    def add_args(self, *args):
        for a in args:
            if not a.startswith('-'):
                a = f'-{a}'
            if a not in self.args:
                self.args.append(a)

    def add_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            k = f'-{k}'
            v = v.replace('\\', '/')
            if k == '-script':
                self.script = v
                k = '-command'
                if self.maya_version in [2022, 2023, 2024]:
                    v = f'python("exec(open(\'{v}\').read())")'
                else:
                    v = f'python("execfile(\'{v}\')")'

            if k not in self.args:
                self.args.extend([k, v])

    def remove_flag(self, flag):
        if flag in self.args:
            i = self.args.index(flag)
            self.args.pop(i)  # remove flag
            if self.args[i].startswith('-'):
                self.args.pop(i)  # remove flag variable

    def help(self):
        self.build_args()
        self.args.append('-help')

    def set_log(self):
        self.remove_flag('-log')

        log_name = 'mayaBatch'
        for a in self.args:
            if is_valid_path(a):
                print(a)
                log_name = os.path.basename(a)
                break

        self.log = os.path.join(TEMP, f'{log_name}.{time.strftime("%H%M%S")}.log')
        self.args.extend(['-log', f'{self.log}'])

    def set_file(self, file):
        self.remove_flag('-file')
        self.args.extend([f'-file', f'{file}'])
        self.set_log()

    def set_archive(self, file):
        self.remove_flag('-archive')
        self.args.extend(['-archive', f'{file}'])
        self.set_log()


class TaskItem(QListWidgetItem):

    def __init__(self, name, arguments):
        super().__init__(name)
        self.log = None

        if isinstance(arguments, dict):
            if 'args' in arguments or 'kwargs' in arguments:
                args = arguments['args']
                kwargs = arguments['kwargs']
                self.batch = MayaBatch(*args, **kwargs)
            else:
                self.batch = MayaBatch(**arguments)
        else:
            self.batch = arguments


class FileItem(QListWidgetItem):

    def __init__(self, name, path):
        super().__init__(name)
        self.name = name
        self.path = path.replace('\\', '/')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui = QUiLoader()
        self.ui = ui.load(MAIN_UI)
        self.job = jobmodel.JobManager()

        self.build_ui()
        self.connect_event()
        self.ui.show()

        self.ui.actionMayapy.setChecked(True)
        self.add_presets()
        self.add_file(r"C:\Dev\temp\Base_Rig_Latest.mb")


    def build_ui(self):

        self.ui.lv_progress.setModel(self.job)
        delegate = jobmodel.ProgressBarDelegate()
        self.ui.lv_progress.setItemDelegate(delegate)

        self.ui.menuMaya.addSeparator()

        from utils import maya_launcher as ml
        ver_group = QActionGroup(self)
        ver_group.setExclusive(True)
        maya_versions = ml.installed_maya_versions()
        for v in maya_versions:
            a = QAction(f'Maya {v}', self)
            a.setCheckable(True)
            self.ui.menuMaya.addAction(a)
            ver_group.addAction(a)
            a.setChecked(True)
            a.triggered.connect(partial(MayaBatch.set_executor, version=v))
        
        exe_group = QActionGroup(self)
        exe_group.setExclusive(True)
        exe_group.addAction(self.ui.actionMayabatch)
        self.ui.actionMayabatch.triggered.connect(partial(MayaBatch.set_executor, executor='mayabatch'))
        exe_group.addAction(self.ui.actionMayapy)
        self.ui.actionMayapy.triggered.connect(partial(MayaBatch.set_executor, executor='mayapy'))
        exe_group.addAction(self.ui.actionRender)
        self.ui.actionRender.triggered.connect(partial(MayaBatch.set_executor, executor='render'))

        self.ui.pte_log.setReadOnly(True)

    def connect_event(self):
        self.ui.actionHelp.triggered.connect(lambda: self.quick_run('help'))
        self.ui.actionVersion.triggered.connect(lambda: self.quick_run('v'))
        self.job.status.connect(self.ui.statusbar.showMessage)
        self.job.result.connect(self.display_result)
        self.ui.b_execute.pressed.connect(self.run_command)
        self.ui.b_clear.pressed.connect(self.job.cleanup)
        self.ui.b_test.pressed.connect(self.test)

        self.ui.lw_files.installEventFilter(self)
        self.ui.pte_log.customContextMenuRequested.connect(self.pte_log_context_menu)

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
                    a.triggered.connect(lambda: self.remove_file())
                    menu.addAction(a)

            menu.exec(QCursor.pos())
            del menu
        elif event_type == QEvent.MouseButtonDblClick:
            if source == self.ui.lw_files:
                self.load_file()

        return super().eventFilter(source, event)

    def pte_log_context_menu(self, event):
        source = self.ui.pte_log
        menu = source.createStandardContextMenu()
        a = QAction('Clear', self)
        a.triggered.connect(lambda: self.ui.pte_log.clear())
        menu.addAction(a)
        menu.exec(source.mapToGlobal(event))
        del menu

    def test(self):
        self.job.execute_detach(['python', 'test.py'])

    def quick_run(self, flag):
        batch = MayaBatch(flag)
        self.job.execute_detach(batch.args)

    def run_command(self):
        t = self.ui.lw_tasks.currentItem()
        task = t.text()
        batch = t.batch
        if task == 'Help':
            batch.help()
            self.job.execute_detach(batch.args)

        else:
            for i in range(self.ui.lw_files.count()):
                f = self.ui.lw_files.item(i)
                if task == 'Archive':
                    batch.set_archive(f.path)
                else:
                    batch.set_file(f.path)
                # args.insert(0, MAYA_BATCH)
                print(batch.args)
                self.job.execute_detach(batch.args)

    # end::startJob[]
    def display_result(self, job_id, data):
        if data:
            self.ui.pte_log.appendPlainText(data)

    def display_log(self, data):
        if data:
            self.ui.pte_log.appendPlainText(data)

    def load_file(self):
        files, _ = QFileDialog.getOpenFileUrls(self, filter="Maya Files (*.ma *.mb);; All files (*)")
        for f in files:
            f = f.toLocalFile()
            self.add_file(f)

    def remove_file(self):
        selected_items = self.ui.lw_files.selectedItems()
        if not selected_items: return
        for item in selected_items:
            print('Removed', item.name)
            self.ui.lw_files.takeItem(self.ui.lw_files.row(item))

    def add_file(self, path):
        if os.path.exists(path):
            lw = self.ui.lw_files
            basename = os.path.basename(path)
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
            a = item.batch

        for f in os.listdir(PRESET_PATH):
            if f == '__init__.py':
                continue
            a = MayaBatch(script=os.path.join(PRESET_PATH, f))
            item = TaskItem(f, a)
            lw.addItem(item)
            print(a.args)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
