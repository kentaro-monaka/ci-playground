import pytest

from ci_playground.domain.values import DeviceId, Range, SensorId, SensorType


class TestValues:
    def test_select_sensor_type_temperature(self):
        r = SensorType.TEMPERATURE
        assert r.value == "TEMPERATURE"

    def test_select_sensor_type_VOLTAGE(self):
        r = SensorType.VOLTAGE
        assert r.value == "VOLTAGE"

    def test_select_sensor_type_CURRENT(self):
        r = SensorType.CURRENT
        assert r.value == "CURRENT"

    def test_select_sensor_type_NONE(self):
        with pytest.raises(ValueError):  # 値の検証エラー
            SensorType("INVALID")

    def test_set_correct_range(self):
        r = Range(min=10.0, max=20.0)
        assert r.min == 10.0
        assert r.max == 20.0

    def test_set_incorrect_range(self):
        with pytest.raises(ValueError):  # 値の検証エラー
            Range(min=20.0, max=10.0)

    def test_equality_when_range_match(self):
        r = Range(min=10.0, max=20.0)
        s = Range(min=10.0, max=20.0)
        assert r == s

    def test_equality_when_range_not_match(self):
        r = Range(min=15.0, max=20.0)
        s = Range(min=10.0, max=20.0)
        assert r != s

    def test_should_not_allow_range_modification(self):
        from dataclasses import FrozenInstanceError

        r = Range(min=15.0, max=20.0)
        with pytest.raises(FrozenInstanceError):  # frozenで属性書き換えできない例外
            r.min = 10.0

    def test_value_contains_center(self):
        r = Range(min=0.0, max=100.0)
        assert r.contains(50)

    def test_value_contains_lower(self):
        r = Range(min=0.0, max=100.0)
        assert r.contains(0)

    def test_value_contains_upper(self):
        r = Range(min=0.0, max=100.0)
        assert r.contains(100)

    def test_value_not_contains_lower_bound(self):
        r = Range(min=0.0, max=100.0)
        assert not r.contains(-1)

    def test_value_not_contains_upper_over(self):
        r = Range(min=0.0, max=100.0)
        assert not r.contains(101)

    def test_create_with_valid_sensor_id(self):
        r = SensorId(value="sensor-001")
        assert r.value == "sensor-001"

    def test_create_with_invalid_sensor_id(self):
        with pytest.raises(ValueError):  # 値の検証エラー
            SensorId(value="   ")

    def test_should_not_allow_sensorid_modification(self):
        from dataclasses import FrozenInstanceError

        r = SensorId(value="sensor-001")
        with pytest.raises(FrozenInstanceError):  # frozenで属性書き換えできない例外
            r.value = "sensor-002"

    def test_create_with_valid_device_id(self):
        r = DeviceId(value="device-001")
        assert r.value == "device-001"

    def test_create_with_invalid_device_id(self):
        with pytest.raises(ValueError):  # 値の検証エラー
            DeviceId(value="   ")

    def test_should_not_allow_deviceid_modification(self):
        from dataclasses import FrozenInstanceError

        r = DeviceId(value="device-001")
        with pytest.raises(FrozenInstanceError):  # frozenで属性書き換えできない例外
            r.value = "device-002"
