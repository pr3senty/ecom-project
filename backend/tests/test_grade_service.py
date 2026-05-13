from types import SimpleNamespace
from typing import Union
from unittest.mock import AsyncMock

import pytest

from app.domain import Student, Subject
from app.service.grade import GradeService, _parse_grades_csv


class FakeUnitOfWork:
    """Minimal unit-of-work fake that exposes repository-like objects."""

    def __init__(self, existing_students: Union[dict[int, Student], None] = None):
        self.enter_count = 0
        self.exit_count = 0
        self.students = SimpleNamespace(
            get_by_ids=AsyncMock(return_value=existing_students or {}),
            create_many=AsyncMock(),
        )
        self.grades = SimpleNamespace(
            create_many=AsyncMock(),
        )

    async def __aenter__(self):
        self.enter_count += 1
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        self.exit_count += 1


class TestParseGradesCsv:
    """Checks CSV parsing and row-level validation for grade uploads."""

    def test_valid_tab_separated_row_is_parsed(self):
        """Parses a valid tab-separated CSV row into a ParsedGrade."""
        content = (
            "ID\tName\tSurname\tPatronymic\tSubject\tGrade\n"
            "1\tIvan\tIvanov\tIvanovich\tMATH\t5\n"
        ).encode()

        grades, errors = _parse_grades_csv(content)

        assert errors == []
        assert len(grades) == 1
        assert grades[0].student.id == 1
        assert grades[0].student.name == "Ivan"
        assert grades[0].student.surname == "Ivanov"
        assert grades[0].student.patronymic == "Ivanovich"
        assert grades[0].subject == Subject.MATH
        assert grades[0].value == 5

    def test_invalid_values_are_reported(self):
        """Collects validation errors and skips invalid CSV rows."""
        content = (
            "ID,Name,Surname,Patronymic,Subject,Grade\n"
            "bad,,Ivanov,,BIOLOGY,11\n"
        ).encode()

        grades, errors = _parse_grades_csv(content)

        assert grades == []
        messages = [error.message for error in errors]
        assert "ID must be an integer" in messages
        assert "Name is required" in messages
        assert "Subject is invalid" in messages
        assert "Grade must be between 0 and 10" in messages

    def test_comma_separated_row_is_parsed(self):
        """Parses comma-separated CSV and normalizes empty patronymic to None."""
        content = (
            "ID,Name,Surname,Patronymic,Subject,Grade\n"
            "2,Petr,Petrov,,PHYSICS,4\n"
        ).encode()

        grades, errors = _parse_grades_csv(content)

        assert errors == []
        assert len(grades) == 1
        assert grades[0].student.patronymic is None


class TestImportGrades:
    """Checks grade import behavior without a real database."""

    @pytest.mark.asyncio
    async def test_same_id_with_different_full_name_is_skipped(self):
        """Skips a later row when the same student ID has a different full name."""
        content = (
            "ID,Name,Surname,Patronymic,Subject,Grade\n"
            "1,Ivan,Ivanov,,MATH,5\n"
            "1,Petr,Petrov,,MATH,4\n"
        ).encode()
        uow = FakeUnitOfWork()

        result = await GradeService(
            uow_factory=lambda: uow,
        ).import_grades(content)

        assert result.records_loaded == 1
        assert result.students == 1
        assert uow.enter_count == 1
        assert uow.exit_count == 1
        assert uow.students.get_by_ids.await_count == 1
        assert uow.students.create_many.await_count == 1
        assert uow.grades.create_many.await_count == 1
        assert len(uow.students.create_many.await_args.args[0]) == 1
        assert len(uow.grades.create_many.await_args.args[0]) == 1
        assert len(result.errors) == 1
        assert result.errors[0].message == (
            "Student ID already exists with different full name"
        )

    @pytest.mark.asyncio
    async def test_same_id_with_same_full_name_loads_multiple_grades(self):
        """Loads multiple grades for the same student when full name matches."""
        content = (
            "ID,Name,Surname,Patronymic,Subject,Grade\n"
            "1,Ivan,Ivanov,,MATH,5\n"
            "1,Ivan,Ivanov,,HISTORY,4\n"
        ).encode()
        uow = FakeUnitOfWork()

        result = await GradeService(
            uow_factory=lambda: uow,
        ).import_grades(content)

        assert result.errors == []
        assert result.records_loaded == 2
        assert result.students == 1
        assert uow.enter_count == 1
        assert uow.exit_count == 1
        assert uow.students.get_by_ids.await_count == 1
        assert uow.students.create_many.await_count == 1
        assert uow.grades.create_many.await_count == 1
        assert len(uow.students.create_many.await_args.args[0]) == 1
        assert len(uow.grades.create_many.await_args.args[0]) == 2

    @pytest.mark.asyncio
    async def test_existing_id_with_different_full_name_is_skipped(self):
        """Skips upload row when existing DB student has different full name."""
        content = (
            "ID,Name,Surname,Patronymic,Subject,Grade\n"
            "1,Petr,Petrov,,MATH,4\n"
        ).encode()
        existing_student = Student(
            id=1,
            name="Ivan",
            surname="Ivanov",
            patronymic=None,
        )

        uow = FakeUnitOfWork(existing_students={1: existing_student})

        result = await GradeService(
            uow_factory=lambda: uow,
        ).import_grades(content)

        assert result.records_loaded == 0
        assert result.students == 0
        assert uow.enter_count == 1
        assert uow.exit_count == 1
        assert uow.students.get_by_ids.await_count == 1
        assert uow.students.create_many.await_count == 0
        assert uow.grades.create_many.await_count == 0
        assert len(result.errors) == 1
