import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TestResults from "@/components/TestResults";
import type { RunResult } from "@/lib/runCode";

const tests = [
  { name: "sum(2, 3)", passed: true, expected: "5", actual: "5" },
  { name: "sum(-4, 4)", passed: false, expected: "0", actual: "1" },
];
const result = (over: Partial<RunResult>): RunResult => ({ status: "failed", tests, ...over });

describe("TestResults", () => {
  it("prompts before the first run", () => {
    render(<TestResults result={null} running={false} error="" />);
    expect(screen.getByText(/click run code/i)).toBeInTheDocument();
  });

  it("shows a running state", () => {
    render(<TestResults result={null} running error="" />);
    expect(screen.getByText(/running your code/i)).toBeInTheDocument();
  });

  it("shows a network/API error instead of results", () => {
    render(<TestResults result={null} running={false} error="Couldn't reach the server." />);
    expect(screen.getByText("Couldn't reach the server.")).toBeInTheDocument();
  });

  it("shows the count, each test, and the actual value only for failures", () => {
    render(<TestResults result={result({})} running={false} error="" />);
    expect(screen.getByText("Some tests failed")).toBeInTheDocument();
    expect(screen.getByText("1 / 2 passed")).toBeInTheDocument();
    expect(screen.getByText("sum(2, 3)")).toBeInTheDocument();
    expect(screen.getByText("1", { selector: "code" })).toBeInTheDocument(); // "got 1" on the failing test
    expect(screen.queryByText(/got 5/)).not.toBeInTheDocument();
  });

  it("celebrates when everything passes", () => {
    const passing = tests.map((t) => ({ ...t, passed: true, actual: t.expected }));
    render(<TestResults result={result({ status: "passed", tests: passing })} running={false} error="" />);
    expect(screen.getByText("All tests passed!")).toBeInTheDocument();
    expect(screen.getByText("2 / 2 passed")).toBeInTheDocument();
  });

  it("shows compiler output for a compile error", () => {
    render(<TestResults result={result({ status: "compilation_error", tests: [], compilerOutput: "error: expected ';'" })} running={false} error="" />);
    expect(screen.getByText("Your code didn't compile")).toBeInTheDocument();
    expect(screen.getByText("error: expected ';'")).toBeInTheDocument();
  });

  it.each([
    ["timeout", "Time limit exceeded"],
    ["execution_error", "Your program crashed"],
  ] as const)("distinguishes %s", (status, headline) => {
    render(<TestResults result={result({ status, tests: [] })} running={false} error="" />);
    expect(screen.getByText(headline)).toBeInTheDocument();
  });
});
