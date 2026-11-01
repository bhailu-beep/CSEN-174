from pathlib import Path

from pydantic import BaseModel, ConfigDict

from models.tests import TestCase, parse_tests

EXERCISES_DIR = Path(__file__).resolve().parents[3] / "exercises"


class Chapter(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str


class Lesson(BaseModel):
    id: int
    name: str
    title: str
    chapter_id: int
    content: str
    starter_code: str
    tester_code: str
    tests: list[TestCase]
    solution_code: str


class LessonRepository:
    def __init__(self, exercises_dir: Path = EXERCISES_DIR):
        self.exercises_dir = exercises_dir
        # Filled on first use and reused. A lesson is (chapter id, lesson id).
        self._by_chapter: dict[Chapter, list[Lesson]] | None = None

    async def get_lessons(self) -> dict[Chapter, list[Lesson]]:
        return self._ensure_loaded()

    async def get_lesson(self, chapter_id: int, lesson_id: int) -> Lesson:
        for chapter, lessons in self._ensure_loaded().items():
            if chapter.id != chapter_id:
                continue
            for lesson in lessons:
                if lesson.id == lesson_id:
                    return lesson
            break
        raise ValueError(f"Lesson {lesson_id} not found in chapter {chapter_id}")

    def _ensure_loaded(self) -> dict[Chapter, list[Lesson]]:
        if self._by_chapter is not None:
            return self._by_chapter
        if not self.exercises_dir.is_dir():
            raise ValueError(f"Exercises directory {self.exercises_dir} not found")

        grouped: dict[Chapter, list[Lesson]] = {}

        for section in sorted(path for path in self.exercises_dir.iterdir() if path.is_dir()):
            chapter_id, name = _split_name(section.name)
            chapter = Chapter(id=chapter_id, name=name)
            lessons: list[Lesson] = []

            for exercise in sorted(path for path in section.iterdir() if path.is_dir()):
                lesson_id, name = _split_name(exercise.name)

                title, content = _read_exercise(exercise / "exercise.md")

                lesson = Lesson(
                    id=lesson_id,
                    name=name,
                    title=title,
                    chapter_id=chapter.id,
                    content=content,
                    starter_code=_read_text(exercise / "starter.cpp"),
                    tester_code=_read_text(exercise / "tester.cpp"),
                    tests=parse_tests(_read_text(exercise / "tests.txt")),
                    solution_code=_read_text(exercise / "solution.cpp"),
                )
                lessons.append(lesson)
            lessons.sort(key=lambda lesson: lesson.id)
            grouped[chapter] = lessons
        self._by_chapter = dict(sorted(grouped.items(), key=lambda item: item[0].id))
        return self._by_chapter


def _split_name(folder_name: str) -> tuple[int, str]:
    # "02-conditionals" -> id 2, name "Conditionals".
    prefix, separator, rest = folder_name.partition("-")
    if separator == "" or not prefix.isdigit() or rest == "":
        raise ValueError(f"Folder {folder_name} must look like 01-basics")
    return int(prefix), rest.replace("-", " ").title()


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"{path} is missing")
    return path.read_text(encoding="utf-8")


def _read_exercise(path: Path) -> tuple[str, str]:
    lines = _read_text(path).splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            content = "\n".join(lines[index + 1 :]).strip()
            return title, content
    raise ValueError(f"{path} is missing a title heading")
