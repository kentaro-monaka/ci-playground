"""全センサの計測値を収集して記録するユースケース."""

from datetime import datetime

from ci_playground.application.ports.field_bus import FieldBus
from ci_playground.application.ports.reading_repository import ReadingRepository
from ci_playground.domain.device import Device


class CollectReadings:
    """Device の全センサをフィールドバスから読み、記録する."""

    def __init__(
        self,
        field_bus: FieldBus,
        repository: ReadingRepository,
    ) -> None:
        self._field_bus = field_bus
        self._repository = repository

    def execute(self, device: Device) -> None:
        """全センサを1巡し、読んだ値をセンサに記録して永続化する.

        1台の機器・1本の線を1周する。読み取りに失敗した場合はその機器を諦め、
        FieldBusError をそのまま送出する（複数機器を回すのは呼び出し元の責務）。

        Args:
            device: 対象の機器。センサの last_reading が更新される。

        Raises:
            FieldBusError: いずれかのセンサの読み取りに失敗した場合.
        """
        recorded_at = datetime.now()
        for sensor in device.sensors:
            reading = self._field_bus.read_reading(sensor.id)
            sensor.record(reading)
            self._repository.save(device.id, sensor.id, reading, recorded_at)
