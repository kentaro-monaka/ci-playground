import pytest
from ci_playground.domain.sensor import Sensor
from ci_playground.domain.values import SensorId, SensorType, Range
from ci_playground.domain.readings import TemperatureReading, VoltageReading


class TestSensor:
    def test_should_create_with_valid_attributes(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        assert s.id == SensorId("temp-01")
        assert s.type == SensorType.TEMPERATURE
        assert s.last_reading is None

    def test_should_record_matching_reading_type(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        s.record(TemperatureReading(value=25.0))
        assert s.last_reading == TemperatureReading(value=25.0)

    def test_should_reject_mismatched_reading_type(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        with pytest.raises(ValueError):
            s.record(VoltageReading(value=100.0))     # 温度センサに電圧Reading

    def test_last_reading_is_none_initially(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        assert s.last_reading is None
    
    def test_should_not_be_anomalous_when_no_reading(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        assert not s.is_anomalous
    
    def test_should_not_be_anomalous_when_within_range(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        s.record(TemperatureReading(value=25.0))
        assert not s.is_anomalous
    
    def test_should_not_be_anomalous_when_outside_range(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        s.record(TemperatureReading(value=100.1))
        assert s.is_anomalous
    
    def test_equality_when_ids_match(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        r = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.VOLTAGE,
            allowed_range=Range(min=200, max=1000),
        )
        assert s == r
    
    def test_inequality_when_ids_differ(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        r = Sensor(
            id=SensorId("temp-02"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        assert s != r
    
    def test_should_be_equal_even_with_different_last_readings(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        r = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.VOLTAGE,
            allowed_range=Range(min=200, max=1000),
        )
        s.record(TemperatureReading(value=200.0))
        r.record(VoltageReading(value=100.1))
        assert s == r
    
    def test_should_be_usable_as_set_element(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        sensors = {s}
        assert s in sensors
    
    def test_equal_sensors_have_same_hash(self):
        s = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        r = Sensor(
            id=SensorId("temp-01"),
            type=SensorType.TEMPERATURE,
            allowed_range=Range(min=0, max=100),
        )
        r.record(TemperatureReading(value=200.0))
        assert s == r
        assert hash(s) == hash(r)