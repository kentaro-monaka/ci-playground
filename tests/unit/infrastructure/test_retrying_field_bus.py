"""RetryingFieldBus のテスト."""

import pytest

from ci_playground.application.ports.field_bus import FieldBusError
from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import SensorId, SetpointId
from ci_playground.infrastructure.retrying_field_bus import RetryingFieldBus


class _FlakyFieldBus:
    """指定回数だけ失敗し、その後は成功する検証用スタブ."""

    def __init__(self, fail_times: int) -> None:
        self._fail_times = fail_times
        self.read_calls = 0
        self.write_calls = 0

    def read_reading(self, sensor_id):
        self.read_calls += 1
        if self.read_calls <= self._fail_times:
            raise FieldBusError("一時的な失敗")
        return TemperatureReading(25.0)

    def read_setpoint(self, setpoint_id):
        self.read_calls += 1
        if self.read_calls <= self._fail_times:
            raise FieldBusError("一時的な失敗")
        return 0.0

    def write_setpoint(self, setpoint_id, value):
        self.write_calls += 1
        if self.write_calls <= self._fail_times:
            raise FieldBusError("一時的な失敗")


def test_succeeds_without_retry():
    inner = _FlakyFieldBus(fail_times=0)
    bus = RetryingFieldBus(inner, attempts=3, backoff=0)

    result = bus.read_reading(SensorId("sen-temp"))

    assert result == TemperatureReading(25.0)
    assert inner.read_calls == 1


def test_succeeds_after_transient_failures():
    inner = _FlakyFieldBus(fail_times=2)
    bus = RetryingFieldBus(inner, attempts=3, backoff=0)

    result = bus.read_reading(SensorId("sen-temp"))

    assert result == TemperatureReading(25.0)
    assert inner.read_calls == 3


def test_raises_after_exhausting_attempts():
    inner = _FlakyFieldBus(fail_times=5)
    bus = RetryingFieldBus(inner, attempts=3, backoff=0)

    with pytest.raises(FieldBusError):
        bus.read_reading(SensorId("sen-temp"))

    assert inner.read_calls == 3


def test_write_is_retried():
    inner = _FlakyFieldBus(fail_times=2)
    bus = RetryingFieldBus(inner, attempts=3, backoff=0)

    bus.write_setpoint(SetpointId("sp-power"), 50.0)

    assert inner.write_calls == 3


def test_read_setpoint_is_retried():
    inner = _FlakyFieldBus(fail_times=2)
    bus = RetryingFieldBus(inner, attempts=3, backoff=0)

    result = bus.read_setpoint(SetpointId("sp-power"))

    assert result == 0.0
    assert inner.read_calls == 3
