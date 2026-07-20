"""CAN FieldBus アダプタを SocketCAN(vcan0) に束ねるテスト."""

import subprocess

import can
import pytest

from tests.contract.field_bus_contract import FieldBusContract
from tests.support.can_layout import build_ecu, build_field_bus


def _vcan0_exists() -> bool:
    """vcan0 インターフェースが存在するか."""
    result = subprocess.run(["ip", "link", "show", "vcan0"], capture_output=True)
    return result.returncode == 0


pytestmark = pytest.mark.skipif(
    not _vcan0_exists(), reason="vcan0 が無い環境（WSL2 等）ではスキップ"
)


@pytest.fixture
def bus_pair():
    """ECU 側とアダプタ側、2本のバスを vcan0 に繋ぐ."""
    ecu_bus = can.Bus(interface="socketcan", channel="vcan0")
    adapter_bus = can.Bus(interface="socketcan", channel="vcan0")
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
