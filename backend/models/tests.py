"""Parse tests.txt and compare sandbox actuals with the expected answers."""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class TestCase:
    __test__ = False

    inputs: tuple[str, ...]
    expected: str


@dataclass(frozen=True)
class TestResult:
    __test__ = False

    passed: bool
    expected: str
    actual: str


def parse_tests(text: str) -> list[TestCase]:
    """tests.txt blocks, separated by a blank line.

    input: sunny
    input: 80
    expected: false
    """
    cases: list[TestCase] = []
    inputs: list[str] = []
    expected: str | None = None
    started = False

    def flush() -> None:
        nonlocal expected, started
        if not started:
            return
        if expected is None:
            raise ValueError("Each test needs an expected value.")
        cases.append(TestCase(inputs=tuple(inputs), expected=expected))
        inputs.clear()
        expected = None
        started = False

    for line in text.splitlines():
        if line.endswith("\r"):
            line = line[:-1]
        if line == "":
            flush()
            continue
        if line.startswith("#"):
            continue
        if line.startswith("input: "):
            inputs.append(line.removeprefix("input: "))
            started = True
            continue
        if line.startswith("expected: "):
            expected = line.removeprefix("expected: ")
            started = True
            continue
        raise ValueError(f"Unrecognized test line: {line}")

    flush()
    return cases


def sandbox_tests(cases: list[TestCase]) -> str:
    """The file mounted into the container: inputs only, in the same order."""
    blocks: list[str] = []
    for case in cases:
        lines = [f"input: {value}" for value in case.inputs]
        # A case with no arguments still needs a block, or the blank line disappears.
        blocks.append("\n".join(lines) if lines else "case")
    if not blocks:
        return ""
    return "\n\n".join(blocks) + "\n"


def score(cases: list[TestCase], stdout: str) -> list[TestResult]:
    """Pair cases with {"actual"} lines in order. Other stdout is ignored."""
    actuals: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and isinstance(payload.get("actual"), str):
            actuals.append(payload["actual"])

    results: list[TestResult] = []
    for index, case in enumerate(cases):
        found = index < len(actuals)
        actual = actuals[index] if found else ""
        results.append(
            TestResult(
                passed=found and actual == case.expected,
                expected=case.expected,
                actual=actual,
            )
        )
    return results
