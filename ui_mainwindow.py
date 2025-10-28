# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(798, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 50, 711, 481))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_Connect = QPushButton(self.verticalLayoutWidget)
        self.pushButton_Connect.setObjectName(u"pushButton_Connect")

        self.verticalLayout.addWidget(self.pushButton_Connect)

        self.label_IL1 = QLabel(self.verticalLayoutWidget)
        self.label_IL1.setObjectName(u"label_IL1")

        self.verticalLayout.addWidget(self.label_IL1)

        self.label_IL2 = QLabel(self.verticalLayoutWidget)
        self.label_IL2.setObjectName(u"label_IL2")

        self.verticalLayout.addWidget(self.label_IL2)

        self.textEdit_Log = QTextEdit(self.verticalLayoutWidget)
        self.textEdit_Log.setObjectName(u"textEdit_Log")

        self.verticalLayout.addWidget(self.textEdit_Log)

        self.label_IL3 = QLabel(self.verticalLayoutWidget)
        self.label_IL3.setObjectName(u"label_IL3")

        self.verticalLayout.addWidget(self.label_IL3)

        self.label_Status = QLabel(self.verticalLayoutWidget)
        self.label_Status.setObjectName(u"label_Status")

        self.verticalLayout.addWidget(self.label_Status)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 798, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_Connect.setText(QCoreApplication.translate("MainWindow", u"pushButton_Connect", None))
        self.label_IL1.setText(QCoreApplication.translate("MainWindow", u"label_IL1", None))
        self.label_IL2.setText(QCoreApplication.translate("MainWindow", u"label_IL2", None))
        self.label_IL3.setText(QCoreApplication.translate("MainWindow", u"label_IL3", None))
        self.label_Status.setText(QCoreApplication.translate("MainWindow", u"label_Status", None))
    # retranslateUi

