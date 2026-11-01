from pathlib import Path

from database.types.lesson import Chapter, LessonRepository


def _exercise(
    directory: Path,
    markdown: str,
    starter: str = "int answer() { return 0; }\n",
    tester: str = "int main() { return 0; }\n",
    tests: str = "expected: 0\n",
    solution: str = "int answer() { return 0; }\n",
) -> None:
    directory.mkdir(parents=True)
    (directory / "exercise.md").write_text(markdown, encoding="utf-8")
    (directory / "starter.cpp").write_text(starter, encoding="utf-8")
    (directory / "tester.cpp").write_text(tester, encoding="utf-8")
    (directory / "tests.txt").write_text(tests, encoding="utf-8")
    (directory / "solution.cpp").write_text(solution, encoding="utf-8")


async def test_get_lessons_reads_sections_and_exercise_markdown(tmp_path: Path) -> None:
    _exercise(tmp_path / "02-conditionals" / "004-umbrella-weather", "# Umbrella Weather\n\nBring an umbrella.\n")
    _exercise(tmp_path / "01-basics" / "001-sum", "# Sum\n\nAdd two integers.\n")

    lessons = await LessonRepository(tmp_path).get_lessons()

    chapters = list(lessons)
    assert [chapter.id for chapter in chapters] == [1, 2]
    assert chapters[0] == Chapter(id=1, name="Basics")
    assert chapters[1] == Chapter(id=2, name="Conditionals")
    assert [(lesson.id, lesson.title) for lesson in lessons[chapters[0]]] == [(1, "Sum")]
    assert lessons[chapters[0]][0].content == "Add two integers."
    assert lessons[chapters[1]][0].content == "Bring an umbrella."


async def test_catalog_is_reused_after_the_first_load(tmp_path: Path) -> None:
    exercise = tmp_path / "01-basics" / "001-sum"
    _exercise(exercise, "# Sum\n\nAdd two integers.\n")
    repository = LessonRepository(tmp_path)
    await repository.get_lessons()
    (exercise / "exercise.md").write_text("# Changed\n\nNope.\n", encoding="utf-8")

    lesson = await repository.get_lesson(1, 1)

    assert lesson.title == "Sum"
    assert lesson.content == "Add two integers."


async def test_the_same_lesson_id_can_exist_in_two_chapters(tmp_path: Path) -> None:
    _exercise(
        tmp_path / "01-basics" / "001-sum",
        "# Sum\n\nAdd two integers.\n",
        starter="int sum(int a, int b) {\n}\n",
        tester="report sum\n",
        tests="input: 1\ninput: 1\nexpected: hidden-sum\n",
        solution="int sum(int a, int b) { return a + b; }\n",
    )
    _exercise(
        tmp_path / "02-conditionals" / "001-umbrella",
        "# Umbrella\n\nBring an umbrella.\n",
        starter="bool umbrella() {\n}\n",
        tester="report umbrella\n",
        tests="expected: hidden-umbrella\n",
        solution="bool umbrella() { return true; }\n",
    )
    repository = LessonRepository(tmp_path)

    basics = await repository.get_lesson(1, 1)
    conditionals = await repository.get_lesson(2, 1)

    assert basics.title == "Sum"
    assert conditionals.title == "Umbrella"
    assert "hidden-sum" not in basics.content
    assert "hidden-umbrella" not in conditionals.content
    assert "return a + b" not in basics.content
    assert "return true" not in conditionals.content
    assert basics.starter_code == "int sum(int a, int b) {\n}\n"
    assert basics.tester_code == "report sum\n"
    assert basics.tests[0].inputs == ("1", "1")
    assert basics.tests[0].expected == "hidden-sum"
    assert conditionals.starter_code == "bool umbrella() {\n}\n"
    assert conditionals.tester_code == "report umbrella\n"
    assert conditionals.tests[0].expected == "hidden-umbrella"
