import sys
# [MODIFICAT] Am adăugat QMessageBox pentru mesajul de avertizare
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout, QMessageBox
from PySide6.QtCore import QTimer, Slot, Qt
from PySide6.QtWidgets import QAbstractItemView

from data_logger import DataLogger
from ui_mainwindow import Ui_MainWindow
from modbus_client import ContorModbusClient
from meter_detail_window import MeterDetailWindow

DEFAULT_METER_DATA = {
    'frequency': '---',
    'status': 'Necunoscut', # Vom folosi 'Necunoscut', 'ON', 'OFF'
    'last_read': 'N/A'
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Monitorizare Multi-Contor Modbus")

        # --- Setări Multi-Contor ---
        self.modbus_port = 'COM5'
        self.slave_ids = list(range(1, 21))  # ID-urile slave de la 1 la 10
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
        """[MODIFICAT] Configurează QTableWidget și inițializează celulele de status."""
        table = self.ui.tableWidget_Meters
        table.setRowCount(len(self.slave_ids))
        table.setHorizontalHeaderLabels(["ID Slave", "Stare", "Frecvență", "Acțiune"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setColumnWidth(1, 150) # Am ajustat puțin lățimea

        for row, slave_id in enumerate(self.slave_ids):
            # Coloana 0: ID Slave
            item_id = QTableWidgetItem(str(slave_id))
            item_id.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, item_id)

            # [ADAUGAT] Inițializăm celulele pentru Stare și Frecvență
            # Acest pas este CRITIC. Fără el, .item(row, 1) ar fi None și ar da crash.
            item_status = QTableWidgetItem("Necunoscut")
            item_status.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, item_status)

            item_freq = QTableWidgetItem("---")
            item_freq.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, item_freq)

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
                self.update_all_meters() # Rulăm o dată imediat
            else:
                self.log_message("Conectarea a eșuat.")
        else:
            self.read_timer.stop()
            self.modbus_client.disconnect()
            self.log_message("Deconectat.")
            self.ui.pushButton_Connect.setText("Conectare la Magistrala Modbus")
            self.is_connected = False
            self.update_ui_disconnected()

    @Slot()
    def update_all_meters(self):
        """[MODIFICAT] Citirea ciclică și actualizarea stării ON/OFF."""
        if not self.is_connected:
            return

        self.log_message("Începe ciclul de citire pentru 10 contoare...")
        table = self.ui.tableWidget_Meters

        for row, slave_id in enumerate(self.slave_ids):
            # Citim datele esențiale
            currents = self.modbus_client.read_currents_float(slave_id)
            voltages = self.modbus_client.read_voltages_float(slave_id)
            
            # (Puteți decomenta citirea parametrilor dacă o reparați în modbus_client.py)
            # params = self.modbus_client.read_system_params(slave_id) 

            # Recuperăm item-urile din tabel (acum sunt garantat să existe)
            status_item = table.item(row, 1)
            freq_item = table.item(row, 2)

            # Verificăm dacă citirea a fost un succes
            read_successful = currents and voltages # (și 'params' dacă decomentați)

            if read_successful:
                # [MODIFICAT] Setăm starea ca ON (Activ)
                self.meter_data[slave_id]['status'] = 'ON'
                status_item.setText("ON")
                status_item.setForeground(Qt.darkGreen)
                
                # freq = params.get('Frequency', 0.0)
                # freq_item.setText(f"{freq:.1f} Hz")
                # self.meter_data[slave_id]['frequency'] = freq

                #  COLECTARE DATE PENTRU LOGARE
                log_data = {
                    'L1_I': currents.get('L1'),
                    'L1_U': voltages.get('L1'),
                    # 'P_Total': powers.get('P_Total'),
                    # 'Frequency': freq
                }
                self.data_logger.log_reading(slave_id, log_data)

            else:
                # [MODIFICAT] Setăm starea ca OFF (Inactiv / Eroare)
                self.meter_data[slave_id]['status'] = 'OFF'
                status_item.setText("OFF")
                status_item.setForeground(Qt.red)
                freq_item.setText("--- Hz")

        self.ui.label_Status.setText("Status Rețea: Citire în desfășurare")
        self.log_message("Ciclul de citire a fost finalizat și datele au fost logate.")
        
    @Slot()
    def show_meter_details(self, slave_id):
        """
        [MODIFICAT] Deschide fereastra de detalii DOAR dacă contorul este 'ON'.
        Altfel, afișează un mesaj de avertizare.
        """

        # [ADAUGAT] Verificăm starea stocată a contorului
        current_status = self.meter_data.get(slave_id, {}).get('status', 'Necunoscut')
        
        if current_status != 'ON':
            # Dacă starea NU este 'ON', afișăm un mesaj și ieșim din funcție
            self.log_message(f"Acces blocat: Contorul ID {slave_id} este '{current_status}'.")
            QMessageBox.warning(
                self,
                "Contor Offline",
                f"Contorul cu ID-ul {slave_id} nu este conectat sau nu răspunde (Status: {current_status}).\n\n"
                "Fereastra de detalii nu poate fi deschisă."
            )
            return  # Oprim execuția aici
            
        # Acest cod se va executa DOAR dacă starea este 'ON'
        self.log_message(f"Se deschid detaliile pentru Contor ID {slave_id} (Status: ON).")

        details_window = MeterDetailWindow(
            slave_id=slave_id,
            modbus_client=self.modbus_client,
            parent=self
        )
        details_window.exec()

    def update_ui_disconnected(self):
        """[MODIFICAT] Actualizează UI și starea internă la deconectare."""
        for row, slave_id in enumerate(self.slave_ids):
            # Resetăm starea internă
            self.meter_data[slave_id]['status'] = 'Necunoscut'
            
            # Actualizăm celulele din tabel
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