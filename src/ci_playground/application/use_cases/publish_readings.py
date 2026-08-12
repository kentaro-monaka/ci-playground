"""1件のセンサの最新計測値をEMS向けに公開する."""

from ci_playground.application.ports.reading_repository import ReadingRepository
from ci_playground.application.ports.server_bus import ServerBus
from ci_playground.domain.values import DeviceId, SensorId


class PublishReadings:
    """DB上の最新計測値を1件、EMS向けに公開する."""

    def __init__(
        self,
        repository: ReadingRepository,
        server_bus: ServerBus,
    ) -> None:
        self._repository = repository
        self._server_bus = server_bus

    def execute(self, device_id: DeviceId, sensor_id: SensorId) -> None:
        """最新計測値を公開する、未記録なら何もしない.

        Args:
            device_id: 対象機器の識別子.
            sensor_id: 対象センサの識別子.

        Raises:
            ServerBusError: 公開に失敗した場合.
        """
        reading = self._repository.find_latest(device_id, sensor_id)
        if reading is None:
            return
        self._server_bus.publish_reading(sensor_id, reading)
