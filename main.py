# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, Slot, QCoreApplication

# Importă clasa generată din ui_mainwindow.py
# NOTĂ: Asigură-te că rulezi pyside6-uic pe ui_mainwindow.ui pentru a genera acest fișier corect!
try:
    from ui_mainwindow import Ui_MainWindow
except ImportError:
    print(
        "Atenție: ui_mainwindow.py nu a fost găsit. Asigură-te că l-ai generat cu 'pyside6-uic ui_mainwindow.ui -o ui_mainwindow.py'.")
    # Ieșire grațioasă sau folosire a unui dummy class, dar e mai bine să forțăm generarea.
    sys.exit(1)

# Importă clientul Modbus
from modbus_client import ContorModbusClient


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Cititor Contor Eaton PXR")

        # --- CONFIGURARE MODBUS ---
        # TODO: Înlocuiește 'COM3' cu portul tău real (ex. 'COM5' pe Windows, '/dev/ttyUSB0' pe Linux)!
        self.modbus_port = 'COM3'
        # TODO: Ajustează adresa slave dacă nu e 2
        self.slave_addr = 2
        self.modbus_client = ContorModbusClient(port=self.modbus_port, slave_address=self.slave_addr)

        # Timer pentru citirea periodică a datelor
        self.read_timer = QTimer(self)
        self.read_timer.timeout.connect(self.update_data)
        self.timer_interval_ms = 2000  # Citește la fiecare 2 secunde (ajustează)

        # Conectează butonul
        self.ui.pushButton_Connect.setText("Conectare")
        self.ui.pushButton_Connect.clicked.connect(self.toggle_connection)
        self.is_connected = False

        # Status inițial
        self.log_message("Aplicație pornită. Gata de conectare.")
        self.ui.label_Status.setText("Status: Gata")
        self.clear_labels()

    # Adaugă un slot pentru logare, pentru a fi thread-safe dacă ai folosi thread-uri
    def log_message(self, message):
        """Afișează un mesaj în zona de log a UI-ului."""
        self.ui.textEdit_Log.append(message)
        print(f"[LOG]: {message}")  # Afișează și în consolă

    @Slot()
    def toggle_connection(self):
        """Pornește sau oprește conexiunea Modbus și citirea periodică."""
        if not self.is_connected:
            self.log_message(f"Se încearcă conectarea la {self.modbus_port} (ID Slave: {self.slave_addr})...")
            self.ui.label_Status.setText("Status: Conectare în curs...")
            QCoreApplication.processEvents()  # Forțează actualizarea UI

            if self.modbus_client.connect():
                self.log_message("Conectat cu succes.")
                self.ui.pushButton_Connect.setText("Deconectare")
                self.ui.label_Status.setText("Status: Conectat. Citire periodică activă.")
                self.is_connected = True
                self.read_timer.start(self.timer_interval_ms)  # Pornește citirea periodică
                self.update_data()  # Citește imediat prima dată
            else:
                self.log_message("Conectarea a eșuat. Verifică portul, cablul și parametrii Modbus.")
                self.ui.label_Status.setText("Status: Eroare de conectare.")
        else:
            self.read_timer.stop()  # Oprește citirea periodică
            self.modbus_client.disconnect()
            self.log_message("Deconectat.")
            self.ui.pushButton_Connect.setText("Conectare")
            self.ui.label_Status.setText("Status: Deconectat.")
            self.is_connected = False
            self.clear_labels()

    @Slot()
    def update_data(self):
        """Funcția apelată de timer pentru citirea și actualizarea datelor."""
        if not self.is_connected:
            return

        self.log_message("Se citesc datele (Curenți)...")
        self.ui.label_Status.setText("Status: Citire date...")
        currents = self.modbus_client.read_currents_float()

        if currents:
            # Afișează curenții
            self.ui.label_IL1.setText(f"{currents.get('L1', 0):.2f} A")
            self.ui.label_IL2.setText(f"{currents.get('L2', 0):.2f} A")
            self.ui.label_IL3.setText(f"{currents.get('L3', 0):.2f} A")
            self.log_message("Datele curenților actualizate.")
            self.ui.label_Status.setText("Status: OK")
        else:
            self.log_message("Eroare la citirea curenților. Încerc să re-conectez...")
            self.ui.label_Status.setText("Status: Eroare de citire.")
            # Dacă citirea eșuează de mai multe ori, oprește conexiunea (opțional)
            # self.toggle_connection()

        # TODO: Adaugă aici citirea și afișarea altor date (status, tensiuni etc.)
        # Ex: voltages = self.modbus_client.read_voltages_float()
        # self.ui.label_VLL.setText(f"{voltages.get('VLL1', 0):.2f} V")

    def clear_labels(self):
        """Resetează etichetele la valoarea implicită."""
        self.ui.label_IL1.setText("--- A")
        self.ui.label_IL2.setText("--- A")
        self.ui.label_IL3.setText("--- A")
        # self.ui.label_Status.setText("Status: ---")
        # TODO: Resetează și alte label-uri

    def closeEvent(self, event):
        """Asigură deconectarea la închiderea aplicației."""
        self.read_timer.stop()
        if self.modbus_client:
            self.modbus_client.disconnect()
        self.log_message("Aplicația se închide. Deconectarea finalizată.")
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
