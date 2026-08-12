"""デバイス集約ルート.

1つの機器に複数のセンサーを追加することができる
"""

from dataclasses import dataclass, field

from ci_playground.domain.readings import (
    CurrentReading,
    TemperatureReading,
    VoltageReading,
)
from ci_playground.domain.sensor import Sensor
from ci_playground.domain.values import DeviceId, Range, SensorId, SetpointId

Reading = TemperatureReading | VoltageReading | CurrentReading


@dataclass(eq=False)
class Device:
    """1台の物理機器を表す集約ルート.

    複数の Sensor を内包し、SensorId の重複を許さない（DeviceId 基準で等価）。

    Attributes:
        id: 1台の物理機器を識別するID.
        sensors: この機器に紐付くセンサのリスト.
        setpoint_ranges: この機器の各制御値の範囲.
    """

    id: DeviceId
    sensors: list[Sensor] = field(default_factory=list)
    setpoint_ranges: dict[SetpointId, Range] = field(default_factory=dict)

    def attach_sensor(self, sensor: Sensor) -> None:
        """機器にセンサを追加する.

        Args:
            sensor: 追加するセンサ。SensorIdに重複がない場合のみ追加できる。

        Raises:
            ValueError: SensorId が既に同一機器に登録されている場合
        """
        if any(s.id == sensor.id for s in self.sensors):
            raise ValueError(f"同じSensorIdが既に登録されています:{sensor.id}")
        self.sensors.append(sensor)

    def find_sensor(self, sensor_id: SensorId) -> Sensor:
        """SensorId に一致するセンサを返す.

        Args:
            sensor_id: 検索するセンサ識別子。

        Raises:
            KeyError: SensorId がデバイス内に見つかれない場合

        Returns:
            機器に登録されたセンサの中にsensor_idと一致するものがあるとセンサエンティティを返す.
        """
        for s in self.sensors:
            if s.id == sensor_id:
                return s
        raise KeyError(f"SensorId {sensor_id.value} は見つかりません")

    def read_all(self) -> dict[SensorId, Reading | None]:
        """全センサの最新計測値を辞書で返す.

        Returns:
            センサIDと最新読み値の辞書.
        """
        return {s.id: s.last_reading for s in self.sensors}

    def anomalous_sensors(self) -> list[Sensor]:
        """許容範囲外の計測値を持つセンサだけ返す.

        Returns:
            最新読み値が許容範囲外になっているセンサのList.
        """
        return [s for s in self.sensors if s.is_anomalous]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Device):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
