"""サーバー（スレーブ）側の受け口のためのポート."""

from typing import Protocol

from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import SensorId, SetpointId


class ServerBusError(Exception):
    """サーバー側バス操作に失敗したことを表す例外."""


class ServerBus(Protocol):
    """サーバーの計測値公開・制御値読取を抽象化するポート.

    実装は infrastructure 層（modbus）で行う。
    """

    def publish_reading(
        self,
        sensor_id: SensorId,
        reading: Reading,
    ) -> None:
        """1件の計測値をサーバー上に公開する.

        Args:
            sensor_id: Device 内のセンサ識別子.
            reading: センサで取得した計測値.

        Raises:
            ServerBusError: 失敗（例外応答／タイムアウト／接続不可）した場合.
        """
        ...

    def read_setpoint(
        self,
        setpoint_id: SetpointId,
    ) -> float:
        """1件の制御値をサーバー上で読み込む.

        Args:
            setpoint_id: Device 内の制御値識別子.

        Returns:
            上位が書き込んだ最新の制御値.

        Raises:
            ServerBusError: 失敗（例外応答／タイムアウト／接続不可）した場合.
        """
        ...
