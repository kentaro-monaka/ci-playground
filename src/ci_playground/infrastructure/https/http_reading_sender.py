"""httpx を使った ReadingSender の実装."""

from datetime import datetime

import httpx

from ci_playground.application.ports.reading_sender import ReadingSendError
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import DeviceId, SensorId
from ci_playground.infrastructure.reading_payload import reading_to_payload


class HttpReadingSender:
    """Reading を HTTPS で外部サーバに送信する Adapter."""

    def __init__(self, base_url: str, client: httpx.Client) -> None:
        self._base_url = base_url
        self._client = client

    def send(
        self,
        device_id: DeviceId,
        sensor_id: SensorId,
        reading: Reading,
        recorded_at: datetime,
    ) -> None:
        """Reading を送信する.

        Raises:
            ReadingSendError.
        """
        payload = reading_to_payload(device_id, sensor_id, reading, recorded_at)
        try:
            response = self._client.post(self._base_url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ReadingSendError(f"Reading の送信に失敗しました: {exc}") from exc
