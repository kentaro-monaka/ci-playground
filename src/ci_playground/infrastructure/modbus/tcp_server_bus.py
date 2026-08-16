"""pymodbus (TCP) を使った ServerBus サーバーの実装."""

import asyncio
import threading
from typing import Any

from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

from ci_playground.application.ports.server_bus import ServerBusError
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import SensorId, SetpointId
from ci_playground.infrastructure.modbus_registers import RegisterSpec

_HOLDING_REGISTERS = 3


class TcpServerBus:
    """Modbus-TCP で計測値公開・制御受付する ServerBus サーバー."""

    def __init__(
        self,
        server: ModbusTcpServer,
        loop: asyncio.AbstractEventLoop,
        device_id: int,
        sensor_registers: dict[SensorId, RegisterSpec],
        setpoint_registers: dict[SetpointId, RegisterSpec],
    ) -> None:
        self._server = server
        self._loop = loop
        self._device_id = device_id
        self._sensor_registers = sensor_registers
        self._setpoint_registers = setpoint_registers

    def publish_reading(self, sensor_id: SensorId, reading: Reading) -> None:
        """Reading を1件公開する."""
        spec = self._sensor_registers.get(sensor_id)
        if spec is None:
            raise ServerBusError(f"未登録の sensor id です: {sensor_id}")
        raw = round(reading.value / spec.scale)
        asyncio.run_coroutine_threadsafe(
            self._server.async_setValues(
                self._device_id, _HOLDING_REGISTERS, spec.address, [raw]
            ),
            self._loop,
        ).result()

    def read_setpoint(self, setpoint_id: SetpointId) -> float:
        """上位が書き込んだ制御値をサーバーの倉庫から読む."""
        spec = self._setpoint_registers.get(setpoint_id)
        if spec is None:
            raise ServerBusError(f"未登録の setpoint id です: {setpoint_id}")
        regs = asyncio.run_coroutine_threadsafe(
            self._server.async_getValues(
                self._device_id, _HOLDING_REGISTERS, spec.address, 1
            ),
            self._loop,
        ).result()
        return float(regs[0]) * spec.scale

    @classmethod
    def start(
        cls,
        host: str,
        port: int,
        device_id: int,
        sensor_registers: dict[SensorId, RegisterSpec],
        setpoint_registers: dict[SetpointId, RegisterSpec],
    ) -> "TcpServerBus":
        """Modbus TCP サーバーを起動し、束ねた TcpServerBus を返す."""
        box: dict[str, Any] = {}
        ready = threading.Event()

        def run() -> None:
            async def main() -> None:
                sim_data = SimData(0, count=100, values=0, datatype=DataType.REGISTERS)
                device = SimDevice(device_id, simdata=[sim_data])
                server = ModbusTcpServer(device, address=(host, port))
                box["server"] = server
                box["loop"] = asyncio.get_running_loop()
                ready.set()
                await server.serve_forever()

            asyncio.run(main())

        threading.Thread(target=run, daemon=True).start()
        ready.wait(timeout=5)

        return cls(
            server=box["server"],
            loop=box["loop"],
            device_id=device_id,
            sensor_registers=sensor_registers,
            setpoint_registers=setpoint_registers,
        )
