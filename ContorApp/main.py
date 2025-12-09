import sys
import logging
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem,
                               QPushButton, QWidget, QHBoxLayout, QAbstractItemView)
from PySide6.QtCore import QTimer, Slot, Qt, QThread, Signal

from data_logger import DataLogger
from ui_mainwindow import Ui_MainWindow
from modbus_worker import ModbusWorker
from meter_detail_window import MeterDetailWindow

# Configurare Logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('MainWindow')

DEFAULT_METER_DATA = {
    'frequency': '---',
    'status': 'Necunoscut',
    'last_read': 'N/A'
}


class MainWindow(QMainWindow):
    # Semnale pentru a controla worker-ul
    start_worker_polling = Signal()
    stop_worker_polling = Signal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Monitorizare Multi-Contor Modbus (Multi-Threaded)")

        # --- CONFIGURARE ---
        self.modbus_port = 'COM5'  # Verifică portul!
        self.slave_ids = list(range(1, 21))  # ID-uri de la 1 la 20
        self.timer_interval_ms = 3000  # Scanare la fiecare 3 secunde

        # Inițializare DataLogger
        self.data_logger = DataLogger()

        # Configurare Tabel (UI)
        self.setup_meter_table()

        # Configurare Worker Thread (Modbus)
        self.setup_worker_thread()

        # Configurare Timer pentru citire ciclică
        self.read_timer = QTimer(self)
        self.read_timer.timeout.connect(self.run_worker_cycle)

        # Conectare Butoane UI
        self.ui.pushButton_Connect.clicked.connect(self.toggle_connection)

        self.is_connected = False
        self.log_message("Aplicație inițializată. Apasă 'Conectare'.")

    def setup_worker_thread(self):
        """Creează worker-ul și thread-ul pe care va rula."""
        self.worker_thread = QThread()
        self.worker = ModbusWorker(
            port=self.modbus_port,
            slave_ids=self.slave_ids,
            interval_ms=self.timer_interval_ms
        )
        self.worker.moveToThread(self.worker_thread)

        # Conectăm semnalele
        self.worker_thread.started.connect(self.worker.start_polling)
        self.worker.cycle_finished.connect(self.update_table_from_data)
        self.worker.log_message.connect(self.log_message)

        # Semnale de control din Main spre Worker
        self.start_worker_polling.connect(self.worker.run_read_cycle)
        self.stop_worker_polling.connect(self.worker.stop_polling)

        self.worker_thread.start()

    def setup_meter_table(self):
        """Configurează QTableWidget cu rânduri și butoane."""
        table = self.ui.tableWidget_Meters
        table.setRowCount(len(self.slave_ids))
        # Setăm coloanele: ID, Status, Curent L1, Detalii
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID Slave", "Status Conexiune", "L1 Curent [A]", "Acțiune"])

        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Ajustare lățime coloane
        table.setColumnWidth(0, 60)  # ID mai îngust
        table.setColumnWidth(1, 150)  # Status lat
        table.setColumnWidth(2, 120)  # Curent

        for row, slave_id in enumerate(self.slave_ids):
            # Coloana 0: ID Slave
            item_id = QTableWidgetItem(str(slave_id))
            item_id.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, item_id)

            # Coloana 1: Status (Initial Deconectat)
            item_status = QTableWidgetItem("Deconectat")
            item_status.setTextAlignment(Qt.AlignCenter)
            item_status.setForeground(Qt.gray)
            table.setItem(row, 1, item_status)

            # Coloana 2: Date
            item_data = QTableWidgetItem("---")
            item_data.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, item_data)

            # Coloana 3: Buton Detalii
            self.add_details_button(row, slave_id)

    def add_details_button(self, row, slave_id):
        """Adaugă butonul de Detalii în ultima coloană."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        btn = QPushButton("Detalii >>")
        # Folosim lambda pentru a captura slave_id corect
        btn.clicked.connect(lambda: self.show_meter_details(slave_id))

        # Stilizare buton (opțional)
        btn.setCursor(Qt.PointingHandCursor)

        layout.addWidget(btn)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.ui.tableWidget_Meters.setCellWidget(row, 3, widget)

    @Slot()
    def toggle_connection(self):
        """Pornește/Oprește citirea ciclică."""
        if not self.is_connected:
            self.log_message(f"Se pornește citirea (interval {self.timer_interval_ms} ms)...")
            self.read_timer.start(self.timer_interval_ms)
            self.ui.pushButton_Connect.setText("Deconectare")
            self.ui.pushButton_Connect.setStyleSheet("background-color: #e74c3c; color: white;")
            self.is_connected = True
            # Cerem o citire imediată
            self.run_worker_cycle()
        else:
            self.log_message("Se oprește citirea...")
            self.read_timer.stop()
            self.ui.pushButton_Connect.setText("Conectare la Magistrala Modbus")
            self.ui.pushButton_Connect.setStyleSheet("")
            self.is_connected = False
            self.update_ui_disconnected()

    @Slot()
    def run_worker_cycle(self):
        """Trigger timer -> Worker."""
        self.start_worker_polling.emit()

    @Slot(dict)
    def update_table_from_data(self, results):
        """
        PRIMEȘTE datele de la worker și actualizează UI-ul.
        Aceasta este versiunea consolidată și corectă.
        """
        table = self.ui.tableWidget_Meters

        for row, slave_id in enumerate(self.slave_ids):
            # Obținem rezultatul sau un default de eroare
            data = results.get(slave_id, {"status": "Eroare"})

            status_item = table.item(row, 1)
            data_item = table.item(row, 2)

            # Resetăm stilul de bază
            status_item.setTextAlignment(Qt.AlignCenter)
            data_item.setTextAlignment(Qt.AlignCenter)

            # --- LOGICA VIZUALĂ PENTRU STATUS ---
            if data["status"] == "OK":
                # CAZ: ONLINE (VERDE)
                status_item.setText("ONLINE")
                status_item.setBackground(QColor("#2ecc71"))  # Verde
                status_item.setForeground(QColor("white"))

                # Actualizare date (Curent L1)
                current_l1 = data["currents"].get('L1', 0)
                data_item.setText(f"{current_l1:.2f} A")

                # Logare în baza de date
                log_data = {
                    'L1_I': data["currents"].get('L1', 0),
                    'L1_U': data["voltages"].get('L1L2', 0),  # Aproximare tensiune linie
                    'P_Total': 0.0,  # ModbusWorker curent nu citeste puteri, poti adauga daca vrei
                    'Frequency': 0.0
                }
                self.data_logger.log_reading(slave_id, log_data)

            elif data["status"] == "Skipped (Offline)":
                # CAZ: SKIPPED / COOLDOWN (PORTOCALIU)
                status_item.setText("OFFLINE (Skip)")
                status_item.setBackground(QColor("#f39c12"))  # Portocaliu
                status_item.setForeground(QColor("white"))
                data_item.setText("---")

            else:
                # CAZ: EROARE / TIMEOUT (ROȘU)
                status_item.setText("OFFLINE")
                status_item.setBackground(QColor("#e74c3c"))  # Roșu
                status_item.setForeground(QColor("white"))
                data_item.setText("---")

        self.ui.label_Status.setText("Status Rețea: Actualizat")

    def update_ui_disconnected(self):
        """Resetează tabelul vizual când se apasă Deconectare."""
        table = self.ui.tableWidget_Meters
        for row in range(len(self.slave_ids)):
            status_item = table.item(row, 1)
            data_item = table.item(row, 2)

            status_item.setText("Deconectat")
            status_item.setBackground(QColor("white"))  # Reset background
            status_item.setForeground(Qt.gray)

            data_item.setText("---")

        self.ui.label_Status.setText("Status Rețea: Deconectat")

    @Slot()
    def show_meter_details(self, slave_id):
        """Deschide fereastra de detalii."""
        self.log_message(f"Deschidere detalii ID {slave_id}...")

        # ATENȚIE: Trimitem clientul, dar worker-ul rulează în paralel.
        # Ideal ar fi să oprim timer-ul principal cât timp ne uităm la detalii
        # pentru a evita conflicte pe portul serial.

        was_running = self.read_timer.isActive()
        if was_running:
            self.read_timer.stop()  # Pauză la scanarea generală

        details_window = MeterDetailWindow(
            slave_id=slave_id,
            modbus_client=self.worker.modbus_client,
            parent=self
        )
        details_window.exec()  # Blocant

        # Repornim scanarea dacă era pornită
        if was_running:
            self.read_timer.start(self.timer_interval_ms)

    def log_message(self, message):
        self.ui.textEdit_Log.append(message)
        # Scroll automat jos
        sb = self.ui.textEdit_Log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def closeEvent(self, event):
        """Oprește corect thread-urile la închidere."""
        self.read_timer.stop()
        self.stop_worker_polling.emit()
        self.worker_thread.quit()
        self.worker_thread.wait(2000)
        self.data_logger.disconnect()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())