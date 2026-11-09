from pathlib import Path

import pytest

from database.types.lesson import Lesson, LessonRepository


def _exercise(directory: Path, tester: str = "int main() { return 0; }\n", tests: str = "expected: 0\n") -> None:
    directory.mkdir(parents=True)
    (directory / "tester.cpp").write_text(tester, encoding="utf-8")
    (directory / "tests.txt").write_text(tests, encoding="utf-8")


async def test_get_lessons_groups_exercises_and_parses_cases(tmp_path: Path) -> None:
    _exercise(tmp_path / "basics" / "sum", tester="report sum\n", tests="input: 1\ninput: 1\nexpected: 2\n")
    _exercise(
        tmp_path / "conditionals" / "max-of-three",
        tester="report max\n",
        tests="input: 1\ninput: 5\ninput: 3\nexpected: 5\n",
    )

    lessons = await LessonRepository(tmp_path).get_lessons()

    by_id = {lesson.id: exercises for lesson, exercises in lessons.items()}
    assert set(by_id) == {"basics", "conditionals"}
    assert Lesson(id="basics", name="Basics") in lessons
    sum_exercise = by_id["basics"][0]
    assert sum_exercise.id == "sum"
    assert sum_exercise.lesson_id == "basics"
    assert sum_exercise.tester_code == "report sum\n"
    assert sum_exercise.tests[0].inputs == ("1", "1")
    assert sum_exercise.tests[0].expected == "2"
    max_exercise = by_id["conditionals"][0]
    assert max_exercise.id == "max-of-three"
    assert max_exercise.tests[0].inputs == ("1", "5", "3")
    assert max_exercise.tests[0].expected == "5"


async def test_catalog_is_reused_after_the_first_load(tmp_path: Path) -> None:
    exercise = tmp_path / "basics" / "sum"
    _exercise(exercise, tester="report sum\n")
    repository = LessonRepository(tmp_path)
    await repository.get_lessons()
    (exercise / "tester.cpp").write_text("report changed\n", encoding="utf-8")

    loaded = await repository.get_exercise("basics", "sum")

    assert loaded.tester_code == "report sum\n"


async def test_the_same_exercise_id_can_exist_in_two_lessons(tmp_path: Path) -> None:
    _exercise(tmp_path / "basics" / "sum", tester="report sum\n", tests="input: 1\ninput: 1\nexpected: hidden-sum\n")
    _exercise(tmp_path / "conditionals" / "sum", tester="report other\n", tests="expected: hidden-other\n")
    repository = LessonRepository(tmp_path)

    basics = await repository.get_exercise("basics", "sum")
    conditionals = await repository.get_exercise("conditionals", "sum")

    assert basics.tester_code == "report sum\n"
    assert basics.tests[0].inputs == ("1", "1")
    assert basics.tests[0].expected == "hidden-sum"
    assert conditionals.tester_code == "report other\n"
    assert conditionals.tests[0].inputs == ()
    assert conditionals.tests[0].expected == "hidden-other"


async def test_numbered_folder_names_are_rejected(tmp_path: Path) -> None:
    _exercise(tmp_path / "01-basics" / "001-sum")

    with pytest.raises(ValueError, match="lowercase slug"):
        await LessonRepository(tmp_path).get_lessons()
