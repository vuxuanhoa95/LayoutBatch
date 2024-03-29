# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QLabel,
    QLineEdit, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPlainTextEdit,
    QPushButton, QSizePolicy, QSplitter, QStackedWidget,
    QStatusBar, QTabWidget, QVBoxLayout, QWidget)

from widget import DragList

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(924, 644)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionExit_2 = QAction(MainWindow)
        self.actionExit_2.setObjectName(u"actionExit_2")
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.actionVersion = QAction(MainWindow)
        self.actionVersion.setObjectName(u"actionVersion")
        self.actionMayabatch = QAction(MainWindow)
        self.actionMayabatch.setObjectName(u"actionMayabatch")
        self.actionMayabatch.setCheckable(True)
        self.actionMayabatch.setChecked(False)
        self.actionMayabatch.setEnabled(False)
        self.actionMayapy = QAction(MainWindow)
        self.actionMayapy.setObjectName(u"actionMayapy")
        self.actionMayapy.setCheckable(True)
        self.actionMayapy.setChecked(True)
        self.actionRender = QAction(MainWindow)
        self.actionRender.setObjectName(u"actionRender")
        self.actionRender.setCheckable(True)
        self.actionRender.setEnabled(False)
        self.actionAddFiles = QAction(MainWindow)
        self.actionAddFiles.setObjectName(u"actionAddFiles")
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
        self.lw_tasks.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lw_tasks.setSelectionRectVisible(False)
        self.splitter.addWidget(self.lw_tasks)
        self.stackedWidget = QStackedWidget(self.splitter)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.default = QWidget()
        self.default.setObjectName(u"default")
        self.verticalLayout_2 = QVBoxLayout(self.default)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.label = QLabel(self.default)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.lw_files = DragList(self.default)
        self.lw_files.setObjectName(u"lw_files")
        self.lw_files.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.verticalLayout_2.addWidget(self.lw_files)

        self.lineEdit = QLineEdit(self.default)
        self.lineEdit.setObjectName(u"lineEdit")

        self.verticalLayout_2.addWidget(self.lineEdit)

        self.stackedWidget.addWidget(self.default)
        self.splitter.addWidget(self.stackedWidget)
        self.splitter_3.addWidget(self.splitter)
        self.splitter_2 = QSplitter(self.splitter_3)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.lv_progress = QListView(self.splitter_2)
        self.lv_progress.setObjectName(u"lv_progress")
        self.splitter_2.addWidget(self.lv_progress)
        self.tabWidget = QTabWidget(self.splitter_2)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_3 = QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pte_log = QPlainTextEdit(self.tab)
        self.pte_log.setObjectName(u"pte_log")

        self.verticalLayout_3.addWidget(self.pte_log)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.stackedWidget_2 = QStackedWidget(self.tab_2)
        self.stackedWidget_2.setObjectName(u"stackedWidget_2")

        self.verticalLayout_4.addWidget(self.stackedWidget_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.splitter_2.addWidget(self.tabWidget)
        self.splitter_3.addWidget(self.splitter_2)

        self.verticalLayout.addWidget(self.splitter_3)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.b_execute = QPushButton(self.centralwidget)
        self.b_execute.setObjectName(u"b_execute")

        self.gridLayout.addWidget(self.b_execute, 0, 0, 1, 1)

        self.b_clear = QPushButton(self.centralwidget)
        self.b_clear.setObjectName(u"b_clear")

        self.gridLayout.addWidget(self.b_clear, 0, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 924, 22))
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
        self.menuFile.addAction(self.actionAddFiles)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit_2)
        self.menuMaya.addAction(self.actionMayapy)
        self.menuMaya.addAction(self.actionMayabatch)
        self.menuMaya.addAction(self.actionRender)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionVersion)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Layout Previz Tasks", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionExit_2.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.actionVersion.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionMayabatch.setText(QCoreApplication.translate("MainWindow", u"Mayabatch", None))
        self.actionMayapy.setText(QCoreApplication.translate("MainWindow", u"Mayapy", None))
        self.actionRender.setText(QCoreApplication.translate("MainWindow", u"Render", None))
        self.actionAddFiles.setText(QCoreApplication.translate("MainWindow", u"Add files", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Default", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.b_execute.setText(QCoreApplication.translate("MainWindow", u"Run Tasks", None))
        self.b_clear.setText(QCoreApplication.translate("MainWindow", u"Clear All", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuMaya.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

