"""CAN FieldBus アダプタを virtual バックエンドに束ねるテスト."""

import uuid

import can
import pytest

from tests.contract.field_bus_contract import FieldBusContract
from tests.support.can_layout import build_ecu, build_field_bus


@pytest.fixture
def bus_pair():
    """ECU 側とアダプタ側、2本のバスを同じチャネルに繋ぐ."""
    channel = f"test-{uuid.uuid4()}"
    ecu_bus = can.Bus(interface="virtual", channel=channel)
    adapter_bus = can.Bus(interface="virtual", channel=channel)
    yield ecu_bus, adapter_bus
    ecu_bus.shutdown()
    adapter_bus.shutdown()


@pytest.fixture
def ecu(bus_pair):
    ecu_bus, _ = bus_pair
    ecu = build_ecu(ecu_bus)
    ecu.start()
    yield ecu
    ecu.stop()


@pytest.fixture
def bus(bus_pair, ecu):
    _, adapter_bus = bus_pair
    return build_field_bus(adapter_bus)


class TestVirtualCanFieldBus(FieldBusContract):
    pass
