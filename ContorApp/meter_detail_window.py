import sys
import csv
import logging
from datetime import datetime, timedelta
from PySide6.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, Slot, QDateTime
from ui_meter_details import Ui_MeterDetailDialog
from data_logger import DataLogger

# Încercăm să importăm matplotlib pentru grafice
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("ATENȚIE: 'matplotlib' nu este instalat. Graficul nu va funcționa.")

log = logging.getLogger('MeterDetailWindow')
log.setLevel(logging.INFO)


class MeterDetailWindow(QDialog):
    def __init__(self, slave_id, modbus_client, parent=None):
        super().__init__(parent)
        self.ui = Ui_MeterDetailDialog()
        self.ui.setupUi(self)

        self.slave_id = slave_id
        self.modbus_client = modbus_client
        self.data_logger = DataLogger()

        # Titlu Fereastră
        self.setWindowTitle(f"Detalii Contor - ID {self.slave_id}")
        self.ui.label_MeterID_Title.setText(f"Contor Detalii (Slave ID: {self.slave_id})")

        # Setăm perioada implicită (Ultimele 24 ore)
        now = QDateTime.currentDateTime()
        self.ui.dateTimeEdit_Start.setDateTime(now.addDays(-1))
        self.ui.dateTimeEdit_End.setDateTime(now)

        # Conectare Butoane
        self.ui.pushButton_GenerateReport.clicked.connect(self.generate_report_and_chart)
        self.ui.pushButton_Export.clicked.connect(self.export_csv)

        # Timer pentru date live (citire la fiecare 1 secundă)
        self.detail_timer = QTimer(self)
        self.detail_timer.timeout.connect(self.update_details)
        self.detail_timer.start(1000)

        # --- INIȚIALIZARE GRAFIC ---
        self.figure = None
        self.canvas = None
        self.ax = None

        if MATPLOTLIB_AVAILABLE:
            self.init_chart()

        # Inițializare valori
        self.clear_labels()
        self.update_details()

        # Generăm automat graficul la deschidere (după scurt timp)
        QTimer.singleShot(500, self.generate_report_and_chart)

    def init_chart(self):
        """Inițializează zona de desenare Matplotlib în interfață."""
        self.figure = Figure(figsize=(5, 3.5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Adăugăm canvas-ul în layout-ul gol pregătit în UI
        self.ui.chart_placeholder_layout.addWidget(self.canvas)

        self.ax.set_title("Așteptare date...")
        self.ax.set_xlabel("Timp")
        self.ax.set_ylabel("Putere (kW)")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.canvas.draw()

    def clear_labels(self):
        self.ui.label_Detail_IL1.setText("--- A")
        self.ui.label_Detail_UL1_N.setText("--- V")
        self.ui.label_Detail_P_Total.setText("--- kW")

    def _update_voltage_LN(self, label, value):
        """
        Logică vizuală pentru Tensiunea Fază-Nul (Nominal 230V).
        Limite stricte: 220V - 237V
        """
        label.setText(f"{value:.1f} V")
        if value < 220.0 or value > 237.0:
            # ALARMĂ: Roșu Bold
            label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        else:
            # OK: Albastru
            label.setStyleSheet("color: #2980b9; font-weight: bold;")

    def _update_voltage_LL(self, label, value):
        """
        Logică vizuală pentru Tensiunea Linie-Linie (Nominal 400V).
        Limite: 380V - 420V
        """
        label.setText(f"{value:.1f} V")
        if value < 380.0 or value > 420.0:
            # ALARMĂ: Roșu Bold
            label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        else:
            # OK: Mov (Specific trifazic)
            label.setStyleSheet("color: #8e44ad; font-weight: bold;")

    def _update_diff_value(self, label, val1, val2):
        """Calculează și colorează diferența dintre două faze."""
        diff = abs(val1 - val2)
        label.setText(f"{diff:.1f} V")

        if diff > 10.0:
            # Dezechilibru Mare -> Roșu
            label.setStyleSheet("color: red; font-weight: bold;")
        elif diff > 5.0:
            # Atenție -> Portocaliu
            label.setStyleSheet("color: #e67e22; font-weight: bold;")
        else:
            # OK -> Gri/Verde
            label.setStyleSheet("color: green;")

    @Slot()
    def update_details(self):
        """Actualizează valorile instantanee (Live)."""
        if not self.modbus_client.client or not self.modbus_client.client.is_socket_open():
            return

        try:
            # Folosim citirea optimizată care aduce totul (I, U_LN, U_LL)
            data = None
            if hasattr(self.modbus_client, 'read_meter_data_optimized'):
                data = self.modbus_client.read_meter_data_optimized(self.slave_id)

            if data:
                # 1. Curenți
                self.ui.label_Detail_IL1.setText(f"{data.get('L1_I', 0):.2f} A")
                self.ui.label_Detail_IL2.setText(f"{data.get('L2_I', 0):.2f} A")
                self.ui.label_Detail_IL3.setText(f"{data.get('L3_I', 0):.2f} A")

                # 2. Tensiuni Fază-Nul (L-N) - Verificare prize (230V)
                ln1 = data.get('L1_N', 0)
                ln2 = data.get('L2_N', 0)
                ln3 = data.get('L3_N', 0)

                self._update_voltage_LN(self.ui.label_Detail_UL1_N, ln1)
                self._update_voltage_LN(self.ui.label_Detail_UL2_N, ln2)
                self._update_voltage_LN(self.ui.label_Detail_UL3_N, ln3)

                # 3. Tensiuni Linie-Linie (L-L) - Verificare motoare (400V)
                ll12 = data.get('L1L2_U', 0)
                ll23 = data.get('L2L3_U', 0)
                ll31 = data.get('L3L1_U', 0)

                self._update_voltage_LL(self.ui.label_Detail_UL1_L2, ll12)
                self._update_voltage_LL(self.ui.label_Detail_UL2_L3, ll23)
                self._update_voltage_LL(self.ui.label_Detail_UL3_L1, ll31)

                # 4. Diferențe (Dezechilibre între tensiunile de fază)
                # Comparăm L1 vs L2 (L-N) pentru a vedea dezechilibrul de încărcare
                if ln1 > 10:
                    self._update_diff_value(self.ui.label_Val_L1L2, ln1, ln2)
                    self._update_diff_value(self.ui.label_Val_L2L3, ln2, ln3)
                    self._update_diff_value(self.ui.label_Val_L3L1, ln3, ln1)

        except Exception as e:
            # log.error(f"Eroare update details: {e}")
            pass

    @Slot()
    def generate_report_and_chart(self):
        """Aduce datele istorice, calculează kWh și desenează graficul (Interval 3 Ore)."""
        start_dt_str = self.ui.dateTimeEdit_Start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_dt_str = self.ui.dateTimeEdit_End.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        self.ui.textEdit_HistoryOutput.setText(f"Se analizează datele între {start_dt_str} și {end_dt_str}...")

        # Luăm datele din DB
        history_data = self.data_logger.get_historical_data(self.slave_id, start_dt_str, end_dt_str)

        if not history_data:
            self.ui.textEdit_HistoryOutput.setText("Nu există date înregistrate în acest interval.")
            if self.ax:
                self.ax.clear()
                self.ax.set_title("Lipsă Date")
                self.canvas.draw()
            return

        timestamps = []
        power_values = []
        total_kwh = 0.0
        last_dt = None

        for row in history_data:
            # Structura row: timestamp, current, voltage, power, freq
            ts_str, i_l1, u_l1, p_total, freq = row
            try:
                dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")

                # Dacă nu avem putere citită, o estimăm (Monofazat L1)
                if p_total is None or p_total == 0:
                    val_power = (u_l1 * i_l1 * 0.9) / 1000.0
                else:
                    val_power = float(p_total)

                timestamps.append(dt)
                power_values.append(val_power)

                # Integrare pentru kWh (Putere * Timp)
                if last_dt is not None:
                    time_diff_hours = (dt - last_dt).total_seconds() / 3600.0
                    total_kwh += val_power * time_diff_hours
                last_dt = dt

            except ValueError:
                continue

        # Afișare Text Sumar
        if len(power_values) > 0:
            avg_power = sum(power_values) / len(power_values)
            max_power = max(power_values)
        else:
            avg_power = 0
            max_power = 0

        msg = (f"Interval: {start_dt_str} -> {end_dt_str}\n"
               f"----------------------------------------\n"
               f"CONSUM TOTAL ESTIMAT: {total_kwh:.3f} kWh\n"
               f"----------------------------------------\n"
               f"Putere Max: {max_power:.2f} kW\n"
               f"Putere Medie: {avg_power:.2f} kW")

        self.ui.textEdit_HistoryOutput.setText(msg)

        # Desenare Grafic
        if MATPLOTLIB_AVAILABLE and self.ax:
            self.ax.clear()

            # Linie Portocalie
            self.ax.plot(timestamps, power_values, color='#FF8C00', linewidth=2, label='Putere (kW)')
            # Umplere sub linie (opțional, arată bine)
            self.ax.fill_between(timestamps, power_values, color='#FF8C00', alpha=0.1)

            self.ax.set_title(f"Consum (Total: {total_kwh:.2f} kWh)", fontsize=10)
            self.ax.set_ylabel("Putere [kW]", color='#FF8C00', fontweight='bold')
            self.ax.grid(True, linestyle='--', alpha=0.5)

            # --- INTERVAL 3 ORE PE AXA X ---
            self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))

            # Format Data
            diff_days = (timestamps[-1] - timestamps[0]).days
            if diff_days < 1:
                # Doar ora dacă e o singură zi
                fmt = mdates.DateFormatter('%H:%M')
            else:
                # Ziua și Ora dacă sunt mai multe zile
                fmt = mdates.DateFormatter('%d/%m %H:%M')

            self.ax.xaxis.set_major_formatter(fmt)
            self.figure.autofmt_xdate(rotation=45)

            self.canvas.draw()

    @Slot()
    def export_csv(self):
        """Exportă datele brute în CSV."""
        start_dt = self.ui.dateTimeEdit_Start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_dt = self.ui.dateTimeEdit_End.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        data = self.data_logger.get_historical_data(self.slave_id, start_dt, end_dt)
        if not data:
            self.ui.textEdit_HistoryOutput.append("\nNu sunt date de exportat.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Salvează CSV", f"Raport_{self.slave_id}.csv",
                                                   "CSV Files (*.csv)")
        if file_name:
            try:
                with open(file_name, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Curent L1 [A]", "Tensiune L1 [V]", "Putere [kW]", "Freq [Hz]"])
                    writer.writerows(data)
                self.ui.textEdit_HistoryOutput.append(f"\nExportat cu succes în:\n{file_name}")
            except Exception as e:
                self.ui.textEdit_HistoryOutput.append(f"\nEroare la scriere: {e}")

    def closeEvent(self, event):
        self.detail_timer.stop()
        super().closeEvent(event)