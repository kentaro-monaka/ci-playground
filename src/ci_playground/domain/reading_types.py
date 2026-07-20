"""Reading クラスと SensorType の対応表."""

from ci_playground.domain.readings import (
    CurrentReading,
    TemperatureReading,
    VoltageReading,
)
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import SensorType

READING_TO_SENSOR_TYPE: dict[type[Reading], SensorType] = {
    TemperatureReading: SensorType.TEMPERATURE,
    VoltageReading: SensorType.VOLTAGE,
    CurrentReading: SensorType.CURRENT,
}

SENSOR_TYPE_TO_READING: dict[SensorType, type[Reading]] = {
    sensor_type: cls for cls, sensor_type in READING_TO_SENSOR_TYPE.items()
}
