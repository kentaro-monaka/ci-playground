"""python-can を使った FieldBus クライアントの実装（CAN）."""

import time

import can

from ci_playground.application.ports.field_bus import FieldBusError
from ci_playground.domain.reading_types import SENSOR_TYPE_TO_READING
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import SensorId, SetpointId
from ci_playground.infrastructure.can.frame_spec import FrameSpec


class CanFieldBus:
    """CAN バスでフィールド機器を読み書きする FieldBus クライアント."""

    def __init__(
        self,
        bus: can.BusABC,
        setpoint_frames: dict[SetpointId, FrameSpec],
        sensor_frames: dict[SensorId, FrameSpec],
        timeout: float = 1.0,
    ) -> None:
        self._bus = bus
        self._setpoint_frames = setpoint_frames
        self._sensor_frames = sensor_frames
        self._timeout = timeout

    def write_setpoint(self, setpoint_id: SetpointId, value: float) -> None:
        """Setpoint を1件書き込む."""
        spec = self._setpoint_frames.get(setpoint_id)
        if spec is None or spec.command_id is None:
            raise FieldBusError(f"未登録の setpoint id です: {setpoint_id}")
        raw = round(value / spec.scale)
        self._bus.send(
            can.Message(
                arbitration_id=spec.command_id,
                data=raw.to_bytes(2, "big"),
                is_extended_id=False,
            )
        )

    def read_setpoint(self, setpoint_id: SetpointId) -> float:
        """Setpoint を1件読む."""
        spec = self._setpoint_frames.get(setpoint_id)
        if spec is None:
            raise FieldBusError(f"未登録の setpoint id です: {setpoint_id}")
        return self._wait_for(spec.broadcast_id) * spec.scale

    def read_reading(self, sensor_id: SensorId) -> Reading:
        """Reading を1件読む."""
        spec = self._sensor_frames.get(sensor_id)
        if spec is None:
            raise FieldBusError(f"未登録の sensor id です: {sensor_id}")
        raw = self._wait_for(spec.broadcast_id)
        if spec.sensor_type is None:
            raise FieldBusError(f"sensor_type が未設定です: {sensor_id}")
        reading_cls = SENSOR_TYPE_TO_READING[spec.sensor_type]
        return reading_cls(value=raw * spec.scale)

    def _wait_for(self, can_id: int) -> int:
        """指定 ID のブロードキャストを1本待ち、生値を返す."""
        deadline = time.monotonic() + self._timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise FieldBusError(f"受信タイムアウト: can_id=0x{can_id:X}")
            msg = self._bus.recv(timeout=remaining)
            if msg is not None and msg.arbitration_id == can_id:
                return int.from_bytes(msg.data[:2], "big")
