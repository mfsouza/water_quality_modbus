#!/usr/bin/env python3
"""
Script de Aquisição de Dados de Qualidade da Água via Modbus-RTU (RS-485).
Sondas compatíveis: Hydrolab MS-5, In-Situ Aqua TROLL / MP TROLL.
"""

import argparse
import logging
import os
import sys
import time

# Permite execução direta adicionando o diretório 'src' ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from water_quality_modbus import WaterQualityProbeClient, ProbeReading


def configure_logging(verbose: bool = False) -> None:
    """Configura formato padronizado de logs."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Leitor Modbus-RTU para Sondas de Qualidade da Água (Hydrolab MS-5 / In-Situ)"
    )
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Porta serial (ex: /dev/ttyUSB0 ou COM3)")
    parser.add_argument("--baudrate", type=int, default=19200, help="Baudrate da comunicação (padrão: 19200)")
    parser.add_argument("--unit-id", type=int, default=0x02, help="Endereço escravo Modbus da sonda (padrão: 2)")
    parser.add_argument("--interval", type=float, default=1.0, help="Intervalo de leitura em segundos (padrão: 1.0s)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Habilitar logs detalhados de debug")
    args = parser.parse_args()

    configure_logging(args.verbose)
    logger = logging.getLogger("WaterQualityAcquisition")
    logger.info("Iniciando leitor de sonda em %s (Baud=%d, UnitID=%d)...", args.port, args.baudrate, args.unit_id)

    client = WaterQualityProbeClient(
        port=args.port,
        baudrate=args.baudrate,
        unit_id=args.unit_id,
        parity="E",
        stopbits=1,
        bytesize=8,
    )

    try:
        while True:
            reading: ProbeReading = client.read_all_parameters()
            if reading.is_valid:
                temp_str = f"{reading.temperature_c:.2f} °C" if reading.temperature_c is not None else "N/A"
                cond_str = f"{reading.conductivity_us_cm:.1f} uS/cm" if reading.conductivity_us_cm is not None else "N/A"
                tdg_str = f"{reading.tdg_mmhg:.1f} mmHg" if reading.tdg_mmhg is not None else "N/A"
                ldo_str = f"{reading.ldo_mg_l:.2f} mg/L" if reading.ldo_mg_l is not None else "N/A"

                logger.info(
                    "Leitura [%s]: Temp=%s | Cond=%s | TDG=%s | LDO=%s",
                    reading.timestamp_utc, temp_str, cond_str, tdg_str, ldo_str
                )
            else:
                logger.warning("Falha na aquisição ou dado inválido: %s", reading.status_message)

            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Encerrando aquisição por interrupção do usuário (Ctrl+C).")
    finally:
        client.close()


if __name__ == "__main__":
    main()
