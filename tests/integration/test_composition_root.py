import can
import pytest
from pymodbus.client import ModbusTcpClient
from sqlalchemy import create_engine

from ci_playground.composition_root import (
    build_composition,
)
from ci_playground.domain.readings import TemperatureReading
from ci_playground.infrastructure.db.connection import session_factory
from ci_playground.infrastructure.db.orm import Base
from ci_playground.infrastructure.db.sqlalchemy_reading_repository import (
    SqlAlchemyReadingRepository,
)
from tests.support.can_layout import build_ecu, vcan0_exists


@pytest.mark.docker  # MQTTブローカーが要るため
@pytest.mark.skipif(not vcan0_exists(), reason="vcan0 が無い環境ではスキップ")
def test_composition_collects_and_sends_both_systems(
    monkeypatch, modbus_server, tmp_path
):
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    engine.dispose()

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("RTU_AUX_PORT", modbus_server)
    monkeypatch.setenv("CAN_BMS_CHANNEL", "vcan0")
    monkeypatch.setenv("MODBUS_EMS_HOST", "127.0.0.1")
    monkeypatch.setenv("MODBUS_EMS_PORT", "5030")

    can_bus = can.Bus(interface="socketcan", channel="vcan0")
    ecu = build_ecu(can_bus)
    ecu.start()

    composition = build_composition()
    aux_sensor_id = composition.aux.device.sensors[0].id
    bms_sensor_id = composition.bms.device.sensors[0].id

    composition.aux.collect_readings.execute(composition.aux.device)
    composition.bms.collect_readings.execute(composition.bms.device)

    assert composition.aux.device.sensors[0].last_reading == TemperatureReading(25.0)
    assert composition.bms.device.sensors[0].last_reading == TemperatureReading(25.0)

    repository = SqlAlchemyReadingRepository(session_factory(engine))
    assert repository.find_latest(
        composition.aux.device.id, aux_sensor_id
    ) == TemperatureReading(25.0)
    assert repository.find_latest(
        composition.bms.device.id, bms_sensor_id
    ) == TemperatureReading(25.0)

    composition.aux.send_readings.execute(composition.aux.device.id, aux_sensor_id)
    composition.bms.send_readings.execute(composition.bms.device.id, bms_sensor_id)

    composition.aux.publish_readings.execute(composition.aux.device.id, aux_sensor_id)
    composition.bms.publish_readings.execute(composition.bms.device.id, bms_sensor_id)

    upper_client = ModbusTcpClient("127.0.0.1", port=5030)
    upper_client.connect()
    aux_result = upper_client.read_holding_registers(20, count=1, device_id=1)
    bms_result = upper_client.read_holding_registers(21, count=1, device_id=1)
    assert aux_result.registers[0] == 250  # 25.0 / scale(0.1)
    assert bms_result.registers[0] == 250
    upper_client.close()

    ecu.stop()
    can_bus.shutdown()
    engine.dispose()
