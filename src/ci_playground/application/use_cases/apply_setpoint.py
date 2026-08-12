"""EMSの指令値を検証し、現場機器へ反映するユースケース."""

from ci_playground.application.ports.field_bus import FieldBus
from ci_playground.application.ports.server_bus import ServerBus
from ci_playground.domain.device import Device
from ci_playground.domain.values import SetpointId


class ApplySetpoint:
    """EMSが書いた指令値を許容範囲内でのみ現場機器へ反映する."""

    def __init__(
        self,
        server_bus: ServerBus,
        field_bus: FieldBus,
    ) -> None:
        self._server_bus = server_bus
        self._field_bus = field_bus

    def execute(self, device: Device, setpoint_id: SetpointId) -> bool:
        """EMSの指令値を読み、許容範囲内なら現場機器へ反映する.

        Args:
            device: 対象機器。setpoint_ranges から許容範囲を引く.
            setpoint_id: 対象制御値の識別子.

        Returns:
            許容範囲内で受理され、現場機器へ反映できた場合 True.
        """
        value = self._server_bus.read_setpoint(setpoint_id)
        allowed_range = device.setpoint_ranges[setpoint_id]
        accepted = allowed_range.contains(value)
        if accepted:
            self._field_bus.write_setpoint(setpoint_id, value)
        return accepted
