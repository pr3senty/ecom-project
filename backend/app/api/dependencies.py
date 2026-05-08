from typing import Annotated

from fastapi import Depends

from app.core.db import Database, db
from app.service.grade import GradeService
from app.service.student import StudentService


def get_database() -> Database:
    return db


def get_grade_service(
    database: Annotated[Database, Depends(get_database)],
) -> GradeService:
    return GradeService(database)


def get_student_service(
    database: Annotated[Database, Depends(get_database)],
) -> StudentService:
    return StudentService(database)


GradeServiceDep = Annotated[GradeService, Depends(get_grade_service)]
StudentServiceDep = Annotated[StudentService, Depends(get_student_service)]
