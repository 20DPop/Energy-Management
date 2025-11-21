import sqlite3
import random
from datetime import datetime, timedelta

# Configurare
DB_NAME = 'meter_readings.db'
DAYS_BACK = 7  # Câte zile de istoric să generăm
INTERVAL_MINUTES = 15  # Intervalul dintre citiri
SLAVE_IDS = range(1, 11)  # ID-urile de la 1 la 10


def seed_database():
    # Conectare la baza de date
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ne asigurăm că tabela există (în caz că rulezi scriptul înainte să pornești aplicația)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            timestamp TEXT,
            slave_id INTEGER,
            current_l1 REAL,
            voltage_l1 REAL,
            power_total REAL,
            frequency REAL
        )
    """)

    # Calculăm timpul de start și timpul de final
    end_time = datetime.now()
    start_time = end_time - timedelta(days=DAYS_BACK)

    current_time = start_time
    total_records = 0

    print(f"Generare date de la {start_time} până la {end_time}...")

    while current_time <= end_time:
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        for slave_id in SLAVE_IDS:
            # Generăm valori random dar plauzibile

            # Voltaj: variații mici în jur de 230V
            voltage = round(random.uniform(225.0, 235.0), 1)

            # Curent: variații între 0.5A și 15A (simulăm consum variabil)
            # Putem simula un consum mai mare ziua și mai mic noaptea
            hour = current_time.hour
            if 8 <= hour <= 18:
                current = round(random.uniform(5.0, 15.0), 2)  # Ziua
            else:
                current = round(random.uniform(0.5, 4.0), 2)  # Noaptea

            # Factor de putere aproximat pentru calcul
            pf = random.uniform(0.85, 0.99)

            # Puterea aproximată (P = U * I * PF / 1000 pentru kW)
            power = round((voltage * current * pf) / 1000.0, 3)

            # Frecvența: foarte stabilă în jur de 50Hz
            freq = round(random.uniform(49.9, 50.1), 2)

            # Inserare în baza de date
            # Ordinea coloanelor conform data_logger.py:
            # timestamp, slave_id, current_l1, voltage_l1, power_total, frequency
            cursor.execute("""
                INSERT INTO readings VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp_str, slave_id, current, voltage, power, freq))

            total_records += 1

        # Avansăm cu intervalul stabilit
        current_time += timedelta(minutes=INTERVAL_MINUTES)

    conn.commit()
    conn.close()
    print(f"Gata! Au fost inserate {total_records} înregistrări în '{DB_NAME}'.")


if __name__ == "__main__":
    seed_database()