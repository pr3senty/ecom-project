import asyncpg

from app.domain import Grade


class GradeRepository:

    @staticmethod
    async def get_all_by_student_id(
        conn: asyncpg.Connection,
        student_id: int
    ):
        rows = await conn.fetch(
            """
            SELECT id, student_id, subject, value
            FROM grade
            WHERE student_id = $1
            """,
            student_id
        )
        return rows

    @staticmethod
    async def create(
        conn: asyncpg.Connection,
        grade: Grade
    ) -> None:
        await conn.execute(
            """
            INSERT INTO grade(id, student_id, subject, value)
            VALUES ($1, $2, $3, $4)
            """,
            grade.id, grade.student_id, grade.subject.value, grade.value
        )

    @staticmethod
    async def get_students_with_twos_count_more_than(
        conn: asyncpg.Connection,
        count: int
    ) -> list[dict]:
        rows = await conn.fetch(
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

    @staticmethod
    async def get_students_with_twos_count_less_than(
        conn: asyncpg.Connection,
        count: int
    ) -> list[dict]:
        rows = await conn.fetch(
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
