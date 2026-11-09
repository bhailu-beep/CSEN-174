import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from models.tests import TestCase, parse_tests

EXERCISES_DIR = Path(__file__).resolve().parents[3] / "exercises"
_SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class Lesson(BaseModel):
    """A group of exercises, one folder under exercises/ (for example basics)."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str


class LessonOverview(BaseModel):
    """One lesson on the dashboard: how many exercises it has, and how many this user has completed."""

    id: str
    name: str
    exercise_count: int
    completed_count: int


class Exercise(BaseModel):
    """One function problem. Identified with its lesson, not by a global number."""

    id: str
    lesson_id: str
    tester_code: str
    tests: list[TestCase]


class LessonRepository:
    def __init__(self, exercises_dir: Path = EXERCISES_DIR):
        self.exercises_dir = exercises_dir
        # Filled on first use and reused. An exercise is (lesson id, exercise id).
        self._by_lesson: dict[Lesson, list[Exercise]] | None = None

    async def get_lessons(self) -> dict[Lesson, list[Exercise]]:
        return self._ensure_loaded()

    async def get_exercise(self, lesson_id: str, exercise_id: str) -> Exercise:
        for lesson, exercises in self._ensure_loaded().items():
            if lesson.id != lesson_id:
                continue
            for exercise in exercises:
                if exercise.id == exercise_id:
                    return exercise
            break
        raise ValueError(f"Exercise {exercise_id} not found in lesson {lesson_id}")

    def _ensure_loaded(self) -> dict[Lesson, list[Exercise]]:
        if self._by_lesson is not None:
            return self._by_lesson
        if not self.exercises_dir.is_dir():
            raise ValueError(f"Exercises directory {self.exercises_dir} not found")

        grouped: dict[Lesson, list[Exercise]] = {}

        for lesson_dir in sorted(path for path in self.exercises_dir.iterdir() if path.is_dir()):
            lesson_id = _slug(lesson_dir.name)
            lesson = Lesson(id=lesson_id, name=_display_name(lesson_id))
            exercises: list[Exercise] = []

            for exercise_dir in sorted(path for path in lesson_dir.iterdir() if path.is_dir()):
                exercise_id = _slug(exercise_dir.name)
                exercises.append(
                    Exercise(
                        id=exercise_id,
                        lesson_id=lesson.id,
                        tester_code=_read_text(exercise_dir / "tester.cpp"),
                        tests=parse_tests(_read_text(exercise_dir / "tests.txt")),
                    )
                )
            grouped[lesson] = exercises
        self._by_lesson = grouped
        return self._by_lesson


def _slug(folder_name: str) -> str:
    if _SLUG.fullmatch(folder_name) is None:
        raise ValueError(f"Folder {folder_name} must be a lowercase slug like basics or sum")
    return folder_name


def _display_name(slug: str) -> str:
    return slug.replace("-", " ").title()


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"{path} is missing")
    return path.read_text(encoding="utf-8")
