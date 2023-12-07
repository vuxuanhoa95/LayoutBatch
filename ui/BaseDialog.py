import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets


class FileDialogLite(QtWidgets.QFileDialog):
    
    '''
        0 Any file, whether it exists or not.
        1 A single existing file.
        2 The name of a directory. Both directories and files are displayed in the dialog.
        3 The name of a directory. Only directories are displayed in the dialog.
        4 The names of one or more existing files.
    '''

    def __init__(self):
        pass

    def __new__(cls, fm, **kwargs):
        fileName = None
        if fm == 0:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileUrl()
        elif fm == 1:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileUrl()
        elif fm == 2:
            fileName = QtWidgets.QFileDialog.getExistingDirectoryUrl()
        elif fm == 3:
            fileName = QtWidgets.QFileDialog.getExistingDirectoryUrl(options=QtWidgets.QFileDialog.ShowDirsOnly)
        elif fm == 4:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileUrls()

        if isinstance(fileName, QtCore.QUrl):
            return fileName.toLocalFile()
        else:
            return [f.toLocalFile() for f in fileName]

