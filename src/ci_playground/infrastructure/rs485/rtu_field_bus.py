"""pymodbus (RTU/RS485) を使った FieldBus クライアントの実装."""

from dataclasses import dataclass

from pymodbus.client import ModbusSerialClient

from ci_playground.application.ports.field_bus import FieldBusError
from ci_playground.domain.values import SetpointId


@dataclass(frozen=True)
class RegisterSpec:
    """Modbus レジスタ1つの割り当て（番地とスケール）."""

    address: int
    scale: float = 1.0


class RtuFieldBus:
    """RS485/Modbus-RTU でフィールド機器を読み書きする FieldBus クライアント."""

    def __init__(
        self,
        client: ModbusSerialClient,
        device_id: int,
        setpoint_registers: dict[SetpointId, RegisterSpec],
    ) -> None:
        self._client = client
        self._device_id = device_id
        self._setpoint_registers = setpoint_registers

    def write_setpoint(self, setpoint_id: SetpointId, value: float) -> None:
        """Setpoint を1件書き込む."""
        spec = self._setpoint_registers.get(setpoint_id)
        if spec is None:
            raise FieldBusError(f"未登録の setpoint id です: {setpoint_id}")
        raw = round(value / spec.scale)
        result = self._client.write_register(
            spec.address, raw, device_id=self._device_id
        )
        if result.isError():
            raise FieldBusError(f"write 失敗: {setpoint_id} -> {result}")

    def read_setpoint(self, setpoint_id: SetpointId) -> float:
        """Setpoint を1件読む."""
        spec = self._setpoint_registers.get(setpoint_id)
        if spec is None:
            raise FieldBusError(f"未登録の setpoint id です: {setpoint_id}")
        result = self._client.read_holding_registers(
            spec.address, count=1, device_id=self._device_id
        )
        if result.isError():
            raise FieldBusError(f"read 失敗: {setpoint_id} -> {result}")
        return result.registers[0] * spec.scale
