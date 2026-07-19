"""Modbus レジスタ割り当ての共通定義."""

from dataclasses import dataclass

from ci_playground.domain.values import SensorType


@dataclass(frozen=True)
class RegisterSpec:
    """Modbus レジスタ1つの割り当て（番地とスケール）."""

    address: int
    scale: float = 1.0
    sensor_type: SensorType | None = None
