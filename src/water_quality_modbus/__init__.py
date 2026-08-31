"""
Pacote para comunicação serial Modbus-RTU com sondas de qualidade da água multiparâmetros (Hydrolab MS-5, In-Situ).
"""

from .probe_client import WaterQualityProbeClient, ProbeReading

__all__ = ["WaterQualityProbeClient", "ProbeReading"]
