"""SendReadings ユースケースのテスト."""

from datetime import datetime

from ci_playground.application.use_cases.send_readings import SendReadings
from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import DeviceId, SensorId
from ci_playground.infrastructure.memory.in_memory_reading_repository import (
    InMemoryFakeReadingRepository,
)
from ci_playground.infrastructure.memory.in_memory_reading_sender import (
    InMemoryFakeReadingSender,
)

_DEVICE_ID = DeviceId("dev-1")
_SENSOR_ID = SensorId("sen-temp")


def test_sends_latest_reading():
    repository = InMemoryFakeReadingRepository()
    repository.save(_DEVICE_ID, _SENSOR_ID, TemperatureReading(25.0), datetime.now())
    sender = InMemoryFakeReadingSender()

    SendReadings(repository, sender).execute(_DEVICE_ID, _SENSOR_ID)

    assert len(sender.sent) == 1
    assert sender.sent[0][:3] == (_DEVICE_ID, _SENSOR_ID, TemperatureReading(25.0))


def test_does_nothing_when_no_reading_recorded():
    repository = InMemoryFakeReadingRepository()
    sender = InMemoryFakeReadingSender()

    SendReadings(repository, sender).execute(_DEVICE_ID, _SENSOR_ID)

    assert sender.sent == []
