from functools import partial
import importlib
import os
import re
import sys
import logging

from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QCursor, QAction, QActionGroup, QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMenu, QListWidgetItem, QMessageBox, QLayout, QWidget

from utils import jobmodel
from main_ui import Ui_MainWindow


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


file_handler = logging.FileHandler(filename=resource_path('tmp.log'))
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger('LOGGER_NAME')


# MAYA_SCRIPT = os.path.join(TEMP, 'test.py').replace("\\", "/")
# # COMMAND = "python(\\\"execfile(\\'{}\\')\\\")".format(
# #         MAYA_SCRIPT.replace("\\", "/")
# #     )
# COMMAND = f'python("exec(open(\'{MAYA_SCRIPT}\').read())")'


def is_valid_path(string: str):
    pattern = re.compile(r'((\w:)|(\.))((/(?!/)(?!/)|\\{2})[^\n?"|></\\:*]+)+')
    if string and isinstance(string, str) and pattern.match(string):
        return True
    return False


def deleteItemsOfLayout(layout: QLayout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                deleteItemsOfLayout(item.layout())

def load_module(modname, fname):
    print("loading module", modname)
    spec = importlib.util.spec_from_file_location(modname, fname)
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module


class TaskItem(QListWidgetItem):

    def __init__(self, name, path):
        super().__init__(name)
        self.name = name
        self.path = path.replace('\\', '/')
        self.plugin = None


class FileItem(QListWidgetItem):

    def __init__(self, name, path):
        super().__init__(name)
        self.name = name
        self.path = path.replace('\\', '/')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # ui = QUiLoader()
        # self.ui = ui.load(resource_path("main.ui"))
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.job = jobmodel.JobManager()
        self.job._modulepath = resource_path("module/maya_kit.py")

        self.build_ui()
        self.connect_event()

        self.ui.actionMayapy.setChecked(True)
        self.add_presets()
        self.add_plugins()
        self.add_file(r"D:\Github\MayaExportFBX\FBX_AnimSample\CH_Frogar_A_Rig_Latest.mb")
        # self.add_file(r"D:\temp\test\Base_Rig_Latest_1.mb")
        # self.add_file(r"D:\temp\test\Base_Rig_Latest_2.mb")
        # self.add_file(r"D:\temp\test\Base_Rig_Latest_3.mb")
        # self.add_file(r"D:\temp\test\Base_Rig_Latest_4.mb")

        self.plugins = {}
        self.current_plugin = None


    def build_ui(self):

        self.ui.lv_progress.setModel(self.job)
        self.ui.lv_progress.setItemDelegate(jobmodel.ProgressBarDelegate())

        self.ui.menuMaya.addSeparator()

        ver_group = QActionGroup(self)
        ver_group.setExclusive(True)
        maya_versions = jobmodel.MAYAPY.keys()
        for v in maya_versions:
            a = QAction(f'Maya {v}', self)
            a.setCheckable(True)
            self.ui.menuMaya.addAction(a)
            ver_group.addAction(a)
            a.triggered.connect(partial(self.job.set_mayapy_version, version=v))
            a.setChecked(True)

        self.ui.menuMaya.addSeparator()
        max_group = QActionGroup(self)
        max_group.setExclusive(True)
        for n in range(4):
            n += 1
            a = QAction(f'Max Process {n}', self)
            a.setCheckable(True)
            self.ui.menuMaya.addAction(a)
            max_group.addAction(a)
            a.triggered.connect(partial(self.job.set_max_instance, n=n))
            if n==4:
                a.setChecked(True)
        
        exe_group = QActionGroup(self)
        exe_group.setExclusive(True)
        exe_group.addAction(self.ui.actionMayabatch)
        exe_group.addAction(self.ui.actionMayapy)
        exe_group.addAction(self.ui.actionRender)

        self.ui.splitter_2.setSizes([1,0])
        self.ui.splitter.setSizes([100,300])

        self.ui.pte_log.setReadOnly(True)

    def connect_event(self):
        self.ui.actionHelp.triggered.connect(lambda: self.quick_run('help'))
        self.ui.actionVersion.triggered.connect(lambda: self.quick_run('v'))
        self.ui.actionAddFiles.triggered.connect(lambda: self.load_file())
        self.ui.actionExit_2.triggered.connect(lambda: self.close())
        self.job.status.connect(self.ui.statusbar.showMessage)
        self.job.finished.connect(self.display_logfile)
        self.ui.b_execute.pressed.connect(self.run_command)
        self.ui.b_clear.pressed.connect(self.clear_all)

        self.ui.lw_files.installEventFilter(self)
        self.ui.lw_tasks.installEventFilter(self)
        self.ui.pte_log.customContextMenuRequested.connect(self.pte_log_context_menu)
        self.ui.lw_files.on_dropped.connect(self.handle_drop)
        self.ui.lw_tasks.itemClicked.connect(self.on_task_clicked)

    def closeEvent(self, event: QCloseEvent) -> None:
        result = len(self.job._jobs)==0
        event.ignore()
        if result:
            result = QMessageBox.question(self, "Confirm Exit...", "Are you sure you want to exit?")
            if result == QMessageBox.Yes:
                event.accept()
        else:
            result = QMessageBox.warning(self, "Cannot Exit...", "Some tasks are running, please wait...")

        # return super().closeEvent(event)

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
            elif source == self.ui.lw_tasks:
                a = QAction('Refresh', self)
                a.triggered.connect(lambda: self.add_presets())
                menu.addAction(a)

            menu.exec(QCursor.pos())
            del menu

        return super().eventFilter(source, event)
    
    def handle_drop(self, links):
        for url in links:
            if os.path.exists(url):
                self.add_file(url)

    def on_task_clicked(self, item):
        if isinstance(item, TaskItem):
            print(item.name)
            self.load_plugin()

            if item.plugin:
                self.load_plugin(item.path)

    def pte_log_context_menu(self, event):
        source = self.ui.pte_log
        menu = source.createStandardContextMenu()
        a = QAction('Clear', self)
        a.triggered.connect(lambda: self.ui.pte_log.clear())
        menu.addAction(a)
        menu.exec(source.mapToGlobal(event))
        del menu

    def load_plugin(self, plugin_path=None, layout=None):
        if not layout:
            layout = self.ui.stackedWidget

        if not plugin_path:
            layout.setCurrentIndex(0)
            self.current_plugin = None
            return

        # check if plugin imported, if not, import it!
        module_name, _ = os.path.splitext(os.path.basename(plugin_path))
        if not self.plugins.get(module_name):
            plugin_dir = os.path.dirname(os.path.realpath(plugin_path))
            if plugin_dir not in sys.path:
                sys.path.append(plugin_dir)
            module_loaded = load_module(module_name, plugin_path)
            self.plugins[module_name] = module_loaded
        else:
            module_loaded = self.plugins[module_name]
        
        if hasattr(module_loaded, 'load'):
            self.current_plugin = module_loaded.load(self)

        # load plugin ui to stacked widget
        widget = None
        if isinstance(self.current_plugin, QWidget):
            widget = self.current_plugin
        elif hasattr(self.current_plugin, 'widget'):
            widget = self.current_plugin.widget

        if isinstance(widget, QWidget):
            index = layout.addWidget(widget)
            layout.setCurrentIndex(index)
            
            
    def quick_run(self, flag):
        if flag == 'help':
            QMessageBox.information(self, "Help", 
                                    "1. Right-Click to add files\n2. Select a task\n3. Hit Run Tasks")
        pass

    def clear_all(self):
        self.ui.lw_files.clear()
        self.job.cleanup()
        print(len(self.job._jobs), 'jobs running')
        return len(self.job._jobs)==0

    def run_command(self):
        t = self.ui.lw_tasks.currentItem()
        count = self.ui.lw_files.count()
        if not count:
            QMessageBox.information(self, "Information", "Please add some files")
            return

        if isinstance(t, TaskItem):
            for i in range(count):
                f = self.ui.lw_files.item(i).path
                self.job.queue_process(t.path, f)
            self.ui.lw_files.clear()
            return

        QMessageBox.information(self, "Information", "Please select a task")

    def display_result(self, job_id, data):
        if data:
            self.ui.pte_log.appendPlainText(data)

    def display_logfile(self, logfile):
        if logfile:
            self.ui.pte_log.appendPlainText(logfile)


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
            item = FileItem(os.path.basename(path), path)
            self.ui.lw_files.addItem(item)
            print('Added file', path)

    def add_task(self, path, name=None):
        if os.path.exists(path):
            if not name:
                name, _ = os.path.splitext(os.path.basename(path))
            item = TaskItem(name, path)
            self.ui.lw_tasks.addItem(item)
            print('Added task', item.name)
            return item

    def add_plugins(self):
        plugin_dir = resource_path('plugins')
        for plugin in os.listdir(plugin_dir):
            plugin_path = resource_path(f'plugins/{plugin}')
            if not os.path.isdir(plugin_path):
                continue

            print(f'Added plugin {plugin}')
            for task in os.listdir(plugin_path):
                task_path = resource_path(f'plugins/{plugin}/{task}')
                if not os.path.isdir(task_path):
                    continue
                task_file = resource_path(f'plugins/{plugin}/{task}/lb_{plugin}_{task}.py')
                if os.path.isfile(task_file):
                    task_item = self.add_task(task_file)
                    task_item.plugin = True
                

    def add_presets(self):
        self.ui.lw_tasks.clear()
        preset_path = resource_path('preset')
        for f in os.listdir(preset_path):
            if f == '__init__.py' or not f.endswith('.py'):
                continue
            self.add_task(os.path.join(preset_path, f))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
