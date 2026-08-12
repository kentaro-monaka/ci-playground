"""RTU FieldBus アダプタを実 pymodbus サーバーに束ねる結合テスト"""

import pytest
from pymodbus.client import ModbusSerialClient

from ci_playground.domain.values import SensorId, SensorType, SetpointId
from ci_playground.infrastructure.modbus_registers import RegisterSpec
from ci_playground.infrastructure.rs485.rtu_field_bus import RtuFieldBus
from tests.contract.field_bus_contract import FieldBusContract


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
