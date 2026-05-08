from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from typing import Union

from app.api.dependencies import GradeServiceDep
from app.service.grade import GradeImportResult


router = APIRouter()


class UploadError(BaseModel):
    row: Union[int, None]
    message: str


class UploadResult(BaseModel):
    status: str
    records_loaded: int
    students: int
    errors: list[UploadError]


def _to_upload_result(result: GradeImportResult) -> UploadResult:
    return UploadResult(
        status=result.status,
        records_loaded=result.records_loaded,
        students=result.students,
        errors=[
            UploadError(row=error.row, message=error.message)
            for error in result.errors
        ],
    )


@router.post("/upload-grades", response_model=UploadResult)
async def upload_grades(
    grade_service: GradeServiceDep,
    file: UploadFile = File(...),
):
    content = await file.read()
    result = await grade_service.import_grades(content)

    return _to_upload_result(result)
