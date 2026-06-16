import fakeredis
import pytest

from ci_playground.infrastructure.redis.redis_reading_repository import (
    RedisReadingRepository,
)
from tests.contract.reading_repository_contract import ReadingRepositoryContract


class TestFakeRedisReadingRepository(ReadingRepositoryContract):
    @pytest.fixture
    def repo(self):
        client = fakeredis.FakeRedis(decode_responses=True)
        client.flushall()
        return RedisReadingRepository(client)
