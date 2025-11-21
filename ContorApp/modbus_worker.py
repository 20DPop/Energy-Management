import logging
import time
from PySide6.QtCore import QObject, Signal, Slot
from modbus_client import ContorModbusClient

log = logging.getLogger('ModbusWorker')
log.setLevel(logging.INFO)


class ModbusWorker(QObject):
    # Folosim object pentru a evita eroarea Shiboken
    cycle_finished = Signal(object)
    log_message = Signal(str)

    def __init__(self, port, slave_ids, interval_ms):
        super().__init__()
        self.modbus_client = ContorModbusClient(port=port)
        self.slave_ids = slave_ids
        self.interval_ms = interval_ms
        self._is_running = False
        self.is_busy = False

        # --- LOGICĂ SMART SKIP AVANSATĂ ---
        self.dead_meters_cooldown = {}  # {id: timestamp_deblocare}
        self.failure_counts = {}  # {id: numar_erori_consecutive}

        # Configurare Toleranță
        self.COOLDOWN_SECONDS = 30  # Redus la 30 secunde (mai prietenos)
        self.MAX_FAILURES = 1  # Acceptăm 2 erori înainte de a da Skip
        # ----------------------------------

    @Slot()
    def start_polling(self):
        """Se apelează când pornești timer-ul / apeși Conectare."""
        log.info("Worker-ul pornește...")

        # --- RESETĂM STATUSURILE LA PORNIRE ---
        # Astfel, dacă dai Deconectare -> Conectare, toate contoarele au o șansă nouă
        self.dead_meters_cooldown.clear()
        self.failure_counts.clear()

        if not self.modbus_client.connect():
            self.log_message.emit("Eroare Worker: Nu s-a putut conecta la portul Modbus.")

        self._is_running = True
        # Putem rula un ciclu imediat, sau așteptăm timer-ul.
        # De obicei e mai safe să așteptăm timer-ul din Main.

    @Slot()
    def stop_polling(self):
        self._is_running = False
        if self.modbus_client:
            self.modbus_client.disconnect()

    @Slot()
    def run_read_cycle(self):
        if not self._is_running:
            return

        if self.is_busy:
            log.warning("Worker ocupat! Se sare peste acest ciclu.")
            return

        self.is_busy = True
        try:
            # log.info("--- Început ciclu ---")
            all_results = {}
            current_time = time.time()

            for sid in self.slave_ids:
                if not self._is_running:
                    break

                # 1. LOGICĂ SMART SKIP
                if sid in self.dead_meters_cooldown:
                    retry_time = self.dead_meters_cooldown[sid]
                    if current_time < retry_time:
                        all_results[sid] = {"status": "Skipped (Offline)"}
                        continue
                    else:
                        del self.dead_meters_cooldown[sid]
                        # Resetăm contorul la reîncercare
                        self.failure_counts[sid] = 0
                        log.info(f"Contor ID {sid}: Cooldown expirat. Se reîncearcă...")

                # 2. CITIRE SECVENȚIALĂ (Curenți APOI Tensiuni)

                # Pasul A: Curenți
                currents = self.modbus_client.read_currents_float(sid)

                if currents:
                    # Dacă curenții sunt OK, încercăm și tensiunile
                    voltages = self.modbus_client.read_voltages_float(sid)

                    if voltages:
                        # --- SUCCES COMPLET ---
                        self.failure_counts[sid] = 0
                        all_results[sid] = {
                            "status": "OK",
                            "currents": currents,
                            "voltages": voltages
                        }
                    else:
                        # Curenți OK, dar Tensiuni Eșec -> E o problemă
                        self._handle_failure(sid, all_results)
                else:
                    # Curenți Eșec -> Totul Eșec
                    self._handle_failure(sid, all_results)

        finally:
            self.is_busy = False

        self.cycle_finished.emit(all_results)

    def _handle_failure(self, sid, all_results):
        """Gestionează contorul de erori și cooldown-ul."""
        fails = self.failure_counts.get(sid, 0) + 1
        self.failure_counts[sid] = fails

        if fails >= self.MAX_FAILURES:
            self._mark_as_dead(sid)
            all_results[sid] = {"status": "Skipped (Offline)"}
        else:
            all_results[sid] = {"status": "Eroare"}
    def _mark_as_dead(self, slave_id):
        """Activează cooldown-ul."""
        retry_timestamp = time.time() + self.COOLDOWN_SECONDS
        self.dead_meters_cooldown[slave_id] = retry_timestamp
        msg = f"ID {slave_id}: {self.MAX_FAILURES} erori consecutive. Ignorat {self.COOLDOWN_SECONDS}s."
        log.warning(msg)
        self.log_message.emit(msg)