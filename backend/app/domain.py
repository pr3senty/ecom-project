import enum
import uuid
from typing import Union


class Subject(enum.Enum):
    MATH = "MATH"
    PHYSICS = "PHYSICS"
    HISTORY = "HISTORY"
    SOFTWARE_ENGINEERING = "SOFTWARE ENGINEERING"

class Student:

    def __init__(
            self,
            id: int,
            name: str,
            surname: str,
            patronymic: Union[str, None]
        ):
        self.id = id
        self.name = name
        self.surname = surname
        self.patronymic = patronymic

    def full_name_identity(self) -> tuple[str, str, Union[str, None]]:
        return (self.name, self.surname, self.patronymic)

    def has_same_full_name(self, other: "Student") -> bool:
        return self.full_name_identity() == other.full_name_identity()

class Grade:

    def __init__(
            self,
            id: uuid.UUID,
            student_id: int,
            subject: Subject,
            value: int
    ):
        self.id = id
        self.student_id = student_id
        self.subject = subject
        self.value = value
