"""結合テスト用の共有フィクスチャ."""

from tests.support.rtu_server import modbus_server, serial_pair

__all__ = ["modbus_server", "serial_pair"]
