"""CAN テスト共通のフレーム割り当てと組み立て."""

import subprocess

import can

from ci_playground.domain.values import SensorId, SensorType, SetpointId
from ci_playground.infrastructure.can.can_field_bus import CanFieldBus
from ci_playground.infrastructure.can.frame_spec import FrameSpec
from tests.support.virtual_ecu import VirtualEcu

TEMP_BROADCAST_ID = 0x100
SETPOINT_BROADCAST_ID = 0x200
SETPOINT_COMMAND_ID = 0x300

SETPOINT_FRAMES = {
    SetpointId("sp-power"): FrameSpec(
        broadcast_id=SETPOINT_BROADCAST_ID,
        command_id=SETPOINT_COMMAND_ID,
        scale=0.1,
    )
}
SENSOR_FRAMES = {
    SensorId("sen-temp"): FrameSpec(
        broadcast_id=TEMP_BROADCAST_ID,
        scale=0.1,
        sensor_type=SensorType.TEMPERATURE,
    )
}


def vcan0_exists() -> bool:
    """vcan0 インターフェースが存在するか."""
    result = subprocess.run(["ip", "link", "show", "vcan0"], capture_output=True)
    return result.returncode == 0


def build_ecu(bus: can.BusABC) -> VirtualEcu:
    """契約が期待する初期状態の仮想ECU（温度 25.0／setpoint 0.0）."""
    return VirtualEcu(
        bus=bus,
        broadcasts={TEMP_BROADCAST_ID: 250, SETPOINT_BROADCAST_ID: 0},
        commands={SETPOINT_COMMAND_ID: SETPOINT_BROADCAST_ID},
    )


def build_field_bus(bus: can.BusABC) -> CanFieldBus:
    """契約に束ねる CanFieldBus."""
    return CanFieldBus(
        bus=bus,
        setpoint_frames=SETPOINT_FRAMES,
        sensor_frames=SENSOR_FRAMES,
    )
