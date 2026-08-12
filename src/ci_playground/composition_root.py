"""構成ルート：付帯設備（RTU接続）の Device ・アダプタ・ユースケースを組み立てる."""

import os
from dataclasses import dataclass

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from pymodbus.client import ModbusSerialClient

from ci_playground.application.use_cases.collect_readings import (
    CollectReadings,
)
from ci_playground.application.use_cases.send_readings import (
    SendReadings,
)
from ci_playground.domain.device import Device
from ci_playground.domain.sensor import Sensor
from ci_playground.domain.values import DeviceId, Range, SensorId, SensorType
from ci_playground.infrastructure.db.connection import get_engine, session_factory
from ci_playground.infrastructure.db.sqlalchemy_reading_repository import (
    SqlAlchemyReadingRepository,
)
from ci_playground.infrastructure.modbus_registers import RegisterSpec
from ci_playground.infrastructure.mqtt.mqtt_reading_sender import (
    MqttReadingSender,
)
from ci_playground.infrastructure.rs485.rtu_field_bus import RtuFieldBus

AUX_DEVICE_ID = DeviceId("dev-aux")
AUX_TEMP_SENSOR_ID = SensorId("sen-aux-temp")

AUX_SENSOR_REGISTERS = {
    AUX_TEMP_SENSOR_ID: RegisterSpec(
        address=20, scale=0.1, sensor_type=SensorType.TEMPERATURE
    ),
}


def build_aux_device() -> Device:
    """付帯設備（RTU接続）の Device を組み立てる."""
    device = Device(id=AUX_DEVICE_ID)
    device.attach_sensor(
        Sensor(AUX_TEMP_SENSOR_ID, SensorType.TEMPERATURE, Range(-20.0, 80.0))
    )
    return device


def build_rtu_field_bus() -> RtuFieldBus:
    """付帯設備向けの RtuFieldBus を組み立てる."""
    client = ModbusSerialClient(
        port=os.environ["RTU_AUX_PORT"],
        baudrate=int(os.environ.get("RTU_AUX_BAUDRATE", "9600")),
    )
    return RtuFieldBus(
        client=client,
        device_id=int(os.environ.get("RTU_AUX_UNIT_ID", "1")),
        setpoint_registers={},
        sensor_registers=AUX_SENSOR_REGISTERS,
    )


def build_reading_repository() -> SqlAlchemyReadingRepository:
    """DB接続の ReadingRepository を組み立てる."""
    engine = get_engine()
    return SqlAlchemyReadingRepository(session_factory(engine))


def build_reading_sender() -> MqttReadingSender:
    """MQTT接続の ReadingSender を組み立てる."""
    host = os.environ.get("MQTT_BROKER_HOST", "localhost")
    port = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
    client = mqtt.Client(CallbackAPIVersion.VERSION2)
    client.connect(host, port)
    client.loop_start()
    return MqttReadingSender(client)


@dataclass(frozen=True)
class AuxComposition:
    """付帯設備（RTU接続）向けに組み立てたユースケース一式."""

    device: Device
    collect_readings: CollectReadings
    send_readings: SendReadings


def build_aux_composition() -> AuxComposition:
    """付帯設備向けの Device・アダプタ・ユースケースを一式組み立てる."""
    device = build_aux_device()
    field_bus = build_rtu_field_bus()
    repository = build_reading_repository()
    sender = build_reading_sender()

    return AuxComposition(
        device=device,
        collect_readings=CollectReadings(field_bus, repository),
        send_readings=SendReadings(repository, sender),
    )
