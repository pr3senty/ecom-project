from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Union

from app.repository.grade import GradeRepository
from app.repository.student import StudentRepository

if TYPE_CHECKING:
    from app.core.db import Database


class UnitOfWork:
    def __init__(self, db: Database):
        self.db = db

    async def __aenter__(self) -> UnitOfWork:
        self._transaction = self.db.transaction()
        conn = await self._transaction.__aenter__()

        self.students = StudentRepository(conn)
        self.grades = GradeRepository(conn)

        return self

    async def __aexit__(
        self,
        exc_type: Union[type[BaseException], None],
        exc: Union[BaseException, None],
        traceback: Union[TracebackType, None],
    ) -> Union[bool, None]:
        return await self._transaction.__aexit__(exc_type, exc, traceback)
