"""1件のセンサの最新計測値を外部サーバへ送信するユースケース."""

from datetime import datetime

from ci_playground.application.ports.reading_repository import ReadingRepository
from ci_playground.application.ports.reading_sender import ReadingSender
from ci_playground.domain.values import DeviceId, SensorId


class SendReadings:
    """DB上の最新計測値を1件、外部サーバに送信する."""

    def __init__(
        self,
        repository: ReadingRepository,
        sender: ReadingSender,
    ) -> None:
        self._repository = repository
        self._sender = sender

    def execute(self, device_id: DeviceId, sensor_id: SensorId) -> None:
        """最新計測値を送信する。未記録なら何もしない.

        Args:
            device_id: 対象機器の識別子.
            sensor_id: 対象センサの識別子.

        Raises:
            ReadingSendError: 送信に失敗した場合.
        """
        reading = self._repository.find_latest(device_id, sensor_id)
        if reading is None:
            return
        self._sender.send(device_id, sensor_id, reading, datetime.now())
