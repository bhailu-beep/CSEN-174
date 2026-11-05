from typing import Annotated

from fastapi import APIRouter, Depends

from database.types.lesson import LessonOverview
from database.types.user import User
from dependencies import get_current_user, get_lesson_service
from services.lesson import LessonService

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/")
async def get_lessons(
    user: Annotated[User, Depends(get_current_user)],
    lessons: Annotated[LessonService, Depends(get_lesson_service)],
) -> list[LessonOverview]:
    return await lessons.get_lessons(user.id)
