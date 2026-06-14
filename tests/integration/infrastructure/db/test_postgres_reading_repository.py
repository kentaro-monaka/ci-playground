import os

import pytest
from sqlalchemy import create_engine

from ci_playground.infrastructure.db.connection import session_factory
from ci_playground.infrastructure.db.orm import Base
from ci_playground.infrastructure.db.sqlalchemy_reading_repository import (
    SqlAlchemyReadingRepository,
)
from tests.contract.reading_repository_contract import ReadingRepositoryContract

DEFAULT_DATABASE_URL = "postgresql+psycopg://ci:ci@localhost:5432/ci_playground"


@pytest.mark.docker
class TestPostgresReadingRepository(ReadingRepositoryContract):
    @pytest.fixture
    def repo(self):
        # 環境変数があればそれを使う（CIで差し替え可能）。なければローカルcompose
        url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
        engine = create_engine(url)
        # 実DBは永続するので、毎テスト空スキーマから始める
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        try:
            yield SqlAlchemyReadingRepository(session_factory(engine))
        finally:
            engine.dispose()
