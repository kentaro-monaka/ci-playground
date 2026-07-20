"""CAN バス上の機器を模す仮想ECU（テスト用）."""

import threading
import time

import can


class VirtualEcu:
    """周期送信しつつ、指令フレームを受けたら値を更新して即座に返す機器."""

    def __init__(
        self,
        bus: can.BusABC,
        broadcasts: dict[int, int],
        commands: dict[int, int],
        period: float = 0.01,
    ) -> None:
        self._bus = bus
        self._broadcasts = dict(broadcasts)
        self._commands = dict(commands)
        self._period = period
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        """バスの監視と周期送信を開始する."""
        self._thread.start()

    def stop(self) -> None:
        """停止してスレッドの終了を待つ."""
        self._stop.set()
        self._thread.join(timeout=5)
    
    def _run(self) -> None:
        """停止されるまで、指令の受信と周期送信を続ける."""
        next_send = time.monotonic()
        while not self._stop.is_set():
            msg = self._bus.recv(timeout=self._period)
            if msg is not None and msg.arbitration_id in self._commands:
                target = self._commands[msg.arbitration_id]
                self._broadcasts[target] = int.from_bytes(msg.data[:2], "big")
                self._send(target)
            if time.monotonic() >= next_send:
                for can_id in self._broadcasts:
                    self._send(can_id)
                next_send = time.monotonic() + self._period

    def _send(self, can_id: int) -> None:
        """現在値を1本流す."""
        self._bus.send(
            can.Message(
                arbitration_id=can_id,
                data=self._broadcasts[can_id].to_bytes(2, "big"),
                is_extended_id=False,
            )
        )