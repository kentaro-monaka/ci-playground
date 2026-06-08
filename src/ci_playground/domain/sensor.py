from dataclasses import dataclass
from ci_playground.domain.values import SensorId, SensorType, Range
from ci_playground.domain.readings import (
    TemperatureReading,
    VoltageReading,
    CurrentReading,
)

Reading = TemperatureReading | VoltageReading | CurrentReading
_TYPE_READING_MAP = {
    SensorType.TEMPERATURE: TemperatureReading,
    SensorType.VOLTAGE: VoltageReading,
    SensorType.CURRENT: CurrentReading,
}


@dataclass(eq=False)
class Sensor:
    id: SensorId
    type: SensorType
    allowed_range: Range
    last_reading: Reading | None = None

    def record(self, reading: Reading) -> None:
        expected_class = _TYPE_READING_MAP[self.type]
        if not isinstance(reading, expected_class):
            raise ValueError(
                f"期待されるReadingクラスは {expected_class.__name__} ですが、"
                f"渡されたのは {type(reading).__name__} です"
            )
        self.last_reading = reading

    @property
    def is_anomalous(self) -> bool:
        if self.last_reading is None:
            return False
        return not self.allowed_range.contains(self.last_reading.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sensor):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
