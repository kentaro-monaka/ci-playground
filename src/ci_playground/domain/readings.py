from dataclasses import dataclass


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class TemperatureReading:
    value: float

    def __post_init__(self):
        if self.value < -273.15:
            raise ValueError(f"絶対零度未満の温度は不正です: {self.value}")
