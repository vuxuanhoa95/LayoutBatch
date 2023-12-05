import os
import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from main import MainWindow
# from export_fbx_ui import Ui_Form


plugin = None


def load(core, layout):
    global plugin
    if not plugin:
        plugin = LB_Maya_Export_FBX(core)
    plugin.add_ui(layout)


if __name__ == "__main__":
    print("Hello World")


class LB_Maya_Export_FBX(object):


    def __init__(self, core):
        print('Initializing...', self.__class__)
        self.core: MainWindow = core
        self.widget: QWidget = None


    def add_ui(self, layout: QLayout):

        if not self.widget:
            Form = QWidget()
            verticalLayout = QVBoxLayout(Form)
            lineEdit = QLineEdit(Form)
            verticalLayout.addWidget(lineEdit)
            self.widget = Form

        layout.addWidget(self.widget)
