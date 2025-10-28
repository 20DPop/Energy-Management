# modbus_client.py
# Folosim ModbusSerialClient deoarece comunicarea RTU se face prin port serial (COM)
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import logging

# Configurare logging pentru a vedea ce se întâmplă
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)  # Schimbă în DEBUG pentru mai multe detalii


class ContorModbusClient:
    def __init__(self, port, baudrate=19200, parity='E', stopbits=1, slave_address=2):
        """Initializează clientul Modbus RTU."""
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.slave_address = slave_address
        self.client = None
        log.info(f"Client Modbus inițializat pentru portul {port} la {baudrate} baud (Slave ID: {slave_address}).")

    def connect(self):
        """Stabilește conexiunea Modbus. Elimină 'method' pentru ModbusSerialClient."""
        if self.client and self.client.is_socket_open():
            log.info("Clientul este deja conectat.")
            return True

        # ModbusSerialClient nu are nevoie de 'method=rtu'
        self.client = ModbusClient(port=self.port,
                                   baudrate=self.baudrate,
                                   parity=self.parity,
                                   stopbits=self.stopbits,
                                   timeout=1)  # Timeout de 1 secundă
        try:
            connection = self.client.connect()
            if connection:
                log.info("Conexiune Modbus RTU reușită.")
                return True
            else:
                log.error(f"Conexiunea Modbus RTU a eșuat. Verifică portul {self.port} și cablul.")
                self.client = None
                return False
        except Exception as e:
            log.error(f"Eroare la conectare: {e}")
            self.client = None
            return False

    def disconnect(self):
        """Închide conexiunea Modbus."""
        if self.client:
            self.client.close()
            log.info("Conexiune Modbus închisă.")
            self.client = None

    def read_currents_float(self):
        """Citește curenții IL1, IL2, IL3 ca float (presupunând format IEEE float)."""
        if not self.client or not self.client.is_socket_open():
            log.warning("Clientul nu este conectat sau conexiunea a fost pierdută.")
            return None

        try:
            # Adresa 404611 devine 4610 în notația 0-based
            address = 4610
            count = 6  # Citim 3 valori float de 32 de biți (3 * 2 regiștri = 6)

            # CORECȚIE FINALĂ: Dacă eroarea este 'takes 2 positional arguments but 4 were given',
            # înseamnă că parametrul slave trebuie să fie keyword argument, NU pozițional.
            # read_input_registers(address, count, *, slave=slave_id)

            # Încercăm read_input_registers (func code 04)
            rr = self.client.read_input_registers(address, count, slave=self.slave_address)

            if rr.isError():
                log.error(f"Eroare la citirea registrelor de input: {rr}. Încercăm holding registers...")

                # Aplicăm aceeași corecție pentru holding registers
                rr = self.client.read_holding_registers(address, count, slave=self.slave_address)

                if rr.isError():
                    log.error(f"Eroare la citirea registrelor holding: {rr}")
                    return None

            # Decodificăm valorile float (IEEE 754)
            # Presupunem Big Endian (Word Order = High Register First)
            decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, byteorder=Endian.Big, wordorder=Endian.Big)

            current_l1 = decoder.decode_32bit_float()
            current_l2 = decoder.decode_32bit_float()
            current_l3 = decoder.decode_32bit_float()

            log.info(f"Curenți citiți: L1={current_l1:.2f} A, L2={current_l2:.2f} A, L3={current_l3:.2f} A")
            return {"L1": current_l1, "L2": current_l2, "L3": current_l3}

        except ConnectionException:
            log.error("Conexiunea a fost pierdută în timpul citirii (ConnectionException).")
            self.disconnect()
            return None
        except Exception as e:
            log.error(f"Eroare neașteptată la citirea curenților: {e}")
            return None
