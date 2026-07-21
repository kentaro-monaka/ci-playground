"""FieldBus を包み、失敗時に固定間隔で再試行するデコレータ."""

import time
from collections.abc import Callable
from typing import TypeVar

from ci_playground.application.ports.field_bus import FieldBus, FieldBusError
from ci_playground.domain.sensor import Reading
from ci_playground.domain.values import SensorId, SetpointId

_T = TypeVar("_T")


class RetryingFieldBus:
    """別の FieldBus を包み、FieldBusError を数回まで再試行する.

    再試行の回数と間隔は方式ごとに最適値が異なるため、外から注入する。
    最後の試行も失敗した場合は FieldBusError をそのまま送出する。
    """

    def __init__(
        self,
        inner: FieldBus,
        attempts: int = 3,
        backoff: float = 0.1,
    ) -> None:
        self._inner = inner
        self._attempts = attempts
        self._backoff = backoff

    def read_reading(self, sensor_id: SensorId) -> Reading:
        """Reading を1件読む（失敗時は再試行）."""
        return self._with_retry(lambda: self._inner.read_reading(sensor_id))

    def read_setpoint(self, setpoint_id: SetpointId) -> float:
        """Setpoint を1件読む（失敗時は再試行）."""
        return self._with_retry(lambda: self._inner.read_setpoint(setpoint_id))

    def write_setpoint(self, setpoint_id: SetpointId, value: float) -> None:
        """Setpoint を1件書く（失敗時は再試行）."""
        self._with_retry(lambda: self._inner.write_setpoint(setpoint_id, value))

    def _with_retry(self, operation: Callable[[], _T]) -> _T:
        for attempt in range(self._attempts):
            try:
                return operation()
            except FieldBusError:
                if attempt == self._attempts - 1:
                    raise
                time.sleep(self._backoff)
        raise AssertionError("到達しない")
