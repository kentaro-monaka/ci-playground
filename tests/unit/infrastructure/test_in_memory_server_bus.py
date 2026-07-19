import pytest

from ci_playground.domain.values import SensorId, SetpointId
from ci_playground.infrastructure.memory.in_memory_server_bus import (
    InMemoryFakeServerBus,
)
from tests.contract.server_bus_contract import ServerBusContract


class TestInMemoryServerBus(ServerBusContract):
    @pytest.fixture
    def bus(self):
        return InMemoryFakeServerBus(
            known_sensors={SensorId("sen-temp")},
            setpoints={SetpointId("sp-power"): 50.5},
        )
