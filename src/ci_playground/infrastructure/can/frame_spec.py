"""CAN フレーム割り当ての定義."""

from dataclasses import dataclass

from ci_playground.domain.values import SensorType


@dataclass(frozen=True)
class FrameSpec:
    """CAN フレーム1つの割り当て（IDとスケール）."""

    broadcast_id: int
    command_id: int | None = None
    scale: float = 1.0
    sensor_type: SensorType | None = None
