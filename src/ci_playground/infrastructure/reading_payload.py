"""Reading を送信用 payload（dict）に変換する共通関数."""

from datetime import datetime

from ci_playground.domain.readings import (
    CurrentReading,
    TemperatureReading,
    VoltageReading,
)
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import DeviceId, SensorId, SensorType

_READING_TO_SENSOR_TYPE: dict[type[Reading], SensorType] = {
    TemperatureReading: SensorType.TEMPERATURE,
    VoltageReading: SensorType.VOLTAGE,
    CurrentReading: SensorType.CURRENT,
}


def reading_to_payload(
    device_id: DeviceId,
    sensor_id: SensorId,
    reading: Reading,
    recorded_at: datetime,
) -> dict[str, object]:
    """Reading を送信用の dict payload に変換する."""
    return {
        "device_id": device_id.value,
        "sensor_id": sensor_id.value,
        "type": _READING_TO_SENSOR_TYPE[type(reading)].value,
        "value": reading.value,
        "recorded_at": recorded_at.isoformat(),
    }
