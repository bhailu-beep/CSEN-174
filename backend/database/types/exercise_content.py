import json
from pathlib import Path

from pydantic import BaseModel

from database.types.lesson import Example

CONTENT_PATH = Path(__file__).resolve().parents[2] / "content" / "exercises.json"


class ExerciseText(BaseModel):
    """Public text for one exercise. Tests are public and served separately."""

    id: str
    slug: str
    title: str
    tags: list[str]
    description: str
    examples: list[Example]
    hint: str
    starter_code: str


class LessonText(BaseModel):
    name: str
    exercises: list[ExerciseText]


class ExerciseContentRepository:
    def __init__(self, path: Path = CONTENT_PATH):
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._lessons = {lesson_id: LessonText.model_validate(body) for lesson_id, body in raw.items()}

    def get_lesson(self, lesson_id: str) -> LessonText:
        try:
            return self._lessons[lesson_id]
        except KeyError:
            raise ValueError(f"Lesson {lesson_id} not found") from None
