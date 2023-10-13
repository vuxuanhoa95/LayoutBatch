import os
import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from main import MainWindow
from export_fbx_ui import Ui_Form


def load_ui(core):
    plugin = LB_Maya_Export_FBX(core)
    plugin.add_ui()


class LB_Maya_Export_FBX(object):


    def __init__(self, core):
        self.core: MainWindow = core
        # self.add_ui()
        

    def add_ui(self):
        self.widget = Ui_Form()
        self.widget.setupUi(self.core.current_plugin_widget)
