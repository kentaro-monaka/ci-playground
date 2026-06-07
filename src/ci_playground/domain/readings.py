from dataclasses import dataclass
import math


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class TemperatureReading:
    value: float

    def __post_init__(self):
        if self.value < -273.15:
            raise ValueError(f"絶対零度未満の温度は不正です: {self.value}")


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class VoltageReading:
    value: float

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"負の電圧値は不正です: {self.value}")


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class CurrentReading:
    value: float

    def __post_init__(self):
        if not math.isfinite(self.value):
            raise ValueError(f"無限大やNaNを示す電流値は不正です: {self.value}")
