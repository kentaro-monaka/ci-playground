import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from ci_playground.infrastructure.db.connection import session_factory
from ci_playground.infrastructure.db.orm import Base
from ci_playground.infrastructure.db.sqlalchemy_reading_repository import (
    SqlAlchemyReadingRepository,
)
from tests.contract.reading_repository_contract import ReadingRepositoryContract


class TestSqliteReadingRepository(ReadingRepositoryContract):
    @pytest.fixture
    def repo(self):
        # 一本の接続を使いまわす in-memory SQLite（接続ごと別DB問題を回避）
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        # ORM 定義から reading テーブルを作成
        Base.metadata.create_all(engine)
        # 本番と同じ session factory を再利用して Repository を組み立てる
        try:
            yield SqlAlchemyReadingRepository(session_factory(engine))
        finally:
            engine.dispose()
