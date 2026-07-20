"""CAN FieldBus アダプタを virtual バックエンドに束ねるテスト."""

import uuid

import can
import pytest

from ci_playground.domain.values import SensorId, SensorType, SetpointId
from ci_playground.infrastructure.can.can_field_bus import CanFieldBus
from ci_playground.infrastructure.can.frame_spec import FrameSpec
from tests.contract.field_bus_contract import FieldBusContract
from tests.support.virtual_ecu import VirtualEcu


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
