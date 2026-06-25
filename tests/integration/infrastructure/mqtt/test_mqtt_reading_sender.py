import os
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import pytest
from paho.mqtt.enums import CallbackAPIVersion

from ci_playground.domain.readings import TemperatureReading
from ci_playground.domain.values import DeviceId, SensorId
from ci_playground.infrastructure.mqtt.mqtt_reading_sender import MqttReadingSender


@pytest.mark.docker
class TestMqttReadingSenderIntegration:
    @pytest.fixture
    def sender(self):
        host = os.environ.get("MQTT_BROKER_HOST", "localhost")
        client = mqtt.Client(CallbackAPIVersion.VERSION2)
        client.connect(host, 1883)
        client.loop_start()
        try:
            yield MqttReadingSender(client)
        finally:
            client.loop_stop()
            client.disconnect()

    def test_send_reaches_real_broker(self, sender):
        sender.send(
            DeviceId("dev-01"),
            SensorId("sen-01"),
            TemperatureReading(25.0),
            datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
