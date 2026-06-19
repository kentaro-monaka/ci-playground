"""Reading 送信のためのポート."""

from datetime import datetime
from typing import Protocol

from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import DeviceId, SensorId


class ReadingSendError(Exception):
    """Reading の外部サーバ送信に失敗したことを表す例外."""


class ReadingSender(Protocol):
    """Reading の送信を抽象化するポート.

    実装は infrastructure 層（HTTPS/MQTT等）で行う。
    """

    def send(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
        reading: Reading,
        recorded_at: datetime,
    ) -> None:
        """1件の計測値を送信する.

        Args:
            device_id: 計測元デバイスの識別子.
            sensor_id: Device 内のセンサ識別子.
            reading: 送信する計測値.
            recorded_at: 計測時刻（呼び出し側が指定）.

        Raises:
            ReadingSendError: 送信に失敗（非2xx／タイムアウト／接続不可）した場合.
        """
        ...
