import pytest

from ci_playground.domain.values import SetpointId
from ci_playground.infrastructure.memory.in_memory_field_bus import (
    InMemoryFakeFieldBus,
)
from tests.contract.field_bus_contract import FieldBusContract


class TestInMemoryFieldBus(FieldBusContract):
    @pytest.fixture
    def bus(self):
        return InMemoryFakeFieldBus(
            readings={},
            setpoint_ids={SetpointId("sp-power")},
        )
