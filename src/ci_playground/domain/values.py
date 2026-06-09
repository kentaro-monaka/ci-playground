"""センサ属性値を表す値オブジェクト群.

センサ生成時に範囲を指定して範囲チェック。
すべて frozen dataclass で不変、等価性は値ベース。
"""

from dataclasses import dataclass
from enum import StrEnum


class SensorType(StrEnum):
    """センサ種別の列挙（温度・電圧・電流）."""

    TEMPERATURE = "TEMPERATURE"
    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class Range:
    """閉区間として動作する許容範囲.

    min > maxの場合は不正として生成時に拒否する。

    Attributes:
        min: 範囲の下限値（境界を含む）.
        max: 範囲の上限値（境界を含む）.

    Raises:
        ValueError: minがmaxを超える場合
    """

    min: float
    max: float

    def __post_init__(self):
        if self.min > self.max:
            raise ValueError(
                f"最小値が最大値より大きい min: {self.min}, max: {self.max}"
            )

    def contains(self, value: float) -> bool:
        """値が許容範囲内（閉区間）かを判定.

        Args:
            value: 判定対象の値.

        Returns:
            min <= value <= max のとき True.
        """
        return self.min <= value <= self.max


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class SensorId:
    """Device 内でローカルに一意なSensor識別子.

    空文字・空白の場合は不正として生成時に拒否する。

    Attributes:
        value: 識別子.

    Raises:
        ValueError: 空文字・空白の場合
    """

    value: str

    def __post_init__(self):
        if self.value.strip() == "":
            raise ValueError(f"sensor_id 空文字のためエラー: {self.value}")


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class DeviceId:
    """1台の物理 Device の識別子.

    空文字・空白の場合は不正として生成時に拒否する。

    Attributes:
        value: 識別子.

    Raises:
        ValueError: 空文字・空白の場合
    """

    value: str

    def __post_init__(self):
        if self.value.strip() == "":
            raise ValueError(f"device_id 空文字のためエラー: {self.value}")
