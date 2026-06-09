"""センサを表すエンティティ.

ID で識別し、type に応じた Reading のみを受け付ける。
"""

from dataclasses import dataclass

from ci_playground.domain.readings import (
    CurrentReading,
    TemperatureReading,
    VoltageReading,
)
from ci_playground.domain.values import Range, SensorId, SensorType

Reading = TemperatureReading | VoltageReading | CurrentReading
_TYPE_READING_MAP = {
    SensorType.TEMPERATURE: TemperatureReading,
    SensorType.VOLTAGE: VoltageReading,
    SensorType.CURRENT: CurrentReading,
}


@dataclass(eq=False)
class Sensor:
    """ID で識別される計測センサ.

    type に応じた Reading のみを record() で受け付ける（ID基準で等価）。

    Attributes:
        id: Device 内でローカルに一意なセンサ識別子.
        type: センサ種別（温度・電圧・電流）.
        allowed_range: 許容される計測値の範囲.
        last_reading: 直近に記録された計測値（未記録なら None）.
    """

    id: SensorId
    type: SensorType
    allowed_range: Range
    last_reading: Reading | None = None

    def record(self, reading: Reading) -> None:
        """センサに新しい計測値を記録する.

        Args:
            reading: 記録する計測値。type に対応する Reading クラスでなければならない。

        Raises:
            ValueError: reading の型がセンサ type に対応しない場合.
        """
        expected_class = _TYPE_READING_MAP[self.type]
        if not isinstance(reading, expected_class):
            raise ValueError(
                f"期待されるReadingクラスは {expected_class.__name__} ですが、"
                f"渡されたのは {type(reading).__name__} です"
            )
        self.last_reading = reading

    @property
    def is_anomalous(self) -> bool:
        """直近の計測値が許容範囲外かを判定.

        Returns:
            last_reading が None なら False、Range 外なら True.
        """
        if self.last_reading is None:
            return False
        return not self.allowed_range.contains(self.last_reading.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sensor):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
