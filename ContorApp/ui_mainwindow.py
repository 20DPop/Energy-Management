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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHeaderView, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(850, 750)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_Title = QLabel(self.centralwidget)
        self.label_Title.setObjectName(u"label_Title")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label_Title.setFont(font)
        self.label_Title.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_Title)

        self.label_Status = QLabel(self.centralwidget)
        self.label_Status.setObjectName(u"label_Status")
        self.label_Status.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_Status)

        self.pushButton_Connect = QPushButton(self.centralwidget)
        self.pushButton_Connect.setObjectName(u"pushButton_Connect")
        self.pushButton_Connect.setMinimumSize(QSize(0, 40))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.pushButton_Connect.setFont(font1)

        self.verticalLayout.addWidget(self.pushButton_Connect)

        self.groupBox_MeterList = QGroupBox(self.centralwidget)
        self.groupBox_MeterList.setObjectName(u"groupBox_MeterList")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_MeterList)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tableWidget_Meters = QTableWidget(self.groupBox_MeterList)
        if (self.tableWidget_Meters.columnCount() < 4):
            self.tableWidget_Meters.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_Meters.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_Meters.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_Meters.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_Meters.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tableWidget_Meters.setObjectName(u"tableWidget_Meters")
        self.tableWidget_Meters.setColumnCount(4)

        self.verticalLayout_2.addWidget(self.tableWidget_Meters)


        self.verticalLayout.addWidget(self.groupBox_MeterList)

        self.groupBox_Log = QGroupBox(self.centralwidget)
        self.groupBox_Log.setObjectName(u"groupBox_Log")
        self.verticalLayout_Log = QVBoxLayout(self.groupBox_Log)
        self.verticalLayout_Log.setObjectName(u"verticalLayout_Log")
        self.textEdit_Log = QTextEdit(self.groupBox_Log)
        self.textEdit_Log.setObjectName(u"textEdit_Log")
        self.textEdit_Log.setMaximumSize(QSize(16777215, 150))
        self.textEdit_Log.setReadOnly(True)

        self.verticalLayout_Log.addWidget(self.textEdit_Log)


        self.verticalLayout.addWidget(self.groupBox_Log)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Monitorizare Multi-Contor Modbus RTU", None))
        self.label_Title.setText(QCoreApplication.translate("MainWindow", u"Monitorizare Re\u021bea Contoare", None))
        self.label_Status.setText(QCoreApplication.translate("MainWindow", u"Status Re\u021bea: Deconectat", None))
        self.pushButton_Connect.setText(QCoreApplication.translate("MainWindow", u"Conectare la Magistrala Modbus", None))
        self.groupBox_MeterList.setTitle(QCoreApplication.translate("MainWindow", u"Lista Contoarelor (10 Unit\u0103\u021bi)", None))
        ___qtablewidgetitem = self.tableWidget_Meters.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"ID", None));
        ___qtablewidgetitem1 = self.tableWidget_Meters.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Stare", None));
        ___qtablewidgetitem2 = self.tableWidget_Meters.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Frecven\u021b\u0103", None));
        ___qtablewidgetitem3 = self.tableWidget_Meters.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Detalii", None));
        self.groupBox_Log.setTitle(QCoreApplication.translate("MainWindow", u"Log Comunicare", None))


