import pytest
from ci_playground.domain.readings import TemperatureReading


class TestTemperatureReading:
    def test_create_with_valid_value(self):
        r = TemperatureReading(value=25.0)
        assert r.value == 25.0

    def test_equality_when_values_match(self):
        r = TemperatureReading(value=30.0)
        s = TemperatureReading(value=30.0)
        assert r == s

    def test_equality_when_values_not_match(self):
        r = TemperatureReading(value=40.0)
        s = TemperatureReading(value=30.0)
        assert r != s

    def test_should_reject_value_below_absolute_zero(self):
        with pytest.raises(ValueError):  # 値の検証エラー
            TemperatureReading(value=-273.2)

    def test_should_not_allow_value_modification(self):
        from dataclasses import FrozenInstanceError

        r = TemperatureReading(value=20.0)
        with pytest.raises(FrozenInstanceError):  # frozenで属性書き換えできない例外
            r.value = 99
