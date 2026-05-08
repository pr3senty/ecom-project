from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest

from app.service.student import StudentService


class FakeDatabase:
    """Minimal async database fake that records connection usage."""

    def __init__(self):
        self.conn = AsyncMock()
        self.connection_count = 0

    @asynccontextmanager
    async def connection(self):
        self.connection_count += 1
        yield self.conn


class TestStudentService:
    """Checks student analytics service delegation to SQL repositories."""

    @pytest.mark.asyncio
    async def test_get_more_than_3_twos_uses_repository_with_threshold(self):
        """Returns students with more than three twos using threshold 3."""
        database = FakeDatabase()
        expected = [{"full_name": "Ivanov Ivan", "count_twos": 5}]

        with patch(
            "app.service.student.GradeRepository.get_students_with_twos_count_more_than",
            new=AsyncMock(return_value=expected),
        ) as get_more_than:
            result = await StudentService(database).get_more_than_3_twos()

        assert result == expected
        assert database.connection_count == 1
        get_more_than.assert_awaited_once_with(database.conn, 3)

    @pytest.mark.asyncio
    async def test_get_less_than_5_twos_uses_repository_with_threshold(self):
        """Returns students with fewer than five twos using threshold 5."""
        database = FakeDatabase()
        expected = [{"full_name": "Petrov Petr", "count_twos": 2}]

        with patch(
            "app.service.student.GradeRepository.get_students_with_twos_count_less_than",
            new=AsyncMock(return_value=expected),
        ) as get_less_than:
            result = await StudentService(database).get_less_than_5_twos()

        assert result == expected
        assert database.connection_count == 1
        get_less_than.assert_awaited_once_with(database.conn, 5)
