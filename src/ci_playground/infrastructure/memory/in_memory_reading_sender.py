"""インメモリーに保存する Fake の reading sender."""

from datetime import datetime

from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import DeviceId, SensorId


class InMemoryFakeReadingSender:
    """メモリ上の計測値を送信する Fake."""

    def __init__(self) -> None:
        self.sent: list[tuple[DeviceId, SensorId, Reading, datetime]] = []

    def send(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
        reading: Reading,
        recorded_at: datetime,
    ) -> None:
        """Reading を1件送信する."""
        self.sent.append((device_id, sensor_id, reading, recorded_at))
