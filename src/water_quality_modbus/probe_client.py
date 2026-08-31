#!/usr/bin/env python3
"""
Cliente Modbus-RTU para Sondas de Qualidade da Água (Hydrolab MS-5 / In-Situ).

Implementa comunicação resiliente sobre RS-485 com decodificação de registradores de 32 bits
(padrão IEEE 754 float com inversão de registradores de 16 bits), reconexão automática,
checagem de plausibilidade físico-química e logging estruturado.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import logging
import struct
import time
from typing import Optional, Tuple, Dict, Any

# Compatibilidade com PyModbus 3.x e fallback para 2.x
try:
    from pymodbus.client import ModbusSerialClient
except ImportError:
    try:
        from pymodbus.client.sync import ModbusSerialClient  # type: ignore
    except ImportError:
        ModbusSerialClient = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class ProbeReading:
    """Representação estruturada dos parâmetros físico-químicos lidos da sonda."""
    temperature_c: Optional[float]
    conductivity_us_cm: Optional[float]
    tdg_mmhg: Optional[float]
    ldo_mg_l: Optional[float]
    timestamp_utc: str
    is_valid: bool
    status_message: str = "OK"

    def to_dict(self) -> Dict[str, Any]:
        """Converte a leitura em dicionário serializável."""
        return asdict(self)


class WaterQualityProbeClient:
    """Cliente para leitura de sondas multiparâmetros via protocolo Modbus-RTU."""

    # Mapeamento de registradores padrão da sonda (Holding Registers)
    REG_TEMPERATURE = 400
    REG_CONDUCTIVITY = 12
    REG_TDG = 24
    REG_LDO = 180

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 19200,
        parity: str = "E",
        stopbits: int = 1,
        bytesize: int = 8,
        unit_id: int = 0x02,
        timeout: float = 1.5,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.unit_id = unit_id
        self.timeout = timeout
        self.client: Optional[Any] = None

    def connect(self) -> bool:
        """Estabelece a conexão serial com o transceptor RS-485."""
        if ModbusSerialClient is None:
            raise RuntimeError("Biblioteca pymodbus não encontrada. Instale com: pip install pymodbus")

        try:
            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                parity=self.parity,
                stopbits=self.stopbits,
                bytesize=self.bytesize,
                timeout=self.timeout,
            )
            connected = self.client.connect()
            if connected:
                logger.info("Conexão serial estabelecida na porta %s (Baud=%d, Parity=%s)", self.port, self.baudrate, self.parity)
            else:
                logger.warning("Falha ao abrir a porta serial %s", self.port)
            return bool(connected)
        except Exception as exc:
            logger.error("Erro inesperado ao conectar à porta serial %s: %s", self.port, exc)
            return False

    def close(self) -> None:
        """Encerra a conexão serial."""
        if self.client:
            try:
                self.client.close()
                logger.info("Conexão serial com a sonda encerrada.")
            except Exception as exc:
                logger.debug("Erro ao fechar conexão: %s", exc)
            finally:
                self.client = None

    @staticmethod
    def decode_float32(reg_high: int, reg_low: int) -> float:
        """
        Decodifica dois registradores de 16 bits para float32 (IEEE 754).
        
        A sonda Hydrolab MS-5 / In-Situ utiliza representação Word-Swapped (Mid-Big Endian),
        onde reg_low contém a parte mais significativa do float e reg_high a menos significativa.
        """
        packed = struct.pack(">HH", reg_low, reg_high)
        val = struct.unpack(">f", packed)[0]
        return float(val)

    @staticmethod
    def encode_float32(value: float) -> Tuple[int, int]:
        """
        Codifica um float32 para o par de registradores de 16 bits com Word-Swap.
        Utilizado principalmente para testes unitários e calibração.
        """
        packed = struct.pack(">f", value)
        reg_low, reg_high = struct.unpack(">HH", packed)
        return reg_high, reg_low

    @staticmethod
    def validate_reading(
        temp: Optional[float],
        cond: Optional[float],
        tdg: Optional[float],
        ldo: Optional[float]
    ) -> Tuple[bool, str]:
        """
        Verifica a plausibilidade físico-química dos parâmetros lidos:
        - Temperatura: -2 °C a 60 °C (faixa hidrológica terrestre)
        - Condutividade: 0 a 100.000 uS/cm
        - TDG: 300 a 1.600 mmHg
        - LDO: 0 a 30 mg/L
        """
        errors = []
        if temp is not None and not (-2.0 <= temp <= 60.0):
            errors.append(f"Temperatura fora da faixa ({temp:.2f} °C)")
        if cond is not None and not (0.0 <= cond <= 100000.0):
            errors.append(f"Condutividade fora da faixa ({cond:.2f} uS/cm)")
        if tdg is not None and not (300.0 <= tdg <= 1600.0):
            errors.append(f"TDG fora da faixa ({tdg:.2f} mmHg)")
        if ldo is not None and not (0.0 <= ldo <= 30.0):
            errors.append(f"LDO fora da faixa ({ldo:.2f} mg/L)")

        if errors:
            return False, "; ".join(errors)
        return True, "OK"

    def read_parameter(self, address: int, count: int = 2) -> Optional[float]:
        """Lê um parâmetro de 32 bits em um endereço de holding register com tratamento de erro."""
        if not self.client:
            if not self.connect():
                return None

        try:
            # Compatibilidade pymodbus v3 (slave/unit)
            try:
                response = self.client.read_holding_registers(address=address, count=count, slave=self.unit_id)
            except TypeError:
                response = self.client.read_holding_registers(address=address, count=count, unit=self.unit_id)

            if response is None or response.isError():
                logger.warning("Falha na resposta Modbus para registrador %d (Slave %d)", address, self.unit_id)
                return None

            if len(response.registers) < 2:
                logger.warning("Registradores insuficientes recebidos para o endereço %d", address)
                return None

            return self.decode_float32(response.registers[0], response.registers[1])
        except Exception as exc:
            logger.error("Erro na leitura do registrador %d: %s", address, exc)
            self.close()  # Força reconexão na próxima tentativa
            return None

    def read_all_parameters(self) -> ProbeReading:
        """Realiza a leitura completa de todos os canais físico-químicos da sonda."""
        now_iso = datetime.now(timezone.utc).isoformat()

        temp = self.read_parameter(self.REG_TEMPERATURE)
        cond = self.read_parameter(self.REG_CONDUCTIVITY)
        tdg = self.read_parameter(self.REG_TDG)
        ldo = self.read_parameter(self.REG_LDO)

        has_any_data = any(x is not None for x in (temp, cond, tdg, ldo))
        if not has_any_data:
            return ProbeReading(
                temperature_c=None,
                conductivity_us_cm=None,
                tdg_mmhg=None,
                ldo_mg_l=None,
                timestamp_utc=now_iso,
                is_valid=False,
                status_message="Sem resposta da sonda (timeout/erro de comunicação)"
            )

        is_valid, msg = self.validate_reading(temp, cond, tdg, ldo)
        return ProbeReading(
            temperature_c=temp,
            conductivity_us_cm=cond,
            tdg_mmhg=tdg,
            ldo_mg_l=ldo,
            timestamp_utc=now_iso,
            is_valid=is_valid,
            status_message=msg
        )
