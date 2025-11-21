import sqlite3
import datetime
import logging

log = logging.getLogger('DataLogger')
log.setLevel(logging.INFO)


class DataLogger:
    def __init__(self, db_path='meter_readings.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self._setup_table()

    def connect(self):
        """Stabilește conexiunea la baza de date."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            log.info(f"Conexiune SQLite reușită la {self.db_path}")
        except sqlite3.Error as e:
            log.error(f"Eroare la conectarea la baza de date: {e}")

    def disconnect(self):
        """Închide conexiunea la baza de date."""
        if self.conn:
            self.conn.close()
            log.info("Conexiune SQLite închisă.")

    def _setup_table(self):
        """Creează tabela necesară pentru stocarea datelor Modbus."""
        if not self.conn: return


        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                timestamp TEXT,
                slave_id INTEGER,
                current_l1 REAL,
                voltage_l1 REAL,
                power_total REAL,
                frequency REAL
            )
        """)
        self.conn.commit()
        log.info("Tabela 'readings' verificată/creată.")

    def log_reading(self, slave_id, data):
        """Înregistrează o citire Modbus în baza de date."""
        if not self.conn: return False

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute("""
                INSERT INTO readings VALUES (?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                slave_id,
                data.get('L1_I', 0.0),
                data.get('L1_U', 0.0),
                data.get('P_Total', 0.0),
                data.get('Frequency', 0.0)
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            log.error(f"Eroare la logarea datelor pentru ID {slave_id}: {e}")
            return False

    def get_historical_data(self, slave_id, start_time_str, end_time_str):
        """Recuperează datele istorice dintr-un interval de timp dat."""
        if not self.conn: return []

        query = """
            SELECT timestamp, current_l1, voltage_l1, power_total, frequency 
            FROM readings 
            WHERE slave_id = ? AND timestamp BETWEEN ? AND ? 
            ORDER BY timestamp
        """
        try:
            self.cursor.execute(query, (slave_id, start_time_str, end_time_str))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            log.error(f"Eroare la citirea datelor istorice pentru ID {slave_id}: {e}")
            return []