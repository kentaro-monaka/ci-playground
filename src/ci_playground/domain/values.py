from dataclasses import dataclass
from enum import StrEnum


class SensorType(StrEnum):
    TEMPERATURE = "TEMPERATURE"
    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class Range:
    min: float
    max: float

    def __post_init__(self):
        if self.min > self.max:
            raise ValueError(
                f"最小値が最大値より大きい min: {self.min}, max: {self.max}"
            )

    def contains(self, value: float) -> bool:
        return self.min <= value <= self.max


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class SensorId:
    value: str

    def __post_init__(self):
        if self.value.strip() == "":
            raise ValueError(f"sensor_id 空文字のためエラー: {self.value}")


@dataclass(frozen=True)  # 不変 + 自動で __eq__/__hash__/__repr__ を生成
class DeviceId:
    value: str

    def __post_init__(self):
        if self.value.strip() == "":
            raise ValueError(f"device_id 空文字のためエラー: {self.value}")
