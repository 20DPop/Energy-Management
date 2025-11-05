from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QTimer, Slot, QDateTime
from ui_meter_details import Ui_MeterDetailDialog
import logging
from data_logger import DataLogger

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
        self.setWindowTitle(f"Detalii Contor - ID {self.slave_id}")
        self.ui.label_MeterID_Title.setText(f"Contor Detalii (Slave ID: {self.slave_id})")

        # Inițializare UI istoric (Data/Ora)
        self.ui.dateTimeEdit_Start.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.ui.dateTimeEdit_End.setDateTime(QDateTime.currentDateTime())
        self.ui.pushButton_GenerateReport.clicked.connect(self.generate_report)

        # Timer specific pentru a citi datele în timp real când fereastra este deschisă
        self.detail_timer = QTimer(self)
        self.detail_timer.timeout.connect(self.update_details)
        self.detail_timer.start(1000)  # Citire mai rapidă (1 dată pe secundă)

        self.clear_labels()
        self.update_details()

    def clear_labels(self):
        # Setează toate label-urile la valoarea inițială
        # (Omit codul repetitiv, dar ideea este de a reseta toate label_Detail_* )
        self.ui.label_Detail_IL1.setText("--- A")
        self.ui.label_Detail_UL1.setText("--- V")
        self.ui.label_Detail_PL1.setText("--- kW")
        # etc.

    @Slot()
    def update_details(self):
        """Citește toate datele detaliate pentru acest contor."""
        if not self.modbus_client.client or not self.modbus_client.client.is_socket_open():
            log.warning(f"ID {self.slave_id}: Clientul Modbus nu este conectat.")
            self.clear_labels()
            return

        # 1. Curenți și Tensiuni
        currents = self.modbus_client.read_currents_float(self.slave_id)
        voltages = self.modbus_client.read_voltages_float(self.slave_id)

        if currents:
            self.ui.label_Detail_IL1.setText(f"{currents.get('L1', 0):.2f} A")
            self.ui.label_Detail_IL2.setText(f"{currents.get('L2', 0):.2f} A")
            self.ui.label_Detail_IL3.setText(f"{currents.get('L3', 0):.2f} A")
        if voltages:
            self.ui.label_Detail_UL1.setText(f"{voltages.get('L1', 0):.1f} V")
            self.ui.label_Detail_UL2.setText(f"{voltages.get('L2', 0):.1f} V")
            self.ui.label_Detail_UL3.setText(f"{voltages.get('L3', 0):.1f} V")

        # 2. Puteri
        # powers = self.modbus_client.read_powers_float(self.slave_id)
        # if powers:
        #     self.ui.label_Detail_PL1.setText(f"{powers.get('PL1', 0):.2f} kW")
        #     self.ui.label_Detail_PL2.setText(f"{powers.get('PL2', 0):.2f} kW")
        #     self.ui.label_Detail_PL3.setText(f"{powers.get('PL3', 0):.2f} kW")
        #     self.ui.label_Detail_P_Total.setText(f"{powers.get('P_Total', 0):.2f} kW")
        #     self.ui.label_Detail_Q_Total.setText(f"{powers.get('Q_Total', 0):.2f} kVAR")
        #     # Q L1/L2/L3 nu sunt implementate în ModbusClient, dar le-am adăugat în UI

        # 3. Parametri Sistem
        # system_params = self.modbus_client.read_system_params(self.slave_id)
        # if system_params:
        #     self.ui.label_Detail_Frequency.setText(f"{system_params.get('Frequency', 0):.1f} Hz")
        #     self.ui.label_Detail_PF_Total.setText(f"{system_params.get('PF_Total', 0):.3f}")

    @Slot()
    def generate_report(self):
        start_dt = self.ui.dateTimeEdit_Start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_dt = self.ui.dateTimeEdit_End.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        self.ui.textEdit_HistoryOutput.clear()
        self.ui.textEdit_HistoryOutput.setText(f"Se citesc datele istorice pentru ID {self.slave_id}...\n"
                                               f"Perioada: {start_dt} la {end_dt}\n\n")

        # Apel la funcția DataLogger
        history = self.data_logger.get_historical_data(
            self.slave_id,
            start_dt,
            end_dt
        )

        if history:
            output = ["Timestamp | I L1 [A] | U L1 [V] | P Total [kW] | Freq [Hz]"]
            output.append("-" * 60)

            for row in history:
                timestamp, i_l1, u_l1, p_total, freq = row
                output.append(f"{timestamp} | {i_l1:.2f} | {u_l1:.1f} | {p_total:.2f} | {freq:.1f}")

            self.ui.textEdit_HistoryOutput.append("\n".join(output))
            self.ui.textEdit_HistoryOutput.append(f"\nTotal înregistrări găsite: {len(history)}")
        else:
            self.ui.textEdit_HistoryOutput.append("Nicio înregistrare găsită în perioada selectată.")
    def closeEvent(self, event):
        self.detail_timer.stop()
        super().closeEvent(event)