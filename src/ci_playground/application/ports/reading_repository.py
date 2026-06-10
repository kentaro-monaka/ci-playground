"""Reading 保存・取得のための Repository ポート."""

from datetime import datetime
from typing import Protocol

from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import DeviceId, SensorId


class ReadingRepository(Protocol):
    """Reading の保存・取得を抽象化するリポジトリ.

    実装は infrastructure 層（DB/Redis/SQLite等）で行う。
    """

    def save(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
        reading: Reading,
        recorded_at: datetime,
    ) -> None:
        """1件の計測値を永続化する.

        Args:
            device_id: 計測元デバイスの識別子.
            sensor_id: Device 内のセンサ識別子.
            reading: 保存する計測値.
            recorded_at: 計測時刻（呼び出し側が指定）.
        """
        ...

    def find_latest(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
    ) -> Reading | None:
        """指定センサの最新計測値を返す.

        Args:
            device_id: 計測元デバイスの識別子.
            sensor_id: Device 内のセンサ識別子.

        Returns:
            登録があれば最新の Reading、無ければ None.
        """
        ...
