"""CollectReadings ユースケースのテスト."""

import pytest

from ci_playground.application.ports.field_bus import FieldBusError
from ci_playground.application.use_cases.collect_readings import CollectReadings
from ci_playground.domain.device import Device
from ci_playground.domain.readings import (
    CurrentReading,
    TemperatureReading,
    VoltageReading,
)
from ci_playground.domain.sensor import Sensor
from ci_playground.domain.values import DeviceId, Range, SensorId, SensorType
from ci_playground.infrastructure.memory.in_memory_field_bus import (
    InMemoryFakeFieldBus,
)
from ci_playground.infrastructure.memory.in_memory_reading_repository import (
    InMemoryFakeReadingRepository,
)

_READINGS = {
    SensorId("sen-temp"): TemperatureReading(25.0),
    SensorId("sen-volt"): VoltageReading(400.0),
    SensorId("sen-curr"): CurrentReading(10.0),
}


@pytest.fixture
def device():
    """センサ3本を持つ機器."""
    device = Device(id=DeviceId("dev-1"))
    device.attach_sensor(
        Sensor(SensorId("sen-temp"), SensorType.TEMPERATURE, Range(-20.0, 80.0))
    )
    device.attach_sensor(
        Sensor(SensorId("sen-volt"), SensorType.VOLTAGE, Range(0.0, 500.0))
    )
    device.attach_sensor(
        Sensor(SensorId("sen-curr"), SensorType.CURRENT, Range(-100.0, 100.0))
    )
    return device


@pytest.fixture
def repository():
    return InMemoryFakeReadingRepository()


def test_all_sensors_are_saved(device, repository):
    field_bus = InMemoryFakeFieldBus(readings=_READINGS, setpoint_ids=set())

    CollectReadings(field_bus, repository).execute(device)

    assert len(repository.records) == 3


def test_sensor_last_reading_is_updated(device, repository):
    field_bus = InMemoryFakeFieldBus(readings=_READINGS, setpoint_ids=set())

    CollectReadings(field_bus, repository).execute(device)

    assert device.find_sensor(SensorId("sen-temp")).last_reading == TemperatureReading(
        25.0
    )


def test_one_scan_shares_single_timestamp(device, repository):
    field_bus = InMemoryFakeFieldBus(readings=_READINGS, setpoint_ids=set())

    CollectReadings(field_bus, repository).execute(device)

    timestamps = {record.recorded_at for record in repository.records}
    assert len(timestamps) == 1


def test_read_failure_aborts_device(device, repository):
    partial = dict(_READINGS)
    del partial[SensorId("sen-volt")]
    field_bus = InMemoryFakeFieldBus(readings=partial, setpoint_ids=set())

    with pytest.raises(FieldBusError):
        CollectReadings(field_bus, repository).execute(device)
