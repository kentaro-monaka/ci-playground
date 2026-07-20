"""CAN FieldBus アダプタを SocketCAN(vcan0) に束ねるテスト."""

import subprocess

import can
import pytest

from ci_playground.domain.values import SensorId, SensorType, SetpointId
from ci_playground.infrastructure.can.can_field_bus import CanFieldBus
from ci_playground.infrastructure.can.frame_spec import FrameSpec
from tests.contract.field_bus_contract import FieldBusContract
from tests.support.virtual_ecu import VirtualEcu


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
    ecu = VirtualEcu(
        bus=ecu_bus,
        broadcasts={0x100: 250, 0x200: 0},
        commands={0x300: 0x200},
    )
    ecu.start()
    yield ecu
    ecu.stop()


@pytest.fixture
def bus(bus_pair, ecu):
    _, adapter_bus = bus_pair
    return CanFieldBus(
        bus=adapter_bus,
        setpoint_frames={
            SetpointId("sp-power"): FrameSpec(
                broadcast_id=0x200, command_id=0x300, scale=0.1
            )
        },
        sensor_frames={
            SensorId("sen-temp"): FrameSpec(
                broadcast_id=0x100, scale=0.1, sensor_type=SensorType.TEMPERATURE
            )
        },
    )


class TestVirtualCanFieldBus(FieldBusContract):
    pass
