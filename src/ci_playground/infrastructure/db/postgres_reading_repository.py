"""PostgreSQL を使った ReadingRepository の実装."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ci_playground.domain.readings import (
    CurrentReading,
    Reading,
    TemperatureReading,
    VoltageReading,
)
from ci_playground.domain.values import DeviceId, SensorId, SensorType
from ci_playground.infrastructure.db.orm import ReadingRow

_READING_TO_SENSOR_TYPE: dict[type[Reading], SensorType] = {
    TemperatureReading: SensorType.TEMPERATURE,
    VoltageReading: SensorType.VOLTAGE,
    CurrentReading: SensorType.CURRENT,
}


class PostgresReadingRepository:
    """Reading を PostgreSQL に保存・取得する Adapter."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
        reading: Reading,
        recorded_at: datetime,
    ) -> None:
        """Reading を1件保存する."""
        with self._session_factory() as session:
            row = ReadingRow(
                device_id=device_id.value,
                sensor_id=sensor_id.value,
                sensor_type=_READING_TO_SENSOR_TYPE[type(reading)].value,
                value=reading.value,
                recorded_at=recorded_at,
            )
            session.add(row)
            session.commit()

    def find_latest(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
    ) -> Reading | None:
        """指定 device/sensor の最新の Reading を返す.

        存在しなければ None.
        """
        with self._session_factory() as session:
            stmt = (
                select(ReadingRow)
                .where(
                    ReadingRow.device_id == device_id.value,
                    ReadingRow.sensor_id == sensor_id.value,
                )
                .order_by(ReadingRow.recorded_at.desc())
                .limit(1)
            )
            row = session.execute(stmt).scalar_one_or_none()
            if row is None:
                return None
            reading_cls = _READING_TO_SENSOR_TYPE[SensorType(row.sensor_type)]
            return reading_cls(value=row.value)
