import logging
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

logging.basicConfig()
log = logging.getLogger('ContorModbusClient')
log.setLevel(logging.INFO)


class ContorModbusClient:
    def __init__(self, port, baudrate=19200, parity='E', stopbits=1):
        """Initializează clientul Modbus RTU (fără adresă slave fixă)."""
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.client = None
        log.info(f"Client Modbus inițializat pentru portul {port} la {baudrate} baud.")

    def connect(self):
        """Stabilește conexiunea la portul serial."""
        if self.client and self.client.is_socket_open():
            log.info("Clientul este deja conectat.")
            return True

        self.client = ModbusClient(method='rtu',
                                   port=self.port,
                                   baudrate=self.baudrate,
                                   parity=self.parity,
                                   stopbits=self.stopbits,
                                   timeout=0.5)  # Timeout de 1 secundă e suficient
        try:
            connection = self.client.connect()
            if connection:
                log.info("Conexiune Modbus RTU reușită.")
                return True
            else:
                log.error("Conexiunea Modbus RTU a eșuat. Verifică setările fizice.")
                self.client = None
                return False
        except Exception as e:
            log.error(f"Eroare la conectare: {e}")
            self.client = None
            return False

    def disconnect(self):
        """Închide portul serial."""
        if self.client:
            self.client.close()
            log.info("Conexiune Modbus închisă.")
            self.client = None

    def _read_registers(self, address, count, slave_address, description):
        """Funcție utilitară generală pentru citirea regiștrilor, cu reconectare automată."""

        # --- MODIFICAREA CHEIE: AUTO-RECONNECT ---
        # Verificăm dacă portul este deschis ÎNAINTE de a încerca să citim.
        if not self.client or not self.client.is_socket_open():
            log.warning(f"ID {slave_address}: Portul este închis. Se încearcă reconectarea...")
            # Încercăm să redeschidem portul
            if not self.connect():
                log.error(f"ID {slave_address}: Reconectarea a eșuat. Se anulează citirea.")
                return None
            log.info(f"ID {slave_address}: Reconectare reușită.")
        # --- SFÂRȘIT MODIFICARE ---

        try:
            # Citim folosind adresa slave specificată (unit)
            print(f"Citire {description} de la contor ID {slave_address}, adresă {address}, count {count}")
            rr = self.client.read_input_registers(address, count, unit=slave_address)

            if rr.isError():
                log.warning(f"Contor ID {slave_address}: FC04 eșuat, se încearcă FC03...")
                rr = self.client.read_holding_registers(address, count, unit=slave_address)

                if rr.isError():
                    log.error(f"Contor ID {slave_address}: NU RĂSPUNDE la citirea {description}: {rr}")
                    # Biblioteca va închide portul aici, dar e OK.
                    # Următorul apel (pt ID 3) îl va redeschide.
                    return None

            return rr.registers

        except ConnectionException as e:
            log.error(f"Contor ID {slave_address}: Eroare de conexiune (Timeout) la citirea {description}: {e}.")
            return None
        except Exception as e:
            log.error(f"Contor ID {slave_address}: Eroare generală la citirea {description}: {e}")
            return None

    def read_currents_float(self, slave_address):
        """Citește curenții IL1, IL2, IL3 (404611 => 4610 0-based)."""
        # Citim 6 regiștri (3 float-uri)
        registers = self._read_registers(4610, 6, slave_address, "Curenți")

        if registers:
            try:
                decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)
                data = {}
                data['L1'] = decoder.decode_32bit_float()
                data['L2'] = decoder.decode_32bit_float()
                data['L3'] = decoder.decode_32bit_float()
                return data
            except Exception as e:
                log.error(f"Contor ID {slave_address}: Eroare decodare curenți: {e}")
        return None

    def read_voltages_float(self, slave_address):
        """Citește tensiunile L-L (404623 => 4622 0-based)."""
        # Citim 6 regiștri (3 float-uri)
        registers = self._read_registers(4622, 6, slave_address, "Tensiuni L-L")

        if registers:
            try:
                decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)
                data = {}
                data['L1L2'] = decoder.decode_32bit_float()
                data['L2L3'] = decoder.decode_32bit_float()
                data['L3L1'] = decoder.decode_32bit_float()
                return data
            except Exception as e:
                log.error(f"Contor ID {slave_address}: Eroare decodare tensiuni: {e}")
        return None

    def read_meter_data_optimized(self, slave_address):
        """
        Citește Curenții (I), Tensiunile Fază-Nul (L-N) și Tensiunile Linie-Linie (L-L).
        Adresa Start: 4610
        Total Count: 18 regiștri
        """
        start_addr = 4610
        count = 18

        registers = self._read_registers(start_addr, count, slave_address, "Date Complete (I + U_LN + U_LL)")

        if not registers:
            return None

        data = {}
        try:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)

            # 1. Curenți (4610-4615)
            data['L1_I'] = decoder.decode_32bit_float()
            data['L2_I'] = decoder.decode_32bit_float()
            data['L3_I'] = decoder.decode_32bit_float()

            # 2. Tensiuni L-N (4616-4621) - ACUM LE CITIM!
            data['L1_N'] = decoder.decode_32bit_float()
            data['L2_N'] = decoder.decode_32bit_float()
            data['L3_N'] = decoder.decode_32bit_float()

            # 3. Tensiuni L-L (4622-4627)
            data['L1L2_U'] = decoder.decode_32bit_float()
            data['L2L3_U'] = decoder.decode_32bit_float()
            data['L3L1_U'] = decoder.decode_32bit_float()

            return data

        except Exception as e:
            log.error(f"Contor ID {slave_address}: Eroare decodare bloc: {e}")
            return None
    def read_meter_data_optimized(self, slave_address):
        """
        Citește Curenții și Tensiunile într-o SINGURĂ tranzacție.
        Adresa Start: 4610 (Curenți)
        Adresa Final: 4627 (Ultimul registru Tensiuni)
        Total Count: 18 regiștri
        """
        start_addr = 4610
        count = 18  # 6 (curenți) + 6 (gap) + 6 (tensiuni)

        # Folosim funcția _read_registers existentă
        registers = self._read_registers(start_addr, count, slave_address, "Date Complete (I+U)")

        if not registers:
            return None

        data = {}
        try:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)

            # 1. Decodificăm Curenții (primii 6 regiștri / 12 bytes)
            data['L1_I'] = decoder.decode_32bit_float()
            data['L2_I'] = decoder.decode_32bit_float()
            data['L3_I'] = decoder.decode_32bit_float()

            # 2. Sărim peste "gaura" de date (următorii 6 regiștri / 12 bytes)
            decoder.skip_bytes(12)

            # 3. Decodificăm Tensiunile (următorii 6 regiștri / 12 bytes)
            data['L1L2_U'] = decoder.decode_32bit_float()
            data['L2L3_U'] = decoder.decode_32bit_float()
            data['L3L1_U'] = decoder.decode_32bit_float()

            return data

        except Exception as e:
            log.error(f"Contor ID {slave_address}: Eroare decodare bloc: {e}")
            return None
