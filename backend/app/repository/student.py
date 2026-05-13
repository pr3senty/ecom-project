import asyncpg

from app.domain import Student


class StudentRepository:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get_by_ids(
        self,
        ids: list[int],
    ) -> dict[int, Student]:
        if not ids:
            return {}

        rows = await self.conn.fetch(
            """
            SELECT id, name, surname, patronymic
            FROM student
            WHERE id = ANY($1::int[])
            """,
            ids
        )

        students = [Student(**dict(row)) for row in rows]
        return {student.id: student for student in students}

    async def create_many(
        self,
        students: list[Student],
    ) -> None:
        if not students:
            return

        await self.conn.executemany(
            """
            INSERT INTO student(id, name, surname, patronymic)
            VALUES ($1, $2, $3, $4)
            """,
            [
                (student.id, student.name, student.surname, student.patronymic)
                for student in students
            ],
        )
