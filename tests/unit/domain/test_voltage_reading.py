import pytest

from ci_playground.domain.readings import VoltageReading


class TestVoltageReading:
    def test_create_with_valid_value(self):
        r = VoltageReading(value=1000.0)
        assert r.value == 1000.0

    def test_create_with_valid_zero_value(self):
        r = VoltageReading(value=0.0)
        assert r.value == 0.0

    def test_equality_when_values_match(self):
        r = VoltageReading(value=500.0)
        s = VoltageReading(value=500.0)
        assert r == s

    def test_equality_when_values_not_match(self):
        r = VoltageReading(value=800.0)
        s = VoltageReading(value=600.0)
        assert r != s

    def test_create_with_invalid_value(self):
        with pytest.raises(ValueError):  # 値の検証エラー
            VoltageReading(value=-1.0)

    def test_should_not_allow_value_modification(self):
        from dataclasses import FrozenInstanceError

        r = VoltageReading(value=1000.0)
        with pytest.raises(FrozenInstanceError):  # frozenで属性書き換えできない例外
            r.value = 2000.0
