"""Redis を使った ReadingRepository の実装."""

import json
from datetime import datetime

import redis

from ci_playground.domain.reading_types import (
    READING_TO_SENSOR_TYPE,
    SENSOR_TYPE_TO_READING,
)
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import DeviceId, SensorId, SensorType


def create_key(device_id: DeviceId, sensor_id: SensorId) -> str:
    """Reading 保存用の Redis キーを組み立てる."""
    return f"reading:{device_id.value}:{sensor_id.value}"


class RedisReadingRepository:
    """Reading を Redis に保存・取得する Adapter."""

    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    def save(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
        reading: Reading,
        recorded_at: datetime,
    ) -> None:
        """Reading を1件保存する."""
        key = create_key(device_id, sensor_id)
        member = json.dumps(
            {
                "type": READING_TO_SENSOR_TYPE[type(reading)].value,
                "value": reading.value,
            }
        )
        score = recorded_at.timestamp()
        self._client.zadd(key, {member: score})

    def find_latest(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
    ) -> Reading | None:
        """指定 device/sensor の最新の Reading を返す.

        存在しなければ None.
        """
        key = create_key(device_id, sensor_id)
        rows = self._client.zrange(key, 0, 0, desc=True)
        if not rows:
            return None
        member = rows[0]
        assert isinstance(member, (str, bytes))
        payload = json.loads(member)
        reading_cls = SENSOR_TYPE_TO_READING[SensorType(payload["type"])]
        return reading_cls(value=payload["value"])
