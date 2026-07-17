"""FieldBus ポートの契約テスト（実装非依存）."""

import pytest

from ci_playground.domain.values import SetpointId


class FieldBusContract:
    def test_written_setpoint_can_be_read_back(self, bus):
        sp = SetpointId("sp-power")
        bus.write_setpoint(sp, 50.5)
        assert bus.read_setpoint(sp) == pytest.approx(50.5)
