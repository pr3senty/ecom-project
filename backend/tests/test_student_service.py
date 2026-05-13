from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.service.student import StudentService


class FakeUnitOfWork:
    """Minimal unit-of-work fake that exposes grade repository methods."""

    def __init__(self):
        self.enter_count = 0
        self.exit_count = 0
        self.grades = SimpleNamespace(
            get_students_with_twos_count_more_than=AsyncMock(),
            get_students_with_twos_count_less_than=AsyncMock(),
        )

    async def __aenter__(self):
        self.enter_count += 1
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        self.exit_count += 1


class TestStudentService:
    """Checks student analytics service delegation to SQL repositories."""

    @pytest.mark.asyncio
    async def test_get_more_than_3_twos_uses_repository_with_threshold(self):
        """Returns students with more than three twos using threshold 3."""
        uow = FakeUnitOfWork()
        expected = [{"full_name": "Ivanov Ivan", "count_twos": 5}]
        uow.grades.get_students_with_twos_count_more_than.return_value = expected

        result = await StudentService(
            uow_factory=lambda: uow,
        ).get_more_than_3_twos()

        assert result == expected
        assert uow.enter_count == 1
        assert uow.exit_count == 1
        uow.grades.get_students_with_twos_count_more_than.assert_awaited_once_with(3)

    @pytest.mark.asyncio
    async def test_get_less_than_5_twos_uses_repository_with_threshold(self):
        """Returns students with fewer than five twos using threshold 5."""
        uow = FakeUnitOfWork()
        expected = [{"full_name": "Petrov Petr", "count_twos": 2}]
        uow.grades.get_students_with_twos_count_less_than.return_value = expected

        result = await StudentService(
            uow_factory=lambda: uow,
        ).get_less_than_5_twos()

        assert result == expected
        assert uow.enter_count == 1
        assert uow.exit_count == 1
        uow.grades.get_students_with_twos_count_less_than.assert_awaited_once_with(5)
