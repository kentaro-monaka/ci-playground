"""DB接続の管理（engine と Session factory）."""

import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def get_engine(url: str | None = None) -> Engine:
    """SQLAlchemy engine を取得する.

    Args:
        url: 接続URL. None の場合は環境変数 DATABASE_URL から取得.

    Returns:
        作成した Engine.
    """
    url = url or os.environ["DATABASE_URL"]
    return create_engine(url, echo=False)


def session_factory(engine) -> sessionmaker[Session]:
    """Session factory を返す."""
    return sessionmaker(bind=engine, expire_on_commit=False)
