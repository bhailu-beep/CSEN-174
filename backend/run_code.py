"""Compile and run untrusted C++ in a locked-down Docker container."""

from runner import RunResult, Stage, run_cpp

__all__ = ["RunResult", "Stage", "run_cpp"]


def _print_result(result: RunResult) -> None:
    print(f"ok={result.ok} stage={result.stage} timed_out={result.timed_out} exit_code={result.exit_code}")
    print("--- stdout ---")
    print(result.stdout, end="" if result.stdout.endswith("\n") or not result.stdout else "\n")
    print("--- stderr ---")
    print(result.stderr, end="" if result.stderr.endswith("\n") or not result.stderr else "\n")
    if result.message:
        print("--- message ---")
        print(result.message)


if __name__ == "__main__":
    sample = """\
#include <iostream>
#include <string>

int main() {
    std::string name;
    std::cin >> name;
    std::cout << "Hello, " << name << "!" << std::endl;
    return 0;
}
"""
    result = run_cpp(sample, stdin="World\n")
    _print_result(result)
    expected = "Hello, World!\n"
    if not result.ok or result.stdout != expected:
        raise SystemExit(1)
