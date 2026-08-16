"""センサ計測値を表す値オブジェクト群.

各計測種別ごとに型を分けて単位ミスを型で検出する。
すべて frozen dataclass で不変、等価性は値ベース。
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class TemperatureReading:
    """温度の計測値（℃）.

    絶対零度（-273.15℃）未満の値は不正として生成時に拒否する。

    Attributes:
        value: 温度値（℃）。

    Raises:
        ValueError: value が -273.15℃ 未満の場合。
    """

    value: float

    def __post_init__(self) -> None:
        if self.value < -273.15:
            raise ValueError(f"絶対零度未満の温度は不正です: {self.value}")


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class VoltageReading:
    """電圧の計測値（V）.

    負値は不正として生成時に拒否する。

    Attributes:
        value: 電圧値（V）。

    Raises:
        ValueError: value が 0 未満の場合。
    """

    value: float

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"負の電圧値は不正です: {self.value}")


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class CurrentReading:
    """電流の計測値（A）.

    InfやNaNは不正として生成時に拒否する。

    Attributes:
        value: 電流値（A）。

    Raises:
        ValueError: value が InfまたはNaN。
    """

    value: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.value):
            raise ValueError(f"無限大やNaNを示す電流値は不正です: {self.value}")
