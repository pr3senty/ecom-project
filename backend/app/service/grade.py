from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

import asyncpg

from app.core.csv_parser import parse_csv
from app.domain import Grade, Student, Subject
from app.repository.grade import GradeRepository
from app.repository.student import StudentRepository

if TYPE_CHECKING:
    from app.core.db import Database


EXPECTED_HEADERS = ("id", "name", "surname", "patronymic", "subject", "grade")


@dataclass(frozen=True)
class GradeImportError:
    row: Union[int, None]
    message: str


@dataclass(frozen=True)
class ParsedGrade:
    row: int
    student: Student
    subject: Subject
    value: int


@dataclass(frozen=True)
class GradeImportResult:
    status: str
    records_loaded: int
    students: int
    errors: list[GradeImportError]


def _normalize_text(value: Union[str, None]) -> str:
    return (value or "").strip()


def _normalize_patronymic(value: Union[str, None]) -> Union[str, None]:
    normalized = _normalize_text(value)
    return normalized or None


def _parse_subject(value: str) -> Union[Subject, None]:
    normalized = " ".join(value.strip().upper().split())
    for subject in Subject:
        if subject.value == normalized:
            return subject
    return None


def _parse_grades_csv(content: bytes) -> tuple[list[ParsedGrade], list[GradeImportError]]:
    parsed_csv = parse_csv(content, EXPECTED_HEADERS)
    grades: list[ParsedGrade] = []
    errors = [
        GradeImportError(error.row, error.message)
        for error in parsed_csv.errors
    ]

    for row_number, row in parsed_csv.rows:
        row_errors: list[str] = []

        try:
            student_id = int(row["id"])
        except ValueError:
            row_errors.append("ID must be an integer")
            student_id = 0

        name = row["name"]
        if not name:
            row_errors.append("Name is required")

        surname = row["surname"]
        if not surname:
            row_errors.append("Surname is required")

        patronymic = _normalize_patronymic(row["patronymic"])

        subject = _parse_subject(row["subject"])
        if subject is None:
            row_errors.append("Subject is invalid")

        try:
            value = int(row["grade"])
        except ValueError:
            row_errors.append("Grade must be an integer")
            value = 0
        else:
            if value < 0 or value > 10:
                row_errors.append("Grade must be between 0 and 10")

        if row_errors:
            errors.extend(GradeImportError(row_number, message) for message in row_errors)
            continue

        grades.append(
            ParsedGrade(
                row=row_number,
                student=Student(
                    id=student_id,
                    name=name,
                    surname=surname,
                    patronymic=patronymic,
                ),
                subject=subject,
                value=value,
            )
        )

    return grades, errors


class GradeService:
    def __init__(self, db: Database):
        self.db = db

    async def import_grades(self, content: bytes) -> GradeImportResult:
        grades, errors = _parse_grades_csv(content)
        if not grades:
            return GradeImportResult(
                status="ok",
                records_loaded=0,
                students=0,
                errors=errors,
            )

        async with self.db.transaction() as conn:
            return await self._import_parsed_grades(conn, grades, errors)

    async def _import_parsed_grades(
        self,
        conn: asyncpg.Connection,
        grades: list[ParsedGrade],
        errors: list[GradeImportError],
    ) -> GradeImportResult:
        loaded_records = 0
        loaded_student_ids: set[int] = set()
        known_students: dict[int, Student] = {}

        for parsed_grade in grades:
            student = parsed_grade.student
            known_student = known_students.get(student.id)
            if known_student is None:
                known_student = await StudentRepository.get_by_id(conn, student.id)
                if known_student is None:
                    await StudentRepository.create(conn, student)
                    known_student = student
                known_students[student.id] = known_student

            if not known_student.has_same_full_name(student):
                errors.append(
                    GradeImportError(
                        parsed_grade.row,
                        "Student ID already exists with different full name",
                    )
                )
                continue

            await GradeRepository.create(
                conn,
                Grade(
                    id=uuid.uuid4(),
                    student_id=student.id,
                    subject=parsed_grade.subject,
                    value=parsed_grade.value,
                ),
            )
            loaded_records += 1
            loaded_student_ids.add(student.id)

        return GradeImportResult(
            status="ok",
            records_loaded=loaded_records,
            students=len(loaded_student_ids),
            errors=errors,
        )
