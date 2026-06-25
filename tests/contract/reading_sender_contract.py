"""ReadingSender ポートの契約テスト（実装非依存）.

送信ポートで共有できる約束は2つだけ：成功＝静か／失敗＝ReadingSendError。
「何を送ったか」は輸送依存なので各実装の個別テストに残す。
子クラスが sender_ok / failing_sender フィクスチャを供給する。
"""

from datetime import datetime, timezone

import pytest

from ci_playground.application.ports.reading_sender import ReadingSendError
from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import DeviceId, SensorId


class ReadingSenderContract:
    def test_send_succeeds_silently(self, sender_ok):
        result = sender_ok.send(
            DeviceId("dev-01"),
            SensorId("sen-01"),
            TemperatureReading(25.0),
            datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        assert result is None

    def test_send_raises_on_failure(self, failing_sender):
        with pytest.raises(ReadingSendError):
            failing_sender.send(
                DeviceId("dev-01"),
                SensorId("sen-01"),
                TemperatureReading(25.0),
                datetime(2026, 1, 1, tzinfo=timezone.utc),
            )
