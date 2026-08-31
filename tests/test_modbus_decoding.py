"""
Testes unitários para o módulo de decodificação e cliente de qualidade da água (Modbus-RTU).
"""

import math
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Adiciona o diretório src ao path de import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from water_quality_modbus import WaterQualityProbeClient, ProbeReading


class TestWaterQualityModbus(unittest.TestCase):
    """Bateria de testes unitários para a decodificação IEEE 754 e validação de sensores."""

    def test_float32_word_swap_roundtrip(self):
        """Valida a codificação e decodificação de float32 com word-swap (Mid-Big Endian)."""
        test_values = [0.0, 25.4, -1.8, 1413.0, 760.5, 8.45]
        for val in test_values:
            reg_high, reg_low = WaterQualityProbeClient.encode_float32(val)
            decoded = WaterQualityProbeClient.decode_float32(reg_high, reg_low)
            self.assertTrue(
                math.isclose(val, decoded, rel_tol=1e-5),
                f"Valor esperado {val} difere do decodificado {decoded}"
            )

    def test_known_float_representation(self):
        """Valida representação exata de 25.0 graus Celsius conforme protocolo da sonda."""
        # 25.0 float IEEE 754 em hex: 0x41C80000
        # Com word swap: reg[0] = 0x0000, reg[1] = 0x41C8 (16840 dec)
        val = WaterQualityProbeClient.decode_float32(0x0000, 0x41C8)
        self.assertAlmostEqual(val, 25.0, places=4)

    def test_validate_reading_valid_cases(self):
        """Garante que leituras em faixas ambientais normais sejam aceitas."""
        is_valid, msg = WaterQualityProbeClient.validate_reading(
            temp=23.5,
            cond=150.0,
            tdg=765.0,
            ldo=7.8
        )
        self.assertTrue(is_valid)
        self.assertEqual(msg, "OK")

    def test_validate_reading_out_of_bounds(self):
        """Garante que leituras absurdas (sonda fora da água / falha de eletrodo) sejam sinalizadas."""
        # Temperatura de 100°C em corpo d'água superficial ou condutividade negativa
        is_valid, msg = WaterQualityProbeClient.validate_reading(
            temp=95.0,
            cond=-10.0,
            tdg=2500.0,
            ldo=45.0
        )
        self.assertFalse(is_valid)
        self.assertIn("Temperatura fora da faixa", msg)
        self.assertIn("Condutividade fora da faixa", msg)
        self.assertIn("TDG fora da faixa", msg)
        self.assertIn("LDO fora da faixa", msg)

    def test_mock_read_all_parameters_success(self):
        """Testa o fluxo de leitura completa com mock do cliente serial."""
        client = WaterQualityProbeClient(port="MOCK_PORT")
        client.client = MagicMock()

        # Mock da resposta de registradores Modbus
        def mock_read_registers(address, count, **kwargs):
            mock_resp = MagicMock()
            mock_resp.isError.return_value = False
            if address == WaterQualityProbeClient.REG_TEMPERATURE:
                mock_resp.registers = [0x0000, 0x41C8]  # 25.0 °C
            elif address == WaterQualityProbeClient.REG_CONDUCTIVITY:
                mock_resp.registers = [0x0000, 0x447A]  # 1000.0 uS/cm
            elif address == WaterQualityProbeClient.REG_TDG:
                mock_resp.registers = [0x0000, 0x443E]  # 760.0 mmHg
            elif address == WaterQualityProbeClient.REG_LDO:
                mock_resp.registers = [0x0000, 0x4100]  # 8.0 mg/L
            else:
                mock_resp.registers = [0, 0]
            return mock_resp

        client.client.read_holding_registers.side_effect = mock_read_registers

        reading = client.read_all_parameters()
        self.assertTrue(reading.is_valid)
        self.assertAlmostEqual(reading.temperature_c, 25.0, places=2)
        self.assertAlmostEqual(reading.conductivity_us_cm, 1000.0, places=1)
        self.assertAlmostEqual(reading.tdg_mmhg, 760.0, places=1)
        self.assertAlmostEqual(reading.ldo_mg_l, 8.0, places=1)

    def test_mock_communication_failure_resilience(self):
        """Garante resiliência quando o transceptor Modbus reporta erro de timeout/comunicação."""
        client = WaterQualityProbeClient(port="MOCK_PORT")
        client.client = MagicMock()

        mock_error_resp = MagicMock()
        mock_error_resp.isError.return_value = True
        client.client.read_holding_registers.return_value = mock_error_resp

        reading = client.read_all_parameters()
        self.assertFalse(reading.is_valid)
        self.assertIn("Sem resposta da sonda", reading.status_message)
        self.assertIsNone(reading.temperature_c)


if __name__ == "__main__":
    unittest.main()
