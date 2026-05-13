from __future__ import annotations

from collections.abc import Callable

from app.repository.unit_of_work import UnitOfWork


class StudentService:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self.uow_factory = uow_factory

    async def get_more_than_3_twos(self) -> list[dict]:
        async with self.uow_factory() as uow:
            return await uow.grades.get_students_with_twos_count_more_than(3)

    async def get_less_than_5_twos(self) -> list[dict]:
        async with self.uow_factory() as uow:
            return await uow.grades.get_students_with_twos_count_less_than(5)
