"""インメモリーに保存する Fake の bus."""

from ci_playground.application.ports.server_bus import ServerBusError
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import SensorId, SetpointId


class InMemoryFakeServerBus:
    """setpoint をメモリ上の辞書 に保存・取得する Fake."""

    def __init__(
        self, known_sensors: set[SensorId], setpoints: dict[SetpointId, float]
    ) -> None:
        self._known_sensors = set(known_sensors)
        self._setpoints = dict(setpoints)

    def publish_reading(
        self,
        sensor_id: SensorId,
        reading: Reading,
    ) -> None:
        """Reading を1件サーバーに公開する."""
        if sensor_id not in self._known_sensors:
            raise ServerBusError(f"未登録の sensor id です: {sensor_id}")

    def read_setpoint(
        self,
        setpoint_id: SetpointId,
    ) -> float:
        """Setpoint を1件サーバーから取得する."""
        if setpoint_id not in self._setpoints:
            raise ServerBusError(f"未登録の setpoint id です: {setpoint_id}")
        return self._setpoints[setpoint_id]
