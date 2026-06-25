import json
from datetime import datetime, timezone

import httpx
import pytest
import respx

from ci_playground.domain.readings import (
    TemperatureReading,
)
from ci_playground.domain.values import DeviceId, SensorId
from ci_playground.infrastructure.https.http_reading_sender import (
    HttpReadingSender,
    ReadingSendError,
)
from tests.contract.reading_sender_contract import ReadingSenderContract

BASE_URL = "https://example.test/readings"


class TestHttpReadingSender(ReadingSenderContract):
    @pytest.fixture
    def sender(self):
        client = httpx.Client()
        try:
            yield HttpReadingSender(BASE_URL, client)
        finally:
            client.close()

    @pytest.fixture
    def sender_ok(self):
        with respx.mock:
            respx.post(BASE_URL).mock(return_value=httpx.Response(200))
            client = httpx.Client()
            try:
                yield HttpReadingSender(BASE_URL, client)
            finally:
                client.close()

    @pytest.fixture
    def failing_sender(self):
        with respx.mock:
            respx.post(BASE_URL).mock(return_value=httpx.Response(500))
            client = httpx.Client()
            try:
                yield HttpReadingSender(BASE_URL, client)
            finally:
                client.close()

    @respx.mock
    def test_send_posts_reading_payload(self, sender):
        route = respx.post(BASE_URL).mock(return_value=httpx.Response(200))
        sender.send(
            DeviceId("dev-01"),
            SensorId("sen-01"),
            TemperatureReading(25.0),
            datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        assert route.called
        assert json.loads(route.calls.last.request.content) == {
            "device_id": "dev-01",
            "sensor_id": "sen-01",
            "type": "TEMPERATURE",
            "value": 25.0,
            "recorded_at": "2026-01-01T00:00:00+00:00",
        }

    @respx.mock
    def test_send_raises_on_connection_error(self, sender):
        respx.post(BASE_URL).mock(side_effect=httpx.ConnectError("boom"))
        with pytest.raises(ReadingSendError):
            sender.send(
                DeviceId("dev-01"),
                SensorId("sen-01"),
                TemperatureReading(25.0),
                datetime(2026, 1, 1, tzinfo=timezone.utc),
            )
