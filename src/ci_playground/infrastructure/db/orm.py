"""SQLAlchemy declarative model群（DBスキーマ）.

ドメイン層の型とは別の、DB一対一マッピング用のクラスを置く。
変換は infrastructure/db/postgres_reading_repository.py で行う。
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative の基底クラス."""


class ReadingRow(Base):
    """計測値レコード（readings テーブル）.

    ドメインの Reading 系（TemperatureReading 等）の永続化形。
    sensor_type で種別を区別する。
    """

    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64))
    sensor_id: Mapped[str] = mapped_column(String(64))
    sensor_type: Mapped[str] = mapped_column(String(16))
    # 'TEMPERATURE' / 'VOLTAGE' / 'CURRENT'
    value: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index(
            "idx_readings_sensor_time",
            "device_id",
            "sensor_id",
            "recorded_at",
        ),
    )
