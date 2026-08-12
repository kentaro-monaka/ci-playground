import pytest
from sqlalchemy import create_engine

from ci_playground.composition_root import build_aux_composition
from ci_playground.domain.readings import TemperatureReading
from ci_playground.infrastructure.db.connection import session_factory
from ci_playground.infrastructure.db.orm import Base
from ci_playground.infrastructure.db.sqlalchemy_reading_repository import (
    SqlAlchemyReadingRepository,
)


@pytest.mark.docker  # MQTTブローカーが要るため
def test_aux_composition_collects_and_sends(monkeypatch, modbus_server, tmp_path):
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    engine.dispose()

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("RTU_AUX_PORT", modbus_server)

    composition = build_aux_composition()
    sensor_id = composition.device.sensors[0].id

    composition.collect_readings.execute(composition.device)

    # 実機(疑似シミュレータ)から読んだ値が正しく反映されているか
    assert composition.device.sensors[0].last_reading == TemperatureReading(25.0)

    # DBに保存された値を、テスト側から独立して確認する
    repository = SqlAlchemyReadingRepository(session_factory(engine))
    saved = repository.find_latest(composition.device.id, sensor_id)
    assert saved == TemperatureReading(25.0)

    composition.send_readings.execute(composition.device.id, sensor_id)
    engine.dispose()
