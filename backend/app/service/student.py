from __future__ import annotations

from typing import TYPE_CHECKING

from app.repository.grade import GradeRepository

if TYPE_CHECKING:
    from app.core.db import Database


class StudentService:
    def __init__(self, db: Database):
        self.db = db

    async def get_more_than_3_twos(self) -> list[dict]:
        async with self.db.connection() as conn:
            return await GradeRepository.get_students_with_twos_count_more_than(conn, 3)

    async def get_less_than_5_twos(self) -> list[dict]:
        async with self.db.connection() as conn:
            return await GradeRepository.get_students_with_twos_count_less_than(conn, 5)
