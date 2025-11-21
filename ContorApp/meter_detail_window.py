import csv
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox, QPushButton
from PySide6.QtCore import QTimer, Slot, QDateTime
from ui_meter_details import Ui_MeterDetailDialog
import logging
from data_logger import DataLogger
from datetime import datetime

# --- Importuri pentru Matplotlib ---
import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

log = logging.getLogger('MeterDetailWindow')
log.setLevel(logging.INFO)


# --- Clasa Canvas pentru Grafice ---
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class MeterDetailWindow(QDialog):
    def __init__(self, slave_id, modbus_client, parent=None):
        super().__init__(parent)
        self.ui = Ui_MeterDetailDialog()
        self.ui.setupUi(self)

        self.slave_id = slave_id
        self.modbus_client = modbus_client
        self.data_logger = DataLogger()

        self.setWindowTitle(f"Analiză & Export - Contor ID {self.slave_id}")
        self.ui.label_MeterID_Title.setText(f"Monitorizare (ID: {self.slave_id})")

        # --- CONFIGURARE UI ---
        # 1. Ascundem elementele inutile (conform cerinței anterioare)
        self.ui.groupBox_Totals.setVisible(False)
        widgets_to_hide = [
            self.ui.label_Header_Power, self.ui.label_Header_Reactive,
            self.ui.label_Detail_PL1, self.ui.label_Detail_PL2, self.ui.label_Detail_PL3,
            self.ui.label_Detail_QL1, self.ui.label_Detail_QL2, self.ui.label_Detail_QL3
        ]
        for w in widgets_to_hide: w.setVisible(False)

        # 2. Adăugăm Graficul
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.ui.verticalLayout_main.insertWidget(3, self.canvas)

        # 3. Adăugăm Butonul de EXPORT CSV (Programatic)
        self.btn_export = QPushButton("Exportă Date în CSV (Excel)", self.ui.groupBox_History)
        # Îl adăugăm în layout-ul existent, sub celălalt buton
        self.ui.gridLayout_History.addWidget(self.btn_export, 3, 0, 1, 2)
        self.btn_export.clicked.connect(self.export_csv)

        # --- Inițializare Intervale Timp ---
        self.ui.dateTimeEdit_Start.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.ui.dateTimeEdit_End.setDateTime(QDateTime.currentDateTime())

        self.ui.pushButton_GenerateReport.clicked.connect(self.generate_report)

        # Timer pentru date live
        self.detail_timer = QTimer(self)
        self.detail_timer.timeout.connect(self.update_details)
        self.detail_timer.start(1000)

        self.clear_labels()
        self.update_details()

    def clear_labels(self):
        self.ui.label_Detail_IL1.setText("--- A")
        self.ui.label_Detail_UL1.setText("--- V")

    # --- FUNCȚIONALITATE 1: ALERTE VIZUALE ---
    def get_alert_style(self, value, value_type):
        """
        Returnează stilul CSS (culoarea) în funcție de limite.
        Poți modifica valorile de aici pentru a schimba pragurile.
        """
        if value_type == 'voltage':
            # Standard 230V +/- 10% (207V - 253V)
            if value < 207 or value > 253:
                return "color: red; font-weight: bold; font-size: 14px;"
            return "color: black;"

        if value_type == 'current':
            # Exemplu: Siguranță de 16A
            limit_warning = 14.5
            limit_critical = 16.0

            if value > limit_critical:
                return "color: red; font-weight: bold; font-size: 14px;"
            if value > limit_warning:
                return "color: orange; font-weight: bold;"
            return "color: black;"

        return "color: black;"

    @Slot()
    def update_details(self):
        """Afișează datele live cu ALERTE VIZUALE."""
        if not self.modbus_client or not self.modbus_client.client or not self.modbus_client.client.is_socket_open():
            return

        currents = self.modbus_client.read_currents_float(self.slave_id)
        voltages = self.modbus_client.read_voltages_float(self.slave_id)

        # Actualizare Curenți cu Alerte
        if currents:
            for phase in ['L1', 'L2', 'L3']:
                val = currents.get(phase, 0)
                label = getattr(self.ui, f"label_Detail_I{phase}")
                label.setText(f"{val:.2f} A")
                label.setStyleSheet(self.get_alert_style(val, 'current'))

        # Actualizare Tensiuni cu Alerte
        if voltages:
            for phase in ['L1', 'L2', 'L3']:
                val = voltages.get(phase, 0)
                label = getattr(self.ui, f"label_Detail_U{phase}")
                label.setText(f"{val:.1f} V")
                label.setStyleSheet(self.get_alert_style(val, 'voltage'))

    # --- FUNCȚIONALITATE 2: EXPORT CSV ---
    @Slot()
    def export_csv(self):
        start_str = self.ui.dateTimeEdit_Start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_str = self.ui.dateTimeEdit_End.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        # 1. Obținem datele brute din DB
        # Formatul primit este: (timestamp, current_l1, voltage_l1, power_total, frequency)
        raw_data = self.data_logger.get_historical_data(self.slave_id, start_str, end_str)

        if not raw_data:
            QMessageBox.warning(self, "Export", "Nu există date în intervalul selectat.")
            return

        # 2. Alegem unde salvăm fișierul
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvează Raport CSV",
            f"raport_contor_{self.slave_id}.csv",
            "CSV Files (*.csv)"
        )

        if not filename:
            return

            # 3. Scriem fișierul cu coloanele dorite
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # --- MODIFICAREA 1: Header-ul personalizat ---
                writer.writerow(["Timestamp", "Curent L1 [A]", "Tensiune L1 [V]", "Putere Totala [kW]"])

                # --- MODIFICAREA 2: Filtrarea coloanelor ---
                for row in raw_data:
                    # row conține 5 elemente. Noi vrem doar primele 4 (0, 1, 2, 3).
                    # row[:4] taie lista și ia doar primele 4 elemente, ignorând Frecvența.
                    writer.writerow(row[:4])

            QMessageBox.information(self, "Succes", f"Date exportate cu succes în:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Nu s-a putut salva fișierul.\nEroare: {e}")
    @Slot()
    def generate_report(self):
        """Generează graficul de consum (codul anterior)."""
        start_str = self.ui.dateTimeEdit_Start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_str = self.ui.dateTimeEdit_End.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        self.ui.textEdit_HistoryOutput.clear()
        self.ui.textEdit_HistoryOutput.setText(f"Analiză perioadă: {start_str} -> {end_str}\n")

        raw_data = self.data_logger.get_historical_data(self.slave_id, start_str, end_str)

        if not raw_data or len(raw_data) < 2:
            self.ui.textEdit_HistoryOutput.append("Date insuficiente pentru grafic.")
            self.canvas.axes.clear()
            self.canvas.draw()
            return

        timestamps = []
        energy_vals = []
        total_kwh = 0.0

        prev_time = datetime.strptime(raw_data[0][0], "%Y-%m-%d %H:%M:%S")
        prev_power = raw_data[0][3]

        for i in range(1, len(raw_data)):
            curr_row = raw_data[i]
            curr_time = datetime.strptime(curr_row[0], "%Y-%m-%d %H:%M:%S")
            curr_power = curr_row[3]

            hours = (curr_time - prev_time).total_seconds() / 3600.0
            avg_p = (prev_power + curr_power) / 2.0
            kwh = avg_p * hours
            if kwh < 0: kwh = 0

            timestamps.append(curr_time)
            energy_vals.append(kwh)
            total_kwh += kwh

            prev_time = curr_time
            prev_power = curr_power

        self.canvas.axes.cla()
        self.canvas.axes.bar(timestamps, energy_vals, width=0.01, color='orange', alpha=0.7, label='Consum (kWh)')
        self.canvas.axes.set_title(f"Consum Total: {total_kwh:.3f} kWh", fontsize=11, fontweight='bold')
        self.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.canvas.fig.autofmt_xdate()
        self.canvas.draw()

        self.ui.textEdit_HistoryOutput.append(f"TOTAL ENERGIE: {total_kwh:.4f} kWh")

    def closeEvent(self, event):
        self.detail_timer.stop()
        super().closeEvent(event)