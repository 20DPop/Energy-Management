import sys
import logging  # <-- 1. Importă modulul logging

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem,
                               QPushButton, QWidget, QHBoxLayout, QAbstractItemView)
from PySide6.QtCore import QTimer, Slot, Qt, QThread, Signal

from data_logger import DataLogger
from ui_mainwindow import Ui_MainWindow
# Importăm Worker-ul, nu clientul direct
from modbus_worker import ModbusWorker
from meter_detail_window import MeterDetailWindow
log = logging.getLogger('MainWindow')
log.setLevel(logging.INFO)

DEFAULT_METER_DATA = {
    'frequency': '---',
    'status': 'Necunoscut',
    'last_read': 'N/A'
}


class MainWindow(QMainWindow):
    # Semnale pentru a porni/opri worker-ul
    start_worker_polling = Signal()
    stop_worker_polling = Signal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Monitorizare Multi-Contor Modbus (Multi-Threaded)")

        self.modbus_port = 'COM5'  # Asigură-te că acesta e portul corect
        self.slave_ids = list(range(1, 21))

        self.meter_data = {sid: DEFAULT_METER_DATA.copy() for sid in self.slave_ids}

        # Timer-ul va porni worker-ul
        self.read_timer = QTimer(self)
        self.timer_interval_ms = 3000  # 5 secunde
        self.read_timer.timeout.connect(self.run_worker_cycle)

        # Configurarea Worker Thread
        self.setup_worker_thread()

        self.ui.pushButton_Connect.clicked.connect(self.toggle_connection)
        self.is_connected = False
        self.data_logger = DataLogger()
        self.log_message("Aplicație pornită.")

        # --- APELUL CARE CAUZA EROAREA ---
        # Acum funcția de mai jos există
        self.setup_meter_table()

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
        self.start_worker_polling.connect(self.worker.run_read_cycle)
        self.stop_worker_polling.connect(self.worker.stop_polling)

        self.worker_thread.start()

    # --- FUNCȚIA LIPSA A FOST ADĂUGATĂ AICI ---
    def setup_meter_table(self):
        """Configurează QTableWidget cu 10 rânduri și butoane."""
        table = self.ui.tableWidget_Meters
        table.setRowCount(len(self.slave_ids))
        table.setHorizontalHeaderLabels(["ID Slave", "Status Conexiune", "L1 Curent [A]", "Acțiune"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 120)

        for row, slave_id in enumerate(self.slave_ids):
            # Coloana 0: ID Slave
            item_id = QTableWidgetItem(str(slave_id))
            item_id.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, item_id)

            # Coloana 1: Status
            item_status = QTableWidgetItem("Deconectat")
            item_status.setForeground(Qt.gray)
            table.setItem(row, 1, item_status)

            # Coloana 2: Date
            item_data = QTableWidgetItem("--- A")
            table.setItem(row, 2, item_data)

            # Coloana 3: Buton Detalii
            self.add_details_button(row, slave_id)

    # --- FUNCȚIA LIPSA A FOST ADĂUGATĂ AICI ---
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
        """Acum doar pornește/oprește QTimer-ul."""
        if not self.is_connected:
            self.log_message(f"Se pornește citirea ciclincă (la fiecare {self.timer_interval_ms} ms)...")
            self.read_timer.start(self.timer_interval_ms)
            self.ui.pushButton_Connect.setText("Deconectare")
            self.is_connected = True
            # Cerem o citire imediată, fără a aștepta timer-ul
            self.run_worker_cycle()
        else:
            self.log_message("Se oprește citirea ciclincă...")
            self.read_timer.stop()
            self.ui.pushButton_Connect.setText("Conectare")
            self.is_connected = False
            self.update_ui_disconnected()

    @Slot()
    def run_worker_cycle(self):
        """Slot apelat de QTimer. Emite un semnal către worker."""
        self.start_worker_polling.emit()

    @Slot(object)
    def update_table_from_data(self, results):
        """
        PRIMEȘTE datele de la worker thread și actualizează UI-ul.
        Această funcție rulează în siguranță pe Main Thread.
        """
        self.log_message("Ciclu de citire terminat. Se actualizează tabelul...")
        table = self.ui.tableWidget_Meters

        for row, slave_id in enumerate(self.slave_ids):
            data = results.get(slave_id, {"status": "Eroare"})

            status_item = table.item(row, 1)
            data_item = table.item(row, 2)

            if data["status"] == "OK":
                status_item.setText("OK")
                status_item.setForeground(Qt.darkGreen)
                current_l1 = data["currents"].get('L1', 0)
                data_item.setText(f"{current_l1:.1f} A")

                # Logarea în baza de date
                log_data = {
                    'L1_I': data["currents"].get('L1'),
                    'L2_I': data["currents"].get('L2'),
                    'L3_I': data["currents"].get('L3'),
                    'L1L2_U': data["voltages"].get('L1L2'),
                    'L2L3_U': data["voltages"].get('L2L3'),
                    'L3L1_U': data["voltages"].get('L3L1')
                }
                # self.data_logger.log_reading(slave_id, log_data) # Activat

            else:  # data["status"] == "Eroare"
                status_item.setText("Eroare comunicare")
                status_item.setForeground(Qt.red)
                data_item.setText("--- A")

        self.ui.label_Status.setText("Status Rețea: Așteaptă următorul ciclu...")

    @Slot()
    def show_meter_details(self, slave_id):
        """
        Atenție: Trimiterea clientului Modbus către altă fereastră
        poate cauza conflicte de thread dacă ambele încearcă să-l folosească simultan.
        """
        self.log_message(f"Se deschid detaliile pentru Contor ID {slave_id}.")

        details_window = MeterDetailWindow(
            slave_id=slave_id,
            modbus_client=self.worker.modbus_client,  # Trimitem clientul din worker
            parent=self
        )
        details_window.exec()

    def update_ui_disconnected(self):
        """Actualizează UI la deconectare."""

        # --- LINIA CARE LIPSEA ---
        table = self.ui.tableWidget_Meters
        # -------------------------

        for row in range(len(self.slave_ids)):
            # Verificăm dacă item-urile există înainte de a le modifica
            if not table.item(row, 1):
                table.setItem(row, 1, QTableWidgetItem())
            if not table.item(row, 2):
                table.setItem(row, 2, QTableWidgetItem())

            table.item(row, 1).setText("Deconectat")
            table.item(row, 1).setForeground(Qt.gray)
            table.item(row, 2).setText("--- A")

        self.ui.label_Status.setText("Status Rețea: Deconectat")
    def log_message(self, message):
        self.ui.textEdit_Log.append(message)
        # print(message)

    def closeEvent(self, event):
        """Oprește corect thread-ul la închidere."""
        self.log_message("Se închide aplicația...")
        self.read_timer.stop()
        self.stop_worker_polling.emit()
        self.worker_thread.quit()
        if not self.worker_thread.wait(3000):
            log.warning("Thread-ul nu s-a oprit la timp, se forțează terminarea.")
            self.worker_thread.terminate()

        self.data_logger.disconnect()
        log.info("Închidere finalizată.")
        super().closeEvent(event)

    @Slot(dict)
    def update_table_from_data(self, results):
        """
        Actualizează tabelul cu datele primite de la Worker.
        Include stilizare vizuală pentru status (ONLINE/OFFLINE).
        """
        # self.log_message("Ciclu terminat. Actualizare UI...") # Poți comenta asta să nu umple logul
        table = self.ui.tableWidget_Meters

        for row, slave_id in enumerate(self.slave_ids):
            # Obținem rezultatul sau un default de eroare
            data = results.get(slave_id, {"status": "Eroare"})

            # Ne asigurăm că celulele există
            if not table.item(row, 1):
                table.setItem(row, 1, QTableWidgetItem())
            if not table.item(row, 2):
                table.setItem(row, 2, QTableWidgetItem())

            status_item = table.item(row, 1)
            data_item = table.item(row, 2)

            # Resetăm stilul de bază
            status_item.setTextAlignment(Qt.AlignCenter)
            data_item.setTextAlignment(Qt.AlignCenter)

            # --- LOGICA VIZUALĂ PENTRU STATUS ---
            if data["status"] == "OK":
                # CAZ: ONLINE
                status_item.setText("ONLINE")
                # Fundal Verde, Text Alb, Bold
                status_item.setBackground(QColor("#2ecc71"))  # Verde smarald
                status_item.setForeground(QColor("white"))
                status_item.setToolTip("Conexiune stabilă. Datele se actualizează.")

                # Actualizare date
                current_l1 = data["currents"].get('L1', 0)
                data_item.setText(f"{current_l1:.2f} A")

                # Logare (opțional)
                # ... cod logare ...

            elif data["status"] == "Skipped (Offline)":
                # CAZ: SKIPPED (Cooldown)
                status_item.setText("OFFLINE (Skip)")
                # Fundal Galben/Portocaliu
                status_item.setBackground(QColor("#f39c12"))
                status_item.setForeground(QColor("white"))
                status_item.setToolTip("Contorul nu a răspuns anterior. Se așteaptă expirarea timpului de cooldown.")

                data_item.setText("---")

            else:
                # CAZ: EROARE / TIMEOUT
                status_item.setText("OFFLINE")
                # Fundal Roșu
                status_item.setBackground(QColor("#e74c3c"))
                status_item.setForeground(QColor("white"))
                status_item.setToolTip("Contorul nu răspunde la interogare.")

                data_item.setText("---")

        self.ui.label_Status.setText("Status Rețea: Actualizat")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())