import pytest

from models.tests import TestResult, parse_tests, sandbox_tests, score


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


def test_parse_tests_rejects_a_case_without_an_expected_value() -> None:
    with pytest.raises(ValueError):
        parse_tests("input: 1\n")
