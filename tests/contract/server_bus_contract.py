"""ServerBus ポートの契約テスト（実装非依存）."""

import pytest

from ci_playground.application.ports.server_bus import ServerBusError
from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import SensorId, SetpointId


class ServerBusContract:
    def test_publish_known_sensor_does_not_raise(self, bus):
        sensor = SensorId("sen-temp")
        bus.publish_reading(sensor, TemperatureReading(25.0))

    def test_publish_unknown_sensor_raises(self, bus):
        with pytest.raises(ServerBusError):
            bus.publish_reading(SensorId("sen-unknown"), TemperatureReading(25.0))

    def test_read_seeded_setpoint_returns_value(self, bus):
        value = bus.read_setpoint(SetpointId("sp-power"))
        assert value == pytest.approx(50.5)

    def test_read_unknown_setpoint_raises(self, bus):
        with pytest.raises(ServerBusError):
            bus.read_setpoint(SetpointId("sp-unknown"))
