"""init tables

Revision ID: 71be6892c828
Revises: 
Create Date: 2026-05-08 12:05:04.372201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71be6892c828'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TYPE subject_enum AS ENUM (
            'MATH',
            'PHYSICS',
            'HISTORY',
            'SOFTWARE ENGINEERING'
        );
        CREATE TABLE student (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            surname VARCHAR(100) NOT NULL,
            patronymic VARCHAR(100)
        );
        CREATE TABLE grade (
            id UUID PRIMARY KEY,
            student_id INT NOT NULL,
            subject subject_enum NOT NULL,
            value INT NOT NULL CHECK (value BETWEEN 0 AND 10),

            CONSTRAINT fk_grade_student
                FOREIGN KEY (student_id)
                REFERENCES student(id)
                ON DELETE CASCADE
        );
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP TABLE IF EXISTS grade;
        DROP TABLE IF EXISTS student;
        DROP TYPE IF EXISTS subject_enum;
        """
    )
