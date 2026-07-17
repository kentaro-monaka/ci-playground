"""フィールドバス経由の計測値読み取り・制御値読み書きのためのポート."""

from typing import Protocol

from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import SensorId, SetpointId


class FieldBusError(Exception):
    """計測値・計測値の読み書きに失敗したことを表す例外."""


class FieldBus(Protocol):
    """計測値読み取り・制御値の読み書きを抽象化するポート.

    実装は infrastructure 層（modbus）で行う。
    """

    def read_reading(
        self,
        sensor_id: SensorId,
    ) -> Reading:
        """1件の計測値を読む.

        Args:
            sensor_id: Device 内のセンサ識別子.

        Returns:
            指定センサの最新の計測値.

        Raises:
            FieldBusError: 失敗（例外応答／タイムアウト／接続不可）した場合.
        """
        ...

    def write_setpoint(
        self,
        setpoint_id: SetpointId,
        value: float,
    ) -> None:
        """1件の制御値を書き込む.

        Args:
            setpoint_id: Device 内の制御値識別子.
            value: 制御値.

        Raises:
            FieldBusError: 失敗（例外応答／タイムアウト／接続不可）した場合.
        """
        ...

    def read_setpoint(
        self,
        setpoint_id: SetpointId,
    ) -> float:
        """1件の制御値を読み込む.

        Args:
            setpoint_id: Device 内の制御値識別子.

        Returns:
            現在設定されている制御値.

        Raises:
            FieldBusError: 失敗（例外応答／タイムアウト／接続不可）した場合.
        """
        ...
