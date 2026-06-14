import pytest

from ci_playground.infrastructure.memory.in_memory_reading_repository import (
    InMemoryFakeReadingRepository,
)
from tests.contract.reading_repository_contract import ReadingRepositoryContract


class TestInMemoryReadingRepository(ReadingRepositoryContract):
    @pytest.fixture
    def repo(self):
        return InMemoryFakeReadingRepository()
