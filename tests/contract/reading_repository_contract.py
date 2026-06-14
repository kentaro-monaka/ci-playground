"""ReadingRepository ポートの契約テスト（実装非依存）.

「どの保存先（Fake/SQlite/Postgres）でも守るべき約束」を定義する抽象クラス。
具体実装は子クラスが repo フィクスチャで供給する。
※ クラス名を Test で始めない（pytest が親単体を収集しないように）。
"""

from datetime import datetime, timedelta, timezone

from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import DeviceId, SensorId


class ReadingRepositoryContract:
    # repo は子クラスが供給するフィクスチャ。毎テスト「空の新品」が渡される前提。

    def test_saved_reading_can_be_retrieved(self, repo):
        device = DeviceId("dev-1")
        sensor = SensorId("sen-01")
        reading = TemperatureReading(25.0)
        recorded_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        repo.save(device, sensor, reading, recorded_at)
        result = repo.find_latest(device, sensor)
        assert result == reading

    def test_find_latest_returns_none_when_empty(self, repo):
        device = DeviceId("dev-1")
        sensor = SensorId("sen-01")
        result = repo.find_latest(device, sensor)
        assert result is None

    def test_find_latest_returns_most_recent_by_recorded_at(self, repo):
        device = DeviceId("dev-1")
        sensor = SensorId("sen-01")
        base_reading = TemperatureReading(25.0)
        base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        new_reading = TemperatureReading(30.0)
        new_time = base_time + timedelta(seconds=1)
        # act:     わざと「新しい時刻 → 古い時刻」の順に save する
        repo.save(device, sensor, new_reading, new_time)
        repo.save(device, sensor, base_reading, base_time)
        result = repo.find_latest(device, sensor)
        assert result == new_reading

    def test_readings_are_isolated_per_sensor(self, repo):
        device_A = DeviceId("dev-A")
        sensor_A = SensorId("sen-A")
        reading_A = TemperatureReading(1.0)
        recorded_at_A = datetime(2026, 1, 1, tzinfo=timezone.utc)
        device_B = DeviceId("dev-B")
        sensor_B = SensorId("sen-B")
        reading_B = TemperatureReading(2.0)
        recorded_at_B = datetime(2026, 1, 1, tzinfo=timezone.utc)
        repo.save(device_A, sensor_A, reading_A, recorded_at_A)
        repo.save(device_B, sensor_B, reading_B, recorded_at_B)
        result_A = repo.find_latest(device_A, sensor_A)
        result_B = repo.find_latest(device_B, sensor_B)
        assert result_A == reading_A
        assert result_B == reading_B
