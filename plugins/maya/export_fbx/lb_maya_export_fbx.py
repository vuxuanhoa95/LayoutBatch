import os
import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from main import MainWindow


class LB_Maya_Export_FBX(object):


    def __init__(self, core):
        self.core: MainWindow = core
        self.add_ui()
        

    def add_ui(self):
        self.core.add_task("plugin", r"D:\Github\LayoutBatch\plugins\maya\export_fbx\export_fbx_ui.py")
