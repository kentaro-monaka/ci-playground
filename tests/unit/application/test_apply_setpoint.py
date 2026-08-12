"""ApplySetpoint ユースケースのテスト."""

from ci_playground.application.use_cases.apply_setpoint import ApplySetpoint
from ci_playground.domain.device import Device
from ci_playground.domain.values import DeviceId, Range, SetpointId
from ci_playground.infrastructure.memory.in_memory_field_bus import (
    InMemoryFakeFieldBus,
)
from ci_playground.infrastructure.memory.in_memory_server_bus import (
    InMemoryFakeServerBus,
)

_SETPOINT_ID = SetpointId("sp-power")


def _device_with_range(allowed_range: Range) -> Device:
    device = Device(id=DeviceId("dev-1"))
    device.setpoint_ranges[_SETPOINT_ID] = allowed_range
    return device


def test_accepts_value_within_range():
    device = _device_with_range(Range(0.0, 100.0))
    server_bus = InMemoryFakeServerBus(
        known_sensors=set(), setpoints={_SETPOINT_ID: 50.0}
    )
    field_bus = InMemoryFakeFieldBus(readings={}, setpoint_ids={_SETPOINT_ID})

    accepted = ApplySetpoint(server_bus, field_bus).execute(device, _SETPOINT_ID)

    assert accepted is True
    assert field_bus.read_setpoint(_SETPOINT_ID) == 50.0


def test_rejects_value_outside_range():
    device = _device_with_range(Range(0.0, 100.0))
    server_bus = InMemoryFakeServerBus(
        known_sensors=set(), setpoints={_SETPOINT_ID: 150.0}
    )
    field_bus = InMemoryFakeFieldBus(readings={}, setpoint_ids={_SETPOINT_ID})

    accepted = ApplySetpoint(server_bus, field_bus).execute(device, _SETPOINT_ID)

    assert accepted is False
    assert field_bus.read_setpoint(_SETPOINT_ID) == 0.0  # 書き込まれていない
