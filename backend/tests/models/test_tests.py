from pathlib import Path

import pytest

from models.tests import TestResult, parse_tests, sandbox_tests, score

UMBRELLA_TESTS = (
    Path(__file__).resolve().parents[3]
    / "exercises"
    / "02-conditionals"
    / "004-umbrella-weather"
    / "tests.txt"
)


def test_score_keeps_each_case_independent() -> None:
    cases = parse_tests(
        "input: 1\n"
        "input: 2\n"
        "expected: 3\n"
        "\n"
        "input: -1\n"
        "input: 5\n"
        "expected: 4\n"
        "\n"
        "input: 0\n"
        "input: 0\n"
        "expected: \n"
    )
    stdout = "not json\n" '{"actual":"3"}\n' '{"actual":"0"}\n'

    assert score(cases, stdout) == [
        TestResult(passed=True, expected="3", actual="3"),
        TestResult(passed=False, expected="4", actual="0"),
        TestResult(passed=False, expected="", actual=""),
    ]
    sandbox = sandbox_tests(cases)
    assert "expected" not in sandbox
    assert "name" not in sandbox


def test_umbrella_tests_file_lists_inputs_and_expected_answers() -> None:
    cases = parse_tests(UMBRELLA_TESTS.read_text(encoding="utf-8"))

    assert [(case.inputs, case.expected) for case in cases[:2]] == [
        (("sunny", "80"), "false"),
        (("sunny", "25"), "false"),
    ]
    assert cases[-1].inputs == ("hail", "0")
    assert cases[-1].expected == "true"
    assert "expected" not in sandbox_tests(cases)


def test_parse_tests_rejects_a_case_without_an_expected_value() -> None:
    with pytest.raises(ValueError):
        parse_tests("input: 1\n")
