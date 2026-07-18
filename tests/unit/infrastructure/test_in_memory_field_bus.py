import pytest

from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import SensorId, SetpointId
from ci_playground.infrastructure.memory.in_memory_field_bus import (
    InMemoryFakeFieldBus,
)
from tests.contract.field_bus_contract import FieldBusContract


class TestInMemoryFieldBus(FieldBusContract):
    @pytest.fixture
    def bus(self):
        return InMemoryFakeFieldBus(
            readings={SensorId("sen-temp"): TemperatureReading(25.0)},
            setpoint_ids={SetpointId("sp-power")},
        )
