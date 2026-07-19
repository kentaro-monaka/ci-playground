"""ModbusTCP ServerBus アダプタを実サーバーに束ねる結合テスト"""

import asyncio
import threading
import time

import pytest
from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import SimData, SimDevice
from pymodbus.simulator.simdata import DataType

from ci_playground.domain.values import SensorId, SetpointId
from ci_playground.infrastructure.modbus.tcp_server_bus import TcpServerBus
from ci_playground.infrastructure.modbus_registers import RegisterSpec
from tests.contract.server_bus_contract import ServerBusContract


@pytest.fixture
def modbus_server():
    """Modbus TCP サーバーを立てる."""
    box = {}
    ready = threading.Event()

    def run():
        async def main():
            setpoint_area = SimData(
                10, count=8, values=505, datatype=DataType.REGISTERS
            )
            sensor_area = SimData(20, count=1, values=0, datatype=DataType.REGISTERS)
            device = SimDevice(1, simdata=[setpoint_area, sensor_area])
            server = ModbusTcpServer(device, address=("127.0.0.1", 5020))
            box["server"] = server
            box["loop"] = asyncio.get_running_loop()
            ready.set()  # 生成できたと本体に知らせる
            await server.serve_forever()

        asyncio.run(main())  # ← スレッドの中でイベントループを回す

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    ready.wait(timeout=5)  # サーバー生成まで待つ
    time.sleep(0.5)  # 待ち受け開始まで少し待つ

    yield box["server"], box["loop"]

    # 停止もコルーチンなので、動いているループに投げて実行してもらう
    asyncio.run_coroutine_threadsafe(box["server"].shutdown(), box["loop"]).result(
        timeout=5
    )
    thread.join(timeout=5)


class TestTcpServerBus(ServerBusContract):
    @pytest.fixture
    def bus(self, modbus_server):
        server, loop = modbus_server
        return TcpServerBus(
            server=server,
            loop=loop,
            device_id=1,
            sensor_registers={
                SensorId("sen-temp"): RegisterSpec(address=20, scale=0.1)
            },
            setpoint_registers={
                SetpointId("sp-power"): RegisterSpec(address=10, scale=0.1)
            },
        )
