"""FieldBus ポートの契約テスト（実装非依存）."""

import pytest

from ci_playground.application.ports.field_bus import FieldBusError
from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import SensorId, SetpointId


class FieldBusContract:
    def test_written_setpoint_can_be_read_back(self, bus):
        sp = SetpointId("sp-power")
        bus.write_setpoint(sp, 50.5)
        assert bus.read_setpoint(sp) == pytest.approx(50.5)

    def test_unwritten_setpoint_reads_zero(self, bus):
        sp = SetpointId("sp-power")
        assert bus.read_setpoint(sp) == 0.0

    def test_read_unknown_setpoint_raises(self, bus):
        with pytest.raises(FieldBusError):
            bus.read_setpoint(SetpointId("sp-unknown"))

    def test_write_unknown_setpoint_raises(self, bus):
        with pytest.raises(FieldBusError):
            bus.write_setpoint(SetpointId("sp-unknown"), 1.0)

    def test_read_reading_returns_seeded_value(self, bus):
        reading = bus.read_reading(SensorId("sen-temp"))
        assert isinstance(reading, TemperatureReading)
        assert reading.value == pytest.approx(25.0)

    def test_read_unknown_reading_raises(self, bus):
        with pytest.raises(FieldBusError):
            bus.read_reading(SensorId("sen-unknown"))
