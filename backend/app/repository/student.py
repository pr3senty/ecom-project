import asyncpg
from typing import Union

from app.domain import Student


class StudentRepository:

    @staticmethod
    async def get_by_id(
        conn: asyncpg.Connection,
        id: int
    ) -> Union[Student, None]:
        row = await conn.fetchrow(
            """
            SELECT id, name, surname, patronymic
            FROM student
            WHERE id = $1
            """,
            id
        )

        return Student(**dict(row)) if row else None
    
    @staticmethod
    async def create(
        conn: asyncpg.Connection,
        student: Student
    ) -> int:
        return await conn.fetchval(
            """
            INSERT INTO student(id, name, surname, patronymic) 
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            student.id, student.name, student.surname, student.patronymic
        )