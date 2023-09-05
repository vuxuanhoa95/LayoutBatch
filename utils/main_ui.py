# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QListView, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPlainTextEdit, QPushButton, QSizePolicy, QSplitter,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(509, 380)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionExit_2 = QAction(MainWindow)
        self.actionExit_2.setObjectName(u"actionExit_2")
        self.actionMaya2018 = QAction(MainWindow)
        self.actionMaya2018.setObjectName(u"actionMaya2018")
        self.actionMaya2018.setCheckable(True)
        self.actionMaya2020 = QAction(MainWindow)
        self.actionMaya2020.setObjectName(u"actionMaya2020")
        self.actionMaya2020.setCheckable(True)
        self.actionMaya2023 = QAction(MainWindow)
        self.actionMaya2023.setObjectName(u"actionMaya2023")
        self.actionMaya2023.setCheckable(True)
        self.actionMaya2023.setChecked(True)
        self.action2022 = QAction(MainWindow)
        self.action2022.setObjectName(u"action2022")
        self.action2022.setCheckable(True)
        self.action2022.setChecked(True)
        self.action2024 = QAction(MainWindow)
        self.action2024.setObjectName(u"action2024")
        self.action2024.setCheckable(True)
        self.action2023 = QAction(MainWindow)
        self.action2023.setObjectName(u"action2023")
        self.action2023.setCheckable(True)
        self.action2023.setChecked(False)
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.actionVersion = QAction(MainWindow)
        self.actionVersion.setObjectName(u"actionVersion")
        self.actionMayabatch = QAction(MainWindow)
        self.actionMayabatch.setObjectName(u"actionMayabatch")
        self.actionMayabatch.setCheckable(True)
        self.actionMayabatch.setChecked(True)
        self.actionMayapy = QAction(MainWindow)
        self.actionMayapy.setObjectName(u"actionMayapy")
        self.actionMayapy.setCheckable(True)
        self.actionRender = QAction(MainWindow)
        self.actionRender.setObjectName(u"actionRender")
        self.actionRender.setCheckable(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter_3 = QSplitter(self.centralwidget)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setOrientation(Qt.Vertical)
        self.splitter = QSplitter(self.splitter_3)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.lw_tasks = QListWidget(self.splitter)
        self.lw_tasks.setObjectName(u"lw_tasks")
        self.splitter.addWidget(self.lw_tasks)
        self.lw_files = QListWidget(self.splitter)
        self.lw_files.setObjectName(u"lw_files")
        self.splitter.addWidget(self.lw_files)
        self.splitter_3.addWidget(self.splitter)
        self.splitter_2 = QSplitter(self.splitter_3)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.lv_progress = QListView(self.splitter_2)
        self.lv_progress.setObjectName(u"lv_progress")
        self.splitter_2.addWidget(self.lv_progress)
        self.pte_log = QPlainTextEdit(self.splitter_2)
        self.pte_log.setObjectName(u"pte_log")
        self.pte_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pte_log.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.splitter_2.addWidget(self.pte_log)
        self.splitter_3.addWidget(self.splitter_2)

        self.verticalLayout.addWidget(self.splitter_3)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.b_clear = QPushButton(self.centralwidget)
        self.b_clear.setObjectName(u"b_clear")

        self.gridLayout.addWidget(self.b_clear, 1, 0, 1, 1)

        self.b_execute = QPushButton(self.centralwidget)
        self.b_execute.setObjectName(u"b_execute")

        self.gridLayout.addWidget(self.b_execute, 0, 0, 1, 1)

        self.b_test = QPushButton(self.centralwidget)
        self.b_test.setObjectName(u"b_test")

        self.gridLayout.addWidget(self.b_test, 0, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 509, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile.setTearOffEnabled(False)
        self.menuMaya = QMenu(self.menubar)
        self.menuMaya.setObjectName(u"menuMaya")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuMaya.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionExit_2)
        self.menuMaya.addAction(self.actionMayabatch)
        self.menuMaya.addAction(self.actionMayapy)
        self.menuMaya.addAction(self.actionRender)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionVersion)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Batch Executor", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionExit_2.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionMaya2018.setText(QCoreApplication.translate("MainWindow", u"Maya2018", None))
        self.actionMaya2020.setText(QCoreApplication.translate("MainWindow", u"Maya2020", None))
        self.actionMaya2023.setText(QCoreApplication.translate("MainWindow", u"Maya2023", None))
        self.action2022.setText(QCoreApplication.translate("MainWindow", u"2022", None))
        self.action2024.setText(QCoreApplication.translate("MainWindow", u"2024", None))
        self.action2023.setText(QCoreApplication.translate("MainWindow", u"2023", None))
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.actionVersion.setText(QCoreApplication.translate("MainWindow", u"Version", None))
        self.actionMayabatch.setText(QCoreApplication.translate("MainWindow", u"Mayabatch", None))
        self.actionMayapy.setText(QCoreApplication.translate("MainWindow", u"Mayapy", None))
        self.actionRender.setText(QCoreApplication.translate("MainWindow", u"Render", None))
        self.pte_log.setPlainText("")
        self.b_clear.setText(QCoreApplication.translate("MainWindow", u"Clear All", None))
        self.b_execute.setText(QCoreApplication.translate("MainWindow", u"Run Command", None))
        self.b_test.setText(QCoreApplication.translate("MainWindow", u"Test", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuMaya.setTitle(QCoreApplication.translate("MainWindow", u"Maya", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

