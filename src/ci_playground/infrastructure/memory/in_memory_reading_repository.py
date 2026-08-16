"""インメモリーに保存する Fake のリポジトリ."""

from dataclasses import dataclass
from datetime import datetime

from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import DeviceId, SensorId


@dataclass
class _Record:
    """保存1件分（DBの1行に相当）."""

    device_id: DeviceId
    sensor_id: SensorId
    reading: Reading
    recorded_at: datetime


class InMemoryFakeReadingRepository:
    """Reading をメモリ上のリスト に保存・取得する Fake."""

    def __init__(self) -> None:
        self._records: list[_Record] = []

    def save(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
        reading: Reading,
        recorded_at: datetime,
    ) -> None:
        """Reading を1件保存する."""
        # オブジェクトのまま1件追加するだけ（分解しない）
        row = _Record(device_id, sensor_id, reading, recorded_at)
        self._records.append(row)

    @property
    def records(self) -> list[_Record]:
        """保存済みレコードの一覧（検証用）."""
        return list(self._records)

    def find_latest(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
    ) -> Reading | None:
        """指定 device/sensor の最新の Reading を返す（無ければ None）."""
        # 1. device_id と sensor_id が一致するものだけ絞り込む

        matches = [
            r
            for r in self._records
            if r.device_id == device_id and r.sensor_id == sensor_id
        ]
        if not matches:
            return None
        latest = max(matches, key=lambda r: r.recorded_at)
        return latest.reading
