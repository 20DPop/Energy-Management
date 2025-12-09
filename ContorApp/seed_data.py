import sqlite3
import datetime
import random

# Configurare
DB_PATH = 'meter_readings.db'
DAYS_BACK = 30
INTERVAL_MINUTES = 60  # O înregistrare la fiecare oră (pentru a nu umple DB prea tare)
METER_IDS = [1, 2]  # Vom genera date pentru contorul 1 și 2


def create_dummy_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Asigură-te că tabela există (în caz că rulezi scriptul pe curat)
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

        print(f"Generare date pentru ultimele {DAYS_BACK} zile...")

        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=DAYS_BACK)

        current_date = start_date
        records_count = 0

        while current_date <= end_date:
            timestamp_str = current_date.strftime("%Y-%m-%d %H:%M:%S")

            for slave_id in METER_IDS:
                # Generăm valori aleatorii dar plauzibile

                # Voltaj: Variatie in jurul a 230V (+/- 5V)
                voltage = round(random.uniform(225.0, 235.0), 1)

                # Curent: Variatie intre 0.5A si 15A (simulam consum variabil)
                # Mai mare ziua (8-20), mai mic noaptea
                hour = current_date.hour
                if 8 <= hour <= 20:
                    current = round(random.uniform(5.0, 15.0), 2)
                else:
                    current = round(random.uniform(0.5, 4.0), 2)

                # Putere: Aproximativ U * I / 1000 (kW) * factor de putere (0.9)
                power = round((voltage * current * 0.9) / 1000, 2)

                # Frecventa: 50Hz (+/- 0.1)
                freq = round(random.uniform(49.9, 50.1), 2)

                cursor.execute("""
                    INSERT INTO readings (timestamp, slave_id, current_l1, voltage_l1, power_total, frequency)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (timestamp_str, slave_id, current, voltage, power, freq))

                records_count += 1

            # Avansăm timpul
            current_date += datetime.timedelta(minutes=INTERVAL_MINUTES)

        conn.commit()
        conn.close()
        print(f"Succes! Au fost adăugate {records_count} înregistrări în '{DB_PATH}'.")

    except sqlite3.Error as e:
        print(f"Eroare la baza de date: {e}")


if __name__ == "__main__":
    create_dummy_data()