"""構成ルート：BMS・付帯設備（RTU接続）の Device ・アダプタ・ユースケースを組立."""

import os
from dataclasses import dataclass

import can
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from pymodbus.client import ModbusSerialClient

from ci_playground.application.ports.reading_repository import ReadingRepository
from ci_playground.application.ports.reading_sender import ReadingSender
from ci_playground.application.ports.server_bus import ServerBus
from ci_playground.application.use_cases.collect_readings import (
    CollectReadings,
)
from ci_playground.application.use_cases.publish_readings import PublishReadings
from ci_playground.application.use_cases.send_readings import (
    SendReadings,
)
from ci_playground.domain.device import Device
from ci_playground.domain.sensor import Sensor
from ci_playground.domain.values import DeviceId, Range, SensorId, SensorType
from ci_playground.infrastructure.can.can_field_bus import CanFieldBus
from ci_playground.infrastructure.can.frame_spec import FrameSpec
from ci_playground.infrastructure.db.connection import get_engine, session_factory
from ci_playground.infrastructure.db.sqlalchemy_reading_repository import (
    SqlAlchemyReadingRepository,
)
from ci_playground.infrastructure.modbus.tcp_server_bus import TcpServerBus
from ci_playground.infrastructure.modbus_registers import RegisterSpec
from ci_playground.infrastructure.mqtt.mqtt_reading_sender import (
    MqttReadingSender,
)
from ci_playground.infrastructure.rs485.rtu_field_bus import RtuFieldBus

AUX_DEVICE_ID = DeviceId("dev-aux")
AUX_TEMP_SENSOR_ID = SensorId("sen-aux-temp")
BMS_DEVICE_ID = DeviceId("dev-bms")
BMS_TEMP_SENSOR_ID = SensorId("sen-bms-temp")

AUX_SENSOR_REGISTERS = {
    AUX_TEMP_SENSOR_ID: RegisterSpec(
        address=20, scale=0.1, sensor_type=SensorType.TEMPERATURE
    ),
}
BMS_SENSOR_FRAMES = {
    BMS_TEMP_SENSOR_ID: FrameSpec(
        broadcast_id=0x100, scale=0.1, sensor_type=SensorType.TEMPERATURE
    ),
}
EMS_SENSOR_REGISTERS = {
    AUX_TEMP_SENSOR_ID: RegisterSpec(
        address=20, scale=0.1, sensor_type=SensorType.TEMPERATURE
    ),
    BMS_TEMP_SENSOR_ID: RegisterSpec(
        address=21, scale=0.1, sensor_type=SensorType.TEMPERATURE
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
    publish_readings: PublishReadings


def build_aux_composition(
    repository: ReadingRepository,
    sender: ReadingSender,
    server_bus: ServerBus,
) -> AuxComposition:
    """付帯設備向けの Device・アダプタ・ユースケースを一式組み立てる."""
    device = build_aux_device()
    field_bus = build_rtu_field_bus()

    return AuxComposition(
        device=device,
        collect_readings=CollectReadings(field_bus, repository),
        send_readings=SendReadings(repository, sender),
        publish_readings=PublishReadings(repository, server_bus),
    )


def build_bms_device() -> Device:
    """BMS本体の Device を組み立てる."""
    device = Device(id=BMS_DEVICE_ID)
    device.attach_sensor(
        Sensor(BMS_TEMP_SENSOR_ID, SensorType.TEMPERATURE, Range(-20.0, 80.0))
    )
    return device


def build_can_field_bus() -> CanFieldBus:
    """BMS本体向けの CanFieldBus を組み立てる."""
    bus = can.Bus(
        interface=os.environ.get("CAN_BMS_INTERFACE", "socketcan"),
        channel=os.environ["CAN_BMS_CHANNEL"],
        bitrate=int(os.environ.get("CAN_BMS_BITRATE", "500000")),
    )
    return CanFieldBus(
        bus=bus,
        setpoint_frames={},
        sensor_frames=BMS_SENSOR_FRAMES,
    )


@dataclass(frozen=True)
class BmsComposition:
    """BMS本体向けに組み立てたユースケース一式."""

    device: Device
    collect_readings: CollectReadings
    send_readings: SendReadings
    publish_readings: PublishReadings


def build_bms_composition(
    repository: ReadingRepository, sender: ReadingSender, server_bus: ServerBus
) -> BmsComposition:
    """BMS本体向けの Device・アダプタ・ユースケースを一式組み立てる."""
    device = build_bms_device()
    field_bus = build_can_field_bus()

    return BmsComposition(
        device=device,
        collect_readings=CollectReadings(field_bus, repository),
        send_readings=SendReadings(repository, sender),
        publish_readings=PublishReadings(repository, server_bus),
    )


@dataclass(frozen=True)
class Composition:
    """付帯設備・BMS、両系統をまとめた構成一式."""

    aux: AuxComposition
    bms: BmsComposition


def build_composition() -> Composition:
    """共有アダプタ（repository/sender）を1回だけ組み立て、両系統に配って束ねる."""
    repository = build_reading_repository()
    sender = build_reading_sender()
    server_bus = build_server_bus()

    return Composition(
        aux=build_aux_composition(repository, sender, server_bus),
        bms=build_bms_composition(repository, sender, server_bus),
    )


def build_server_bus() -> TcpServerBus:
    """EMS向けの TcpServerBus を組み立てる."""
    return TcpServerBus.start(
        host=os.environ.get("MODBUS_EMS_HOST", "0.0.0.0"),
        port=int(os.environ.get("MODBUS_EMS_PORT", "502")),
        device_id=1,
        sensor_registers=EMS_SENSOR_REGISTERS,
        setpoint_registers={},
    )
