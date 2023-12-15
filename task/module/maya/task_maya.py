import os
import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from main_window import MainWindow
from ui import BaseWidget


plugin = None


def load(core: MainWindow):
    global plugin
    if not plugin:
        plugin = _MayaUi(core)

    return plugin


def run():
    if plugin:
        plugin.run()


class _MayaUi(BaseWidget.BaseSidePanel):

    def __init__(self, core):
        self.core: MainWindow = core
        super().__init__(self.core)
        print('Initializing...', self.__class__)

        self.label.setText("Export FBX")