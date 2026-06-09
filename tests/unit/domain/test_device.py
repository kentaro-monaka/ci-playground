import pytest

from ci_playground.domain.device import Device
from ci_playground.domain.readings import TemperatureReading, VoltageReading
from ci_playground.domain.sensor import Sensor
from ci_playground.domain.values import DeviceId, Range, SensorId, SensorType


class TestDevice:
    def test_should_attach_sensor(self):
        device = Device(id=DeviceId("dev-01"))
        sensor = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        device.attach_sensor(sensor)
        assert len(device.sensors) == 1

    def test_should_reject_duplicate_sensor_id(self):
        device = Device(id=DeviceId("dev-01"))
        s1 = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        s2 = Sensor(
            id=SensorId("temp-01"),  # 同じID
            type=SensorType.VOLTAGE,
            allowed_range=Range(min=0, max=500),
        )
        device.attach_sensor(s1)
        with pytest.raises(ValueError):
            device.attach_sensor(s2)

    def test_should_find_sensor_by_id(self):
        device = Device(id=DeviceId("dev-01"))
        sensor = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        device.attach_sensor(sensor)
        found = device.find_sensor(SensorId("temp-01"))
        assert found is sensor  # 同一オブジェクトであることを is で確認

    def test_should_raise_when_sensor_not_found(self):
        device = Device(id=DeviceId("dev-01"))
        with pytest.raises(KeyError):
            device.find_sensor(SensorId("ghost"))

    def test_read_all_returns_dict_of_readings(self):
        device = Device(id=DeviceId("dev-01"))
        temp = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        volt = Sensor(
            id=SensorId("volt-01"),
            type=SensorType.VOLTAGE,
            allowed_range=Range(min=0, max=500),
        )
        device.attach_sensor(temp)
        device.attach_sensor(volt)
        temp.record(TemperatureReading(value=25.0))

        readings = device.read_all()
        assert readings[SensorId("temp-01")] == TemperatureReading(value=25.0)
        assert readings[SensorId("volt-01")] is None  # まだ record してない

    def test_anomalous_sensors_returns_only_outside_range(self):
        device = Device(id=DeviceId("dev-01"))
        temp = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        volt = Sensor(
            id=SensorId("volt-01"),
            type=SensorType.VOLTAGE,
            allowed_range=Range(min=0, max=500),
        )
        device.attach_sensor(temp)
        device.attach_sensor(volt)
        temp.record(TemperatureReading(value=200.0))  # 範囲外（100超）
        volt.record(VoltageReading(value=100.0))  # 範囲内

        anomalous = device.anomalous_sensors()
        assert len(anomalous) == 1
        assert anomalous[0].id == SensorId("temp-01")

    def test_equality_when_match(self):
        device1 = Device(id=DeviceId("dev-01"))
        device2 = Device(id=DeviceId("dev-01"))
        s1 = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        s2 = Sensor(
            id=SensorId("temp-01"),  # 同じID
            type=SensorType.VOLTAGE,
            allowed_range=Range(min=0, max=500),
        )
        device1.attach_sensor(s1)
        device2.attach_sensor(s2)
        assert device1 == device2

    def test_inequality_when_differ(self):
        device1 = Device(id=DeviceId("dev-01"))
        device2 = Device(id=DeviceId("dev-02"))
        assert device1 != device2

    def test_should_be_usable_as_set_element(self):
        device = Device(id=DeviceId("dev-01"))
        s1 = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        device.attach_sensor(s1)
        devices = {device}
        assert device in devices

    def test_equal_devices_have_same_hash(self):
        device1 = Device(id=DeviceId("dev-01"))
        device2 = Device(id=DeviceId("dev-01"))
        s1 = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        s2 = Sensor(
            id=SensorId("temp-01"),  # 同じID
            type=SensorType.VOLTAGE,
            allowed_range=Range(min=0, max=500),
        )
        device1.attach_sensor(s1)
        device2.attach_sensor(s2)
        assert device1 == device2
        assert hash(device1) == hash(device2)
