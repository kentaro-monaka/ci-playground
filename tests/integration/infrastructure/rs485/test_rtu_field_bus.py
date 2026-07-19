"""RTU FieldBus アダプタを実 pymodbus サーバーに束ねる結合テスト"""

import asyncio
import re
import subprocess
import threading
import time

import pytest
from pymodbus.client import ModbusSerialClient
from pymodbus.server import ModbusSerialServer
from pymodbus.simulator import SimData, SimDevice
from pymodbus.simulator.simdata import DataType

from ci_playground.domain.values import SensorId, SensorType, SetpointId
from ci_playground.infrastructure.rs485.rtu_field_bus import RtuFieldBus
from ci_playground.infrastructure.modbus_registers import RegisterSpec
from tests.contract.field_bus_contract import FieldBusContract


@pytest.fixture
def serial_pair():
    """socat で疑似シリアルペアを立てて、2つのポート名を返す."""
    proc = subprocess.Popen(
        ["socat", "-d", "-d", "pty,raw,echo=0", "pty,raw,echo=0"],
        stderr=subprocess.PIPE,
        text=True,
    )
    ports = []
    # socat は起動時に stderr へ "... PTY is /dev/pts/N" を2行出す
    while len(ports) < 2:
        line = proc.stderr.readline()
        if not line:
            raise RuntimeError("socat がポートを出力せず終了した")
        match = re.search(r"/dev/pts/\d+", line)
        if match:
            ports.append(match.group())
    time.sleep(0.5)
    yield ports[0], ports[1]
    proc.terminate()


@pytest.fixture
def modbus_server(serial_pair):
    """擬似シリアルの片端(server側)に Modbus RTU サーバーを立てる."""
    server_port, client_port = serial_pair
    box = {}
    ready = threading.Event()

    def run():
        async def main():
            setpoint_area = SimData(10, count=8, values=0, datatype=DataType.REGISTERS)
            sensor_area = SimData(20, count=1, values=250, datatype=DataType.REGISTERS)
            device = SimDevice(1, simdata=[setpoint_area, sensor_area])
            server = ModbusSerialServer(device, port=server_port, baudrate=9600)
            box["server"] = server
            box["loop"] = asyncio.get_running_loop()
            ready.set()  # 生成できたと本体に知らせる
            await server.serve_forever()

        asyncio.run(main())  # ← スレッドの中でイベントループを回す

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    ready.wait(timeout=5)  # サーバー生成まで待つ
    time.sleep(0.5)  # 待ち受け開始まで少し待つ

    yield client_port

    # 停止もコルーチンなので、動いているループに投げて実行してもらう
    asyncio.run_coroutine_threadsafe(box["server"].shutdown(), box["loop"]).result(
        timeout=5
    )
    thread.join(timeout=5)


class TestRtuFieldBus(FieldBusContract):
    @pytest.fixture
    def bus(self, modbus_server):
        client = ModbusSerialClient(port=modbus_server, baudrate=9600)
        client.connect()
        adapter = RtuFieldBus(
            client=client,
            device_id=1,
            setpoint_registers={
                SetpointId("sp-power"): RegisterSpec(address=10, scale=0.1),
            },
            sensor_registers={
                SensorId("sen-temp"): RegisterSpec(
                    address=20, scale=0.1, sensor_type=SensorType.TEMPERATURE
                ),
            },
        )
        yield adapter
        client.close()
