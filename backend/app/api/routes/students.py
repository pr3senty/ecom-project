from fastapi import APIRouter

from app.api.dependencies import StudentServiceDep


router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/more-than-3-twos")
async def get_more_than_3_twos(student_service: StudentServiceDep):
    return await student_service.get_more_than_3_twos()


@router.get("/less-than-5-twos")
async def get_less_than_5_twos(student_service: StudentServiceDep):
    return await student_service.get_less_than_5_twos()
