import json
from datetime import datetime, timezone
from unittest.mock import Mock

import paho.mqtt.client as mqtt
import pytest

from ci_playground.application.ports.reading_sender import ReadingSendError
from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import DeviceId, SensorId
from ci_playground.infrastructure.mqtt.mqtt_reading_sender import MqttReadingSender
from tests.contract.reading_sender_contract import ReadingSenderContract


def make_client(rc=mqtt.MQTT_ERR_SUCCESS, wait_side_effect=None):
    info = Mock()
    info.rc = rc
    if wait_side_effect is not None:
        info.wait_for_publish.side_effect = wait_side_effect
    client = Mock()
    client.publish.return_value = info
    return client


class TestMqttReadingSender(ReadingSenderContract):
    def test_send_publishes_payload(self):
        client = make_client()
        sender = MqttReadingSender(client)
        sender.send(
            DeviceId("dev-01"),
            SensorId("sen-01"),
            TemperatureReading(25.0),
            datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        client.publish.assert_called_once()
        topic, payload = client.publish.call_args.args
        assert topic == "readings/dev-01/sen-01"
        assert client.publish.call_args.kwargs["qos"] == 1
        assert json.loads(payload) == {
            "device_id": "dev-01",
            "sensor_id": "sen-01",
            "type": "TEMPERATURE",
            "value": 25.0,
            "recorded_at": "2026-01-01T00:00:00+00:00",
        }

    def test_send_raises_when_wait_for_publish_fails(self):
        client = make_client(wait_side_effect=RuntimeError("boom"))
        sender = MqttReadingSender(client)
        with pytest.raises(ReadingSendError):
            sender.send(
                DeviceId("dev-01"),
                SensorId("sen-01"),
                TemperatureReading(25.0),
                datetime(2026, 1, 1, tzinfo=timezone.utc),
            )

    @pytest.fixture
    def sender_ok(self):
        return MqttReadingSender(make_client())

    @pytest.fixture
    def failing_sender(self):
        return MqttReadingSender(make_client(rc=mqtt.MQTT_ERR_NO_CONN))
