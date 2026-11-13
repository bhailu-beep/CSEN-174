from typing import Annotated

from config import MAX_SOURCE_BYTES
from database.types.lesson import LessonOverview, TestCase
from database.types.lesson_progress import ExerciseProgress
from database.types.user import User
from dependencies import (get_current_user, get_lesson_progress_service,
                          get_lesson_service)
from fastapi import APIRouter, Depends, HTTPException
from models.result import SubmissionResult
from pydantic import BaseModel, Field
from services.lesson import LessonService
from services.lesson_progress import LessonProgressService

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/")
async def get_lessons(
    user: Annotated[User, Depends(get_current_user)],
    lessons: Annotated[LessonService, Depends(get_lesson_service)],
) -> list[LessonOverview]:
    return await lessons.get_lessons(user.id)

@router.get("/{lesson_id}/progress")
async def get_lesson_progress(
    user: Annotated[User, Depends(get_current_user)],
    lesson_id: str,
    lesson_progress_service: Annotated[LessonProgressService, Depends(get_lesson_progress_service)],
) -> list[ExerciseProgress]:
    try:
        return await lesson_progress_service.get_lesson_progress(user.id, lesson_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.get("/{lesson_id}/exercises/{exercise_id}/tests")
async def get_tests(
    lesson_id: str,
    exercise_id: str,
    lessons: Annotated[LessonService, Depends(get_lesson_service)],
) -> list[TestCase]:
    tests = await lessons.get_tests(lesson_id, exercise_id)
    if tests is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return tests

@router.get("/{lesson_id}/exercises/{exercise_id}/code")
async def get_code(
    user: Annotated[User, Depends(get_current_user)],
    lesson_id: str,
    exercise_id: str,
    lesson_progress_service: Annotated[LessonProgressService, Depends(get_lesson_progress_service)],
) -> str:
    try:
        code = await lesson_progress_service.get_code(user.id, lesson_id, exercise_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if code is None:
        return ""
    return code

class SaveCodeRequest(BaseModel):
    # Same cap the runner applies to submitted source, so saved code can always be run.
    code: str = Field(max_length=MAX_SOURCE_BYTES)


@router.put("/{lesson_id}/exercises/{exercise_id}/code")
async def update_code(
    user: Annotated[User, Depends(get_current_user)],
    lesson_id: str,
    exercise_id: str,
    body: SaveCodeRequest,
    lesson_progress_service: Annotated[LessonProgressService, Depends(get_lesson_progress_service)],
) -> None:
    try:
        await lesson_progress_service.update_code(user.id, lesson_id, exercise_id, body.code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class RunCodeRequest(BaseModel):
    code: str


@router.post("/{lesson_id}/exercises/{exercise_id}/run")
async def run_code(
    lesson_id: str,
    exercise_id: str,
    body: RunCodeRequest,
    user: Annotated[User, Depends(get_current_user)],
    lessons: Annotated[LessonService, Depends(get_lesson_service)],
) -> SubmissionResult:
    try:
        return await lessons.run_code(user.id, lesson_id, exercise_id, body.code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

