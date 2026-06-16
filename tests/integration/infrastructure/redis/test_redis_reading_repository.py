import os

import pytest
import redis

from ci_playground.infrastructure.redis.redis_reading_repository import (
    RedisReadingRepository,
)
from tests.contract.reading_repository_contract import ReadingRepositoryContract

DEFAULT_REDIS_URL = "redis://localhost:6379/0"


@pytest.mark.docker
class TestRedisReadingRepository(ReadingRepositoryContract):
    @pytest.fixture
    def repo(self):
        # 環境変数があればそれを使う（CIで差し替え可能）。なければローカルcompose
        url = os.environ.get("REDIS_URL", DEFAULT_REDIS_URL)
        client = redis.Redis.from_url(url, decode_responses=True)
        client.flushdb()
        try:
            yield RedisReadingRepository(client)
        finally:
            client.close()
