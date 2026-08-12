"""PublishReadings ユースケースのテスト."""

from datetime import datetime

from ci_playground.application.use_cases.publish_readings import PublishReadings
from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import DeviceId, SensorId
from ci_playground.infrastructure.memory.in_memory_reading_repository import (
    InMemoryFakeReadingRepository,
)
from ci_playground.infrastructure.memory.in_memory_server_bus import (
    InMemoryFakeServerBus,
)

_DEVICE_ID = DeviceId("dev-1")
_SENSOR_ID = SensorId("sen-temp")


def test_publishes_latest_reading():
    repository = InMemoryFakeReadingRepository()
    repository.save(_DEVICE_ID, _SENSOR_ID, TemperatureReading(25.0), datetime.now())
    bus = InMemoryFakeServerBus(known_sensors={_SENSOR_ID}, setpoints={})

    PublishReadings(repository, bus).execute(_DEVICE_ID, _SENSOR_ID)

    assert bus.published == [(_SENSOR_ID, TemperatureReading(25.0))]


def test_does_nothing_when_no_reading_recorded():
    repository = InMemoryFakeReadingRepository()
    bus = InMemoryFakeServerBus(known_sensors={_SENSOR_ID}, setpoints={})

    PublishReadings(repository, bus).execute(_DEVICE_ID, _SENSOR_ID)

    assert bus.published == []
