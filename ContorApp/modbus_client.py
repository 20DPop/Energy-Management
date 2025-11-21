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
        if self.client and self.client.is_socket_open():
            log.info("Clientul este deja conectat.")
            return True

        self.client = ModbusClient(method='rtu',
                                   port=self.port,
                                   baudrate=self.baudrate,
                                   parity=self.parity,
                                   stopbits=self.stopbits,
                                   timeout=1.5)
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
        if self.client:
            self.client.close()
            log.info("Conexiune Modbus închisă.")
            self.client = None

    def _read_float_registers(self, address, count, slave_address, description):
        """Funcție utilitară pentru citirea regiștrilor float (IEEE 754)."""
        if not self.client or not self.client.is_socket_open():
            log.warning(f"Clientul nu este conectat.")
            return None

        try:
            # Citim folosind adresa slave specificată (unit)
            print(f"Citire {description} de la contor ID {slave_address}, adresă {address}, count {count}")
            rr = self.client.read_input_registers(address, count, unit=slave_address)
            print(rr)
            if rr.isError():
                rr = self.client.read_holding_registers(address, count, unit=slave_address)

                if rr.isError():
                    log.error(f"Contor ID {slave_address}: Eroare fatală la citirea {description}: {rr}")
                    return None

            return rr.registers

        except ConnectionException:
            log.error(f"Conexiunea Modbus a fost pierdută.")
            self.disconnect()
            return None
        except Exception as e:
            log.error(f"Contor ID {slave_address}: Eroare generală la citirea {description}: {e}")
            return None

    def read_currents_float(self, slave_address):
        """Citește curenții IL1, IL2, IL3 (404611 => 4610 0-based)."""
        registers = self._read_float_registers(4610, 6, slave_address, "Curenți")
        if registers:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)
            current_l1 = decoder.decode_32bit_float()
            current_l2 = decoder.decode_32bit_float()
            current_l3 = decoder.decode_32bit_float()
            print(f"Curenți citiți: L1={current_l1:.2f} A, L2={current_l2:.2f} A, L3={current_l3:.2f} A")
            return {"L1": current_l1, "L2": current_l2,
                    "L3": current_l3}
        return None

    def read_voltages_float(self, slave_address):
        """Citește tensiunile UL1, UL2, UL3 (404602 => 4601 0-based)."""
        registers = self._read_float_registers(4622, 6, slave_address, "Tensiuni")
        if registers:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)
            voltage_l1l2 = decoder.decode_32bit_float()
            voltage_l2l3 = decoder.decode_32bit_float()
            voltage_l3l1 = decoder.decode_32bit_float()

            print(
                f"Tensiuni L-L citite: L1-L2={voltage_l1l2:.2f} V, L2-L3={voltage_l2l3:.2f} V, L3-L1={voltage_l3l1:.2f} V")
            return {"L1L2": voltage_l1l2, "L2L3": voltage_l2l3, "L3L1": voltage_l3l1}
        return None

    def read_total_active_energy_kwh(self):
        """Citește energia activă totală (combinată) în kWh (format Fixed Point)."""
        address = 6262
        count = 2  # 1 valoare uint32 * 2 regiștri/valoare
        registers = self._read_registers(address, count)

        if registers is None:
            return None

        try:
            # Decodificăm valoarea uint32 (2 regiștri)
            # Presupunem Big Endian pentru Byte și Word Order.
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)
            total_kwh = decoder.decode_32bit_uint()

            # Aplicăm factorul de scalare (care e 1 în acest caz)
            # total_kwh = total_kwh / 1.0

            log.info(f"Energie activă totală citită: {total_kwh} kWh")
            return {"Total kWh": total_kwh}
        except Exception as e:
            log.error(f"Eroare la decodificarea energiei totale kWh: {e}")
            return None
    def read_powers_float(self, slave_address):
        """Citește Puterile (P total, Q total, P L1, P L2, P L3).
           ADRESE  (404701 => 4700 0-based pentru P total, 404711 pentru PL1)
        """
        #  404701 pentru P Total, 404703 pentru Q Total
        # Citim P Total (4700), Q Total (4702), Frecvență (4800)
        address = 4650  # P Total
        count = 4  # 2 float * 2 = 4 regiștri
        registers = self._read_float_registers(address, count, slave_address, "P/Q Total")

        data = {}
        if registers:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)
            data["P_Total"] = decoder.decode_32bit_float()
            data["Q_Total"] = decoder.decode_32bit_float()

        # Citim puterile pe fază (PL1, PL2, PL3) -  404711 (4710)
        # registers_phase = self._read_float_registers(4710, 6, slave_address, "P Fază")
        # if registers_phase:
        #     decoder = BinaryPayloadDecoder.fromRegisters(registers_phase, byteorder=Endian.Big, wordorder=Endian.Big)
        #     data["PL1"] = decoder.decode_32bit_float()
        #     data["PL2"] = decoder.decode_32bit_float()
        #     data["PL3"] = decoder.decode_32bit_float()

        return data if (data.get("P_Total") is not None) else None

    def read_system_params(self, slave_address):
        """Citește Frecvența și Factorul de Putere (Presupunem 404801 => 4800 0-based)."""
        address = 4660
        count = 4  # Frecvență (float), PF Total (float)
        registers = self._read_float_registers(address, count, slave_address, "Frecvență/PF")

        if registers:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)
            freq = decoder.decode_32bit_float()
            pf_total = decoder.decode_32bit_float()
            return {"Frequency": freq, "PF_Total": pf_total}
        return None
