import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets


from ui import BaseDialog


class InputFilePath(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget, 
                 label: str="Path", 
                 fileMode: int=0, **kwargs) -> None:


        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel(label, self)
        layout.addWidget(self.label)

        self.input = QtWidgets.QLineEdit("", self)
        layout.addWidget(self.input)

        self.button = QtWidgets.QPushButton(self)
        self.button.setText("Browse")
        self.button.clicked.connect(lambda: self.browse(**kwargs))
        layout.addWidget(self.button)

        self.fileMode = fileMode

    def browse(self):
        fileName = BaseDialog.FileDialogLite(self.fileMode)
        if fileName:
            self.input.setText(fileName)
