"""paho-mqtt を使った ReadingSender の実装."""

import json
from datetime import datetime

import paho.mqtt.client as mqtt

from ci_playground.application.ports.reading_sender import ReadingSendError
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import DeviceId, SensorId
from ci_playground.infrastructure.reading_payload import reading_to_payload


class MqttReadingSender:
    """Reading を MQTT で外部ブローカに送信する Adapter."""

    def __init__(self, client: mqtt.Client) -> None:
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
        topic = f"readings/{device_id.value}/{sensor_id.value}"
        payload = json.dumps(
            reading_to_payload(device_id, sensor_id, reading, recorded_at)
        )
        info = self._client.publish(topic, payload, qos=1)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            raise ReadingSendError(f"publish に失敗しました (rc={info.rc})")
        try:
            info.wait_for_publish(timeout=5.0)
        except (RuntimeError, ValueError) as exc:
            raise ReadingSendError(f"publish の確認に失敗しました: {exc}") from exc
