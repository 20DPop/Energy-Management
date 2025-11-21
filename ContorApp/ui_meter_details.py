# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_meter_details.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication,
    QMetaObject, Qt)
from PySide6.QtGui import (QFont )
from PySide6.QtWidgets import ( QDateTimeEdit,  QGridLayout,
    QGroupBox,  QLabel, QPushButton, QTextEdit,
    QVBoxLayout)

class Ui_MeterDetailDialog(object):
    def setupUi(self, MeterDetailDialog):
        if not MeterDetailDialog.objectName():
            MeterDetailDialog.setObjectName(u"MeterDetailDialog")
        MeterDetailDialog.resize(650, 700)
        self.verticalLayout_main = QVBoxLayout(MeterDetailDialog)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.label_MeterID_Title = QLabel(MeterDetailDialog)
        self.label_MeterID_Title.setObjectName(u"label_MeterID_Title")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_MeterID_Title.setFont(font)
        self.label_MeterID_Title.setAlignment(Qt.AlignCenter)

        self.verticalLayout_main.addWidget(self.label_MeterID_Title)

        self.groupBox_RealTime = QGroupBox(MeterDetailDialog)
        self.groupBox_RealTime.setObjectName(u"groupBox_RealTime")
        self.gridLayout_RealTime = QGridLayout(self.groupBox_RealTime)
        self.gridLayout_RealTime.setObjectName(u"gridLayout_RealTime")
        self.label_Header_Phase = QLabel(self.groupBox_RealTime)
        self.label_Header_Phase.setObjectName(u"label_Header_Phase")
        font1 = QFont()
        self.label_Header_Phase.setFont(font1)

        self.gridLayout_RealTime.addWidget(self.label_Header_Phase, 0, 0, 1, 1)

        self.label_Header_Current = QLabel(self.groupBox_RealTime)
        self.label_Header_Current.setObjectName(u"label_Header_Current")
        self.label_Header_Current.setFont(font1)

        self.gridLayout_RealTime.addWidget(self.label_Header_Current, 0, 1, 1, 1)

        self.label_Header_Voltage = QLabel(self.groupBox_RealTime)
        self.label_Header_Voltage.setObjectName(u"label_Header_Voltage")
        self.label_Header_Voltage.setFont(font1)

        self.gridLayout_RealTime.addWidget(self.label_Header_Voltage, 0, 2, 1, 1)

        self.label_Header_Power = QLabel(self.groupBox_RealTime)
        self.label_Header_Power.setObjectName(u"label_Header_Power")
        self.label_Header_Power.setFont(font1)

        self.gridLayout_RealTime.addWidget(self.label_Header_Power, 0, 3, 1, 1)

        self.label_Header_Reactive = QLabel(self.groupBox_RealTime)
        self.label_Header_Reactive.setObjectName(u"label_Header_Reactive")
        self.label_Header_Reactive.setFont(font1)

        self.gridLayout_RealTime.addWidget(self.label_Header_Reactive, 0, 4, 1, 1)

        self.label_Detail_L1_Text = QLabel(self.groupBox_RealTime)
        self.label_Detail_L1_Text.setObjectName(u"label_Detail_L1_Text")

        self.gridLayout_RealTime.addWidget(self.label_Detail_L1_Text, 1, 0, 1, 1)

        self.label_Detail_IL1 = QLabel(self.groupBox_RealTime)
        self.label_Detail_IL1.setObjectName(u"label_Detail_IL1")

        self.gridLayout_RealTime.addWidget(self.label_Detail_IL1, 1, 1, 1, 1)

        self.label_Detail_UL1 = QLabel(self.groupBox_RealTime)
        self.label_Detail_UL1.setObjectName(u"label_Detail_UL1")

        self.gridLayout_RealTime.addWidget(self.label_Detail_UL1, 1, 2, 1, 1)

        self.label_Detail_PL1 = QLabel(self.groupBox_RealTime)
        self.label_Detail_PL1.setObjectName(u"label_Detail_PL1")

        self.gridLayout_RealTime.addWidget(self.label_Detail_PL1, 1, 3, 1, 1)

        self.label_Detail_QL1 = QLabel(self.groupBox_RealTime)
        self.label_Detail_QL1.setObjectName(u"label_Detail_QL1")

        self.gridLayout_RealTime.addWidget(self.label_Detail_QL1, 1, 4, 1, 1)

        self.label_Detail_L2_Text = QLabel(self.groupBox_RealTime)
        self.label_Detail_L2_Text.setObjectName(u"label_Detail_L2_Text")

        self.gridLayout_RealTime.addWidget(self.label_Detail_L2_Text, 2, 0, 1, 1)

        self.label_Detail_IL2 = QLabel(self.groupBox_RealTime)
        self.label_Detail_IL2.setObjectName(u"label_Detail_IL2")

        self.gridLayout_RealTime.addWidget(self.label_Detail_IL2, 2, 1, 1, 1)

        self.label_Detail_UL2 = QLabel(self.groupBox_RealTime)
        self.label_Detail_UL2.setObjectName(u"label_Detail_UL2")

        self.gridLayout_RealTime.addWidget(self.label_Detail_UL2, 2, 2, 1, 1)

        self.label_Detail_PL2 = QLabel(self.groupBox_RealTime)
        self.label_Detail_PL2.setObjectName(u"label_Detail_PL2")

        self.gridLayout_RealTime.addWidget(self.label_Detail_PL2, 2, 3, 1, 1)

        self.label_Detail_QL2 = QLabel(self.groupBox_RealTime)
        self.label_Detail_QL2.setObjectName(u"label_Detail_QL2")

        self.gridLayout_RealTime.addWidget(self.label_Detail_QL2, 2, 4, 1, 1)

        self.label_Detail_L3_Text = QLabel(self.groupBox_RealTime)
        self.label_Detail_L3_Text.setObjectName(u"label_Detail_L3_Text")

        self.gridLayout_RealTime.addWidget(self.label_Detail_L3_Text, 3, 0, 1, 1)

        self.label_Detail_IL3 = QLabel(self.groupBox_RealTime)
        self.label_Detail_IL3.setObjectName(u"label_Detail_IL3")

        self.gridLayout_RealTime.addWidget(self.label_Detail_IL3, 3, 1, 1, 1)

        self.label_Detail_UL3 = QLabel(self.groupBox_RealTime)
        self.label_Detail_UL3.setObjectName(u"label_Detail_UL3")

        self.gridLayout_RealTime.addWidget(self.label_Detail_UL3, 3, 2, 1, 1)

        self.label_Detail_PL3 = QLabel(self.groupBox_RealTime)
        self.label_Detail_PL3.setObjectName(u"label_Detail_PL3")

        self.gridLayout_RealTime.addWidget(self.label_Detail_PL3, 3, 3, 1, 1)

        self.label_Detail_QL3 = QLabel(self.groupBox_RealTime)
        self.label_Detail_QL3.setObjectName(u"label_Detail_QL3")

        self.gridLayout_RealTime.addWidget(self.label_Detail_QL3, 3, 4, 1, 1)


        self.verticalLayout_main.addWidget(self.groupBox_RealTime)

        self.groupBox_Totals = QGroupBox(MeterDetailDialog)
        self.groupBox_Totals.setObjectName(u"groupBox_Totals")
        self.gridLayout_Totals = QGridLayout(self.groupBox_Totals)
        self.gridLayout_Totals.setObjectName(u"gridLayout_Totals")
        self.label_TotalP_Text = QLabel(self.groupBox_Totals)
        self.label_TotalP_Text.setObjectName(u"label_TotalP_Text")

        self.gridLayout_Totals.addWidget(self.label_TotalP_Text, 0, 0, 1, 1)

        self.label_Detail_P_Total = QLabel(self.groupBox_Totals)
        self.label_Detail_P_Total.setObjectName(u"label_Detail_P_Total")

        self.gridLayout_Totals.addWidget(self.label_Detail_P_Total, 0, 1, 1, 1)

        self.label_TotalQ_Text = QLabel(self.groupBox_Totals)
        self.label_TotalQ_Text.setObjectName(u"label_TotalQ_Text")

        self.gridLayout_Totals.addWidget(self.label_TotalQ_Text, 1, 0, 1, 1)

        self.label_Detail_Q_Total = QLabel(self.groupBox_Totals)
        self.label_Detail_Q_Total.setObjectName(u"label_Detail_Q_Total")

        self.gridLayout_Totals.addWidget(self.label_Detail_Q_Total, 1, 1, 1, 1)

        self.label_Freq_Text = QLabel(self.groupBox_Totals)
        self.label_Freq_Text.setObjectName(u"label_Freq_Text")

        self.gridLayout_Totals.addWidget(self.label_Freq_Text, 0, 2, 1, 1)

        self.label_Detail_Frequency = QLabel(self.groupBox_Totals)
        self.label_Detail_Frequency.setObjectName(u"label_Detail_Frequency")

        self.gridLayout_Totals.addWidget(self.label_Detail_Frequency, 0, 3, 1, 1)

        self.label_PF_Text = QLabel(self.groupBox_Totals)
        self.label_PF_Text.setObjectName(u"label_PF_Text")

        self.gridLayout_Totals.addWidget(self.label_PF_Text, 1, 2, 1, 1)

        self.label_Detail_PF_Total = QLabel(self.groupBox_Totals)
        self.label_Detail_PF_Total.setObjectName(u"label_Detail_PF_Total")

        self.gridLayout_Totals.addWidget(self.label_Detail_PF_Total, 1, 3, 1, 1)


        self.verticalLayout_main.addWidget(self.groupBox_Totals)

        self.groupBox_History = QGroupBox(MeterDetailDialog)
        self.groupBox_History.setObjectName(u"groupBox_History")
        self.gridLayout_History = QGridLayout(self.groupBox_History)
        self.gridLayout_History.setObjectName(u"gridLayout_History")
        self.label_Start = QLabel(self.groupBox_History)
        self.label_Start.setObjectName(u"label_Start")

        self.gridLayout_History.addWidget(self.label_Start, 0, 0, 1, 1)

        self.dateTimeEdit_Start = QDateTimeEdit(self.groupBox_History)
        self.dateTimeEdit_Start.setObjectName(u"dateTimeEdit_Start")

        self.gridLayout_History.addWidget(self.dateTimeEdit_Start, 0, 1, 1, 1)

        self.label_End = QLabel(self.groupBox_History)
        self.label_End.setObjectName(u"label_End")

        self.gridLayout_History.addWidget(self.label_End, 1, 0, 1, 1)

        self.dateTimeEdit_End = QDateTimeEdit(self.groupBox_History)
        self.dateTimeEdit_End.setObjectName(u"dateTimeEdit_End")

        self.gridLayout_History.addWidget(self.dateTimeEdit_End, 1, 1, 1, 1)

        self.pushButton_GenerateReport = QPushButton(self.groupBox_History)
        self.pushButton_GenerateReport.setObjectName(u"pushButton_GenerateReport")

        self.gridLayout_History.addWidget(self.pushButton_GenerateReport, 2, 0, 1, 2)


        self.verticalLayout_main.addWidget(self.groupBox_History)

        self.textEdit_HistoryOutput = QTextEdit(MeterDetailDialog)
        self.textEdit_HistoryOutput.setObjectName(u"textEdit_HistoryOutput")
        self.textEdit_HistoryOutput.setReadOnly(True)

        self.verticalLayout_main.addWidget(self.textEdit_HistoryOutput)


        self.retranslateUi(MeterDetailDialog)

        QMetaObject.connectSlotsByName(MeterDetailDialog)
    # setupUi

    def retranslateUi(self, MeterDetailDialog):
        MeterDetailDialog.setWindowTitle(QCoreApplication.translate("MeterDetailDialog", u"Detalii Contor - ID [Dynamic]", None))
        self.label_MeterID_Title.setText(QCoreApplication.translate("MeterDetailDialog", u"Contor Detalii (Slave ID: --)", None))
        self.groupBox_RealTime.setTitle(QCoreApplication.translate("MeterDetailDialog", u"Date Instantanee", None))
        self.label_Header_Phase.setText(QCoreApplication.translate("MeterDetailDialog", u"Faz\u0103", None))
        self.label_Header_Current.setText(QCoreApplication.translate("MeterDetailDialog", u"Curent (I) [A]", None))
        self.label_Header_Voltage.setText(QCoreApplication.translate("MeterDetailDialog", u"Tensiune (U) [V]", None))
        self.label_Header_Power.setText(QCoreApplication.translate("MeterDetailDialog", u"Putere Activ\u0103 (P) [kW]", None))
        self.label_Header_Reactive.setText(QCoreApplication.translate("MeterDetailDialog", u"Putere Reactiv\u0103 (Q) [kVAR]", None))
        self.label_Detail_L1_Text.setText(QCoreApplication.translate("MeterDetailDialog", u"L1", None))
        self.label_Detail_IL1.setText(QCoreApplication.translate("MeterDetailDialog", u"--- A", None))
        self.label_Detail_UL1.setText(QCoreApplication.translate("MeterDetailDialog", u"--- V", None))
        self.label_Detail_PL1.setText(QCoreApplication.translate("MeterDetailDialog", u"--- kW", None))
        self.label_Detail_QL1.setText(QCoreApplication.translate("MeterDetailDialog", u"--- kVAR", None))
        self.label_Detail_L2_Text.setText(QCoreApplication.translate("MeterDetailDialog", u"L2", None))
        self.label_Detail_IL2.setText(QCoreApplication.translate("MeterDetailDialog", u"--- A", None))
        self.label_Detail_UL2.setText(QCoreApplication.translate("MeterDetailDialog", u"--- V", None))
        self.label_Detail_PL2.setText(QCoreApplication.translate("MeterDetailDialog", u"--- kW", None))
        self.label_Detail_QL2.setText(QCoreApplication.translate("MeterDetailDialog", u"--- kVAR", None))
        self.label_Detail_L3_Text.setText(QCoreApplication.translate("MeterDetailDialog", u"L3", None))
        self.label_Detail_IL3.setText(QCoreApplication.translate("MeterDetailDialog", u"--- A", None))
        self.label_Detail_UL3.setText(QCoreApplication.translate("MeterDetailDialog", u"--- V", None))
        self.label_Detail_PL3.setText(QCoreApplication.translate("MeterDetailDialog", u"--- kW", None))
        self.label_Detail_QL3.setText(QCoreApplication.translate("MeterDetailDialog", u"--- kVAR", None))
        self.groupBox_Totals.setTitle(QCoreApplication.translate("MeterDetailDialog", u"Totaluri \u0219i Parametri Sistem", None))
        self.label_TotalP_Text.setText(QCoreApplication.translate("MeterDetailDialog", u"Putere Activ\u0103 Total\u0103 (\u03a3P):", None))
        self.label_Detail_P_Total.setText(QCoreApplication.translate("MeterDetailDialog", u"--- kW", None))
        self.label_TotalQ_Text.setText(QCoreApplication.translate("MeterDetailDialog", u"Putere Reactiv\u0103 Total\u0103 (\u03a3Q):", None))
        self.label_Detail_Q_Total.setText(QCoreApplication.translate("MeterDetailDialog", u"--- kVAR", None))
        self.label_Freq_Text.setText(QCoreApplication.translate("MeterDetailDialog", u"Frecven\u021b\u0103:", None))
        self.label_Detail_Frequency.setText(QCoreApplication.translate("MeterDetailDialog", u"--- Hz", None))
        self.label_PF_Text.setText(QCoreApplication.translate("MeterDetailDialog", u"Factor Putere Total (PF):", None))
        self.label_Detail_PF_Total.setText(QCoreApplication.translate("MeterDetailDialog", u"---", None))
        self.groupBox_History.setTitle(QCoreApplication.translate("MeterDetailDialog", u"Vizualizare Istoric\u0103 (Logare)", None))
        self.label_Start.setText(QCoreApplication.translate("MeterDetailDialog", u"Data Start:", None))
        self.label_End.setText(QCoreApplication.translate("MeterDetailDialog", u"Data Sf\u00e2r\u0219it:", None))
        self.pushButton_GenerateReport.setText(QCoreApplication.translate("MeterDetailDialog", u"Genereaz\u0103 Raport / Afi\u0219eaz\u0103 Grafic", None))
        self.textEdit_HistoryOutput.setPlaceholderText(QCoreApplication.translate("MeterDetailDialog", u"Datele istorice vor fi afi\u0219ate aici...", None))


