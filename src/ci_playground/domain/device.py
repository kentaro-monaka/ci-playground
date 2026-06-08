from dataclasses import dataclass, field
from ci_playground.domain.values import DeviceId, SensorId
from ci_playground.domain.sensor import Sensor
from ci_playground.domain.readings import (
    TemperatureReading,
    VoltageReading,
    CurrentReading,
)

Reading = TemperatureReading | VoltageReading | CurrentReading


@dataclass(eq=False)
class Device:
    id: DeviceId
    sensors: list[Sensor] = field(default_factory=list)

    def attach_sensor(self, sensor: Sensor) -> None:
        if any(s.id == sensor.id for s in self.sensors):
            raise ValueError(f"同じSensorIdが既に登録されています:{sensor.id}")
        self.sensors.append(sensor)

    def find_sensor(self, sensor_id: SensorId) -> Sensor:
        for s in self.sensors:
            if s.id == sensor_id:
                return s
        raise KeyError(f"SensorId {sensor_id.value} は見つかりません")

    def read_all(self) -> dict[SensorId, Reading | None]:
        return {s.id: s.last_reading for s in self.sensors}

    def anomalous_sensors(self) -> list[Sensor]:
        return [s for s in self.sensors if s.is_anomalous]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Device):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
