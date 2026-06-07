import pytest
from ci_playground.domain.readings import CurrentReading


class TestCurrentReading:
    def test_create_with_valid_positive_value(self):
        r = CurrentReading(value=1000.0)
        assert r.value == 1000.0

    def test_create_with_valid_zero_value(self):
        r = CurrentReading(value=0.0)
        assert r.value == 0.0

    def test_create_with_valid_negative_value(self):
        r = CurrentReading(value=-1000.0)
        assert r.value == -1000.0

    def test_equality_when_values_match(self):
        r = CurrentReading(value=500.0)
        s = CurrentReading(value=500.0)
        assert r == s

    def test_equality_when_values_not_match(self):
        r = CurrentReading(value=500.0)
        s = CurrentReading(value=-500.0)
        assert r != s

    def test_should_not_allow_value_modification(self):
        from dataclasses import FrozenInstanceError

        r = CurrentReading(value=500.0)
        with pytest.raises(FrozenInstanceError):  # frozenで属性書き換えできない例外
            r.value = -500.0
