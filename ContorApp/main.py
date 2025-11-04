
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout
from PySide6.QtCore import QTimer, Slot, Qt
from PySide6.QtWidgets import QAbstractItemView

from data_logger import DataLogger
from ui_mainwindow import Ui_MainWindow
from modbus_client import ContorModbusClient
from meter_detail_window import MeterDetailWindow  # Noul import

DEFAULT_METER_DATA = {
    'frequency': '---',
    'status': 'Necunoscut',
    'last_read': 'N/A'
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Monitorizare Multi-Contor Modbus")

        # --- Setări Multi-Contor ---
        self.modbus_port = 'COM3'
        self.slave_ids = list(range(1, 11))  # ID-urile slave de la 1 la 10
        self.modbus_client = ContorModbusClient(port=self.modbus_port)

        # Stocarea datelor citite
        self.meter_data = {sid: DEFAULT_METER_DATA.copy() for sid in self.slave_ids}

        # --- Timer și Conexiuni ---
        self.read_timer = QTimer(self)
        self.read_timer.timeout.connect(self.update_all_meters)
        self.timer_interval_ms = 3000  # Citire la fiecare 3 secunde

        self.ui.pushButton_Connect.clicked.connect(self.toggle_connection)
        self.is_connected = False
        self.data_logger= DataLogger()
        self.log_message("Aplicație pornită.")
        self.setup_meter_table()

    def setup_meter_table(self):
        """Configurează QTableWidget cu 10 rânduri și butoane."""
        table = self.ui.tableWidget_Meters
        table.setRowCount(len(self.slave_ids))
        table.setHorizontalHeaderLabels(["ID Slave", "Status Conexiune", "Frecvență", "Acțiune"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setColumnWidth(1, 200)

        for row, slave_id in enumerate(self.slave_ids):
            # Coloana 0: ID Slave
            item = QTableWidgetItem(str(slave_id))
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, item)

            # Coloana 3: Buton Detalii
            self.add_details_button(row, slave_id)

    def add_details_button(self, row, slave_id):
        """Adaugă butonul de Detalii în ultima coloană."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        btn = QPushButton("Detalii >>")
        btn.clicked.connect(lambda: self.show_meter_details(slave_id))

        layout.addWidget(btn)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.ui.tableWidget_Meters.setCellWidget(row, 3, widget)

    @Slot()
    def toggle_connection(self):
        if not self.is_connected:
            self.log_message(f"Se încearcă conectarea la {self.modbus_port}...")
            if self.modbus_client.connect():
                self.log_message("Conexiune Modbus reușită. Se pornește citirea ciclincă.")
                self.ui.pushButton_Connect.setText("Deconectare")
                self.is_connected = True
                self.read_timer.start(self.timer_interval_ms)
                self.update_all_meters()
            else:
                self.log_message("Conectarea a eșuat.")
        else:
            self.read_timer.stop()
            self.modbus_client.disconnect()
            self.log_message("Deconectat.")
            self.ui.pushButton_Connect.setText("Conectare")
            self.is_connected = False
            self.update_ui_disconnected()

    @Slot()
    def update_all_meters(self):
        """Citirea ciclică a datelor pentru toate cele 10 contoare."""
        if not self.is_connected:
            return

        self.log_message("Începe ciclul de citire pentru 10 contoare...")

        table = self.ui.tableWidget_Meters

        for row, slave_id in enumerate(self.slave_ids):
            params = self.modbus_client.read_system_params(slave_id)
            currents = self.modbus_client.read_currents_float(slave_id)
            voltages = self.modbus_client.read_voltages_float(slave_id)
            powers = self.modbus_client.read_powers_float(slave_id)

            status_item = table.item(row, 1)
            freq_item = table.item(row, 2)

            read_successful = params and currents and voltages and powers

            if read_successful:

                freq = params.get('Frequency')
                status_item.setText("OK")
                status_item.setForeground(Qt.darkGreen)
                freq_item.setText(f"{freq:.1f} Hz")

                #  COLECTARE DATE PENTRU LOGARE
                log_data = {
                    'L1_I': currents.get('L1'),
                    'L1_U': voltages.get('L1'),
                    'P_Total': powers.get('P_Total'),
                    'Frequency': freq
                }

                #  LOGARE ÎN BAZA DE DATE
                self.data_logger.log_reading(slave_id, log_data)

            else:

                status_item.setText("Eroare comunicare")
                status_item.setForeground(Qt.red)
                freq_item.setText("--- Hz")

        self.ui.label_Status.setText("Status Rețea: Citire în desfășurare")
        self.log_message("Ciclul de citire a fost finalizat și datele au fost logate.")
    @Slot()
    def show_meter_details(self, slave_id):
        """Deschide fereastra de detalii pentru contorul selectat, indiferent de starea conexiunii Modbus."""

        # Trimitem clientul Modbus (care poate fi deconectat) și ID-ul slave
        details_window = MeterDetailWindow(
            slave_id=slave_id,
            modbus_client=self.modbus_client,
            parent=self
        )

        # Dacă clientul nu este conectat, fereastra de detalii va afișa "---" și un mesaj de warning.
        self.log_message(f"Se deschid detaliile pentru Contor ID {slave_id}.")

        details_window.exec()
    def update_ui_disconnected(self):
        """Actualizează UI la deconectare."""
        for row in range(len(self.slave_ids)):
            self.ui.tableWidget_Meters.item(row, 1).setText("Deconectat")
            self.ui.tableWidget_Meters.item(row, 1).setForeground(Qt.gray)
            self.ui.tableWidget_Meters.item(row, 2).setText("---")
        self.ui.label_Status.setText("Status Rețea: Deconectat")

    def log_message(self, message):
        self.ui.textEdit_Log.append(message)
        # print(message)

    def closeEvent(self, event):
        self.data_logger.disconnect()
        self.read_timer.stop()
        if self.modbus_client:
            self.modbus_client.disconnect()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())