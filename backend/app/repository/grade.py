import asyncpg

from app.domain import Grade


class GradeRepository:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def create_many(
        self,
        grades: list[Grade],
    ) -> None:
        if not grades:
            return

        await self.conn.executemany(
            """
            INSERT INTO grade(id, student_id, subject, value)
            VALUES ($1, $2, $3, $4)
            """,
            [
                (grade.id, grade.student_id, grade.subject.value, grade.value)
                for grade in grades
            ],
        )

    async def get_students_with_twos_count_more_than(
        self,
        count: int
    ) -> list[dict]:
        rows = await self.conn.fetch(
            """
            SELECT
                trim(concat_ws(' ', s.surname, s.name, s.patronymic)) AS full_name,
                COUNT(g.id) FILTER (WHERE g.value = 2)::int AS count_twos
            FROM student s
            LEFT JOIN grade g ON g.student_id = s.id
            GROUP BY s.id, s.surname, s.name, s.patronymic
            HAVING COUNT(g.id) FILTER (WHERE g.value = 2) > $1
            ORDER BY full_name
            """,
            count
        )
        return [dict(row) for row in rows]

    async def get_students_with_twos_count_less_than(
        self,
        count: int
    ) -> list[dict]:
        rows = await self.conn.fetch(
            """
            SELECT
                trim(concat_ws(' ', s.surname, s.name, s.patronymic)) AS full_name,
                COUNT(g.id) FILTER (WHERE g.value = 2)::int AS count_twos
            FROM student s
            LEFT JOIN grade g ON g.student_id = s.id
            GROUP BY s.id, s.surname, s.name, s.patronymic
            HAVING COUNT(g.id) FILTER (WHERE g.value = 2) < $1
            ORDER BY full_name
            """,
            count
        )
        return [dict(row) for row in rows]
