# -*- coding: utf-8 -*-
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDateTimeEdit, QDialog, QGridLayout,
                               QGroupBox, QLabel, QPushButton, QSizePolicy,
                               QTextEdit, QVBoxLayout, QWidget, QSpacerItem)


class Ui_MeterDetailDialog(object):
    def setupUi(self, MeterDetailDialog):
        if not MeterDetailDialog.objectName():
            MeterDetailDialog.setObjectName(u"MeterDetailDialog")
        MeterDetailDialog.resize(800, 700)  # Lățime mai mare pentru extra coloană
        self.verticalLayout_main = QVBoxLayout(MeterDetailDialog)

        # --- TITLU ---
        self.label_MeterID_Title = QLabel(MeterDetailDialog)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_MeterID_Title.setFont(font)
        self.label_MeterID_Title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalLayout_main.addWidget(self.label_MeterID_Title)

        # --- GROUP BOX: DATE INSTANTANEE ---
        self.groupBox_RealTime = QGroupBox(MeterDetailDialog)
        self.groupBox_RealTime.setTitle("Monitorizare Faze & Tensiuni")
        self.gridLayout_RealTime = QGridLayout(self.groupBox_RealTime)

        # HEADERS (4 Coloane)
        # Col 0
        self.label_Header_Phase = QLabel(self.groupBox_RealTime)
        self.label_Header_Phase.setText("Fază")
        self.label_Header_Phase.setStyleSheet("font-weight: bold; text-decoration: underline;")
        self.gridLayout_RealTime.addWidget(self.label_Header_Phase, 0, 0)

        # Col 1
        self.label_Header_Current = QLabel(self.groupBox_RealTime)
        self.label_Header_Current.setText("Curent [A]")
        self.label_Header_Current.setStyleSheet("font-weight: bold; text-decoration: underline;")
        self.gridLayout_RealTime.addWidget(self.label_Header_Current, 0, 1)

        # Col 2 (NOU)
        self.label_Header_LN = QLabel(self.groupBox_RealTime)
        self.label_Header_LN.setText("Tensiune L-N (230V)")
        self.label_Header_LN.setStyleSheet("font-weight: bold; text-decoration: underline; color: #2980b9;")
        self.gridLayout_RealTime.addWidget(self.label_Header_LN, 0, 2)

        # Col 3
        self.label_Header_LL = QLabel(self.groupBox_RealTime)
        self.label_Header_LL.setText("Tensiune L-L (400V)")
        self.label_Header_LL.setStyleSheet("font-weight: bold; text-decoration: underline; color: #8e44ad;")
        self.gridLayout_RealTime.addWidget(self.label_Header_LL, 0, 3)

        # --- ROW 1: L1 ---
        self.gridLayout_RealTime.addWidget(QLabel("L1"), 1, 0)

        self.label_Detail_IL1 = QLabel("--- A")
        self.gridLayout_RealTime.addWidget(self.label_Detail_IL1, 1, 1)

        self.label_Detail_UL1_N = QLabel("--- V")  # NOU L1-N
        self.gridLayout_RealTime.addWidget(self.label_Detail_UL1_N, 1, 2)

        self.label_Detail_UL1_L2 = QLabel("--- V")  # L1-L2
        self.gridLayout_RealTime.addWidget(self.label_Detail_UL1_L2, 1, 3)

        # --- ROW 2: L2 ---
        self.gridLayout_RealTime.addWidget(QLabel("L2"), 2, 0)

        self.label_Detail_IL2 = QLabel("--- A")
        self.gridLayout_RealTime.addWidget(self.label_Detail_IL2, 2, 1)

        self.label_Detail_UL2_N = QLabel("--- V")  # NOU L2-N
        self.gridLayout_RealTime.addWidget(self.label_Detail_UL2_N, 2, 2)

        self.label_Detail_UL2_L3 = QLabel("--- V")  # L2-L3
        self.gridLayout_RealTime.addWidget(self.label_Detail_UL2_L3, 2, 3)

        # --- ROW 3: L3 ---
        self.gridLayout_RealTime.addWidget(QLabel("L3"), 3, 0)

        self.label_Detail_IL3 = QLabel("--- A")
        self.gridLayout_RealTime.addWidget(self.label_Detail_IL3, 3, 1)

        self.label_Detail_UL3_N = QLabel("--- V")  # NOU L3-N
        self.gridLayout_RealTime.addWidget(self.label_Detail_UL3_N, 3, 2)

        self.label_Detail_UL3_L1 = QLabel("--- V")  # L3-L1
        self.gridLayout_RealTime.addWidget(self.label_Detail_UL3_L1, 3, 3)

        # --- DIFERENTE (Span 4 columns) ---
        line = QLabel();
        line.setFrameShape(QLabel.HLine);
        line.setFrameShadow(QLabel.Sunken)
        self.gridLayout_RealTime.addWidget(line, 4, 0, 1, 4)

        # Diff L1-L2
        self.label_Txt_L1L2 = QLabel("L1 - L2:")
        self.label_Txt_L1L2.setStyleSheet("color: gray;")
        self.gridLayout_RealTime.addWidget(self.label_Txt_L1L2, 5, 0, 1, 3)
        self.label_Val_L1L2 = QLabel("--- V")
        self.gridLayout_RealTime.addWidget(self.label_Val_L1L2, 5, 3)

        # Diff L2-L3
        self.label_Txt_L2L3 = QLabel("L2 - L3:")
        self.label_Txt_L2L3.setStyleSheet("color: gray;")
        self.gridLayout_RealTime.addWidget(self.label_Txt_L2L3, 6, 0, 1, 3)
        self.label_Val_L2L3 = QLabel("--- V")
        self.gridLayout_RealTime.addWidget(self.label_Val_L2L3, 6, 3)

        # Diff L3-L1
        self.label_Txt_L3L1 = QLabel("L3 - L1:")
        self.label_Txt_L3L1.setStyleSheet("color: gray;")
        self.gridLayout_RealTime.addWidget(self.label_Txt_L3L1, 7, 0, 1, 3)
        self.label_Val_L3L1 = QLabel("--- V")
        self.gridLayout_RealTime.addWidget(self.label_Val_L3L1, 7, 3)

        self.verticalLayout_main.addWidget(self.groupBox_RealTime)

        # --- TOTALURI ---
        self.groupBox_Totals = QGroupBox(MeterDetailDialog)
        self.groupBox_Totals.setTitle("Totaluri și Parametri Sistem")
        self.gridLayout_Totals = QGridLayout(self.groupBox_Totals)

        self.gridLayout_Totals.addWidget(QLabel("Putere Activă Totală (ΣP):"), 0, 0)
        self.label_Detail_P_Total = QLabel("--- kW")
        self.gridLayout_Totals.addWidget(self.label_Detail_P_Total, 0, 1)

        self.gridLayout_Totals.addWidget(QLabel("Frecvență:"), 0, 2)
        self.label_Detail_Frequency = QLabel("--- Hz")
        self.gridLayout_Totals.addWidget(self.label_Detail_Frequency, 0, 3)

        self.gridLayout_Totals.addWidget(QLabel("Factor Putere (PF):"), 1, 2)
        self.label_Detail_PF_Total = QLabel("---")
        self.gridLayout_Totals.addWidget(self.label_Detail_PF_Total, 1, 3)

        self.verticalLayout_main.addWidget(self.groupBox_Totals)

        # --- ISTORIC ---
        self.groupBox_History = QGroupBox(MeterDetailDialog)
        self.groupBox_History.setTitle("Istoric & Grafic")
        self.verticalLayout_History = QVBoxLayout(self.groupBox_History)

        self.gridLayout_Controls = QGridLayout()
        self.gridLayout_Controls.addWidget(QLabel("Data Start:"), 0, 0)
        self.dateTimeEdit_Start = QDateTimeEdit(self.groupBox_History)
        self.gridLayout_Controls.addWidget(self.dateTimeEdit_Start, 0, 1)

        self.gridLayout_Controls.addWidget(QLabel("Data Sfârșit:"), 1, 0)
        self.dateTimeEdit_End = QDateTimeEdit(self.groupBox_History)
        self.gridLayout_Controls.addWidget(self.dateTimeEdit_End, 1, 1)

        self.pushButton_GenerateReport = QPushButton("Actualizează Grafic")
        self.gridLayout_Controls.addWidget(self.pushButton_GenerateReport, 2, 0)

        self.pushButton_Export = QPushButton("Export CSV")
        self.gridLayout_Controls.addWidget(self.pushButton_Export, 2, 1)

        self.verticalLayout_History.addLayout(self.gridLayout_Controls)

        self.chart_layout_container = QVBoxLayout()
        self.chart_placeholder_widget = QWidget()
        self.chart_placeholder_widget.setMinimumHeight(300)
        self.chart_placeholder_layout = QVBoxLayout(self.chart_placeholder_widget)
        self.chart_layout_container.addWidget(self.chart_placeholder_widget)
        self.verticalLayout_History.addLayout(self.chart_layout_container)

        self.verticalLayout_main.addWidget(self.groupBox_History)

        self.textEdit_HistoryOutput = QTextEdit(MeterDetailDialog)
        self.textEdit_HistoryOutput.setReadOnly(True)
        self.textEdit_HistoryOutput.setMaximumHeight(80)
        self.verticalLayout_main.addWidget(self.textEdit_HistoryOutput)

        self.retranslateUi(MeterDetailDialog)
        QMetaObject.connectSlotsByName(MeterDetailDialog)

    def retranslateUi(self, MeterDetailDialog):
        MeterDetailDialog.setWindowTitle(QCoreApplication.translate("MeterDetailDialog", u"Detalii Contor", None))