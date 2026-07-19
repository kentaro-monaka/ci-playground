"""インメモリーに保存する Fake の bus."""

from ci_playground.application.ports.field_bus import FieldBusError
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import SensorId, SetpointId


class InMemoryFakeFieldBus:
    """setpoint をメモリ上の辞書 に保存・取得する Fake."""

    def __init__(
        self, readings: dict[SensorId, Reading], setpoint_ids: set[SetpointId]
    ) -> None:
        self._readings = dict(readings)
        self._setpoints: dict[SetpointId, float] = {}
        self._setpoint_ids = set(setpoint_ids)

    def write_setpoint(
        self,
        setpoint_id: SetpointId,
        value: float,
    ) -> None:
        """Setpoint を1件保存する."""
        # オブジェクトのまま1件追加するだけ（分解しない）
        if setpoint_id not in self._setpoint_ids:
            raise FieldBusError(f"未登録の setpoint id です: {setpoint_id}")
        self._setpoints[setpoint_id] = value

    def read_reading(
        self,
        sensor_id: SensorId,
    ) -> Reading:
        """Reading を1件取得する."""
        if sensor_id not in self._readings:
            raise FieldBusError(f"未登録の sensor id です: {sensor_id}")
        return self._readings[sensor_id]

    def read_setpoint(
        self,
        setpoint_id: SetpointId,
    ) -> float:
        """Setpoint を1件取得する."""
        if setpoint_id not in self._setpoint_ids:
            raise FieldBusError(f"未登録の setpoint id です: {setpoint_id}")
        return self._setpoints.get(setpoint_id, 0.0)
