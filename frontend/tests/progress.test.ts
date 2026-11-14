// Tests for src/lib/progress.ts and src/lib/runCode.ts with fetch mocked.
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setAccessToken } from "@/lib/api";
import { findExercise } from "@/lib/exercises";
import { fetchStatuses, loadCode, saveCode, statusOf } from "@/lib/progress";
import { runCode } from "@/lib/runCode";

const json = (status: number, body?: unknown) =>
  new Response(body === undefined ? null : JSON.stringify(body), { status });

const sum = findExercise("sum-two-numbers")!;
let fetchMock: ReturnType<typeof vi.fn>;
beforeEach(() => {
  fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  setAccessToken("tok");
});
afterEach(() => vi.unstubAllGlobals());

describe("progress", () => {
  it("maps completed/started to solved/started/new, keyed by lesson/exercise", async () => {
    fetchMock.mockResolvedValueOnce(json(200, [
      { exercise_id: "sum", completed: true, started: true },
      { exercise_id: "is-even", completed: false, started: true },
      { exercise_id: "to-fahrenheit", completed: false, started: false },
    ]));
    const map = await fetchStatuses(["basics"]);
    expect(map).toEqual({ "basics/sum": "solved", "basics/is-even": "started", "basics/to-fahrenheit": "new" });
    expect(statusOf(map, sum)).toBe("solved");
    expect(statusOf({}, sum)).toBe("new");
  });

  it("loads and saves code at the exercise's code route", async () => {
    fetchMock.mockResolvedValueOnce(json(200, "int sum(){}")).mockResolvedValueOnce(json(204));
    expect(await loadCode(sum)).toBe("int sum(){}");
    await saveCode(sum, "x");
    expect(fetchMock.mock.calls[0][0]).toContain("/lessons/basics/exercises/sum/code");
    expect(fetchMock.mock.calls[1][1].method).toBe("PUT");
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({ code: "x" });
  });
});

describe("runCode", () => {
  it("posts only the code, maps compiler_output, and names the tests", async () => {
    fetchMock
      .mockResolvedValueOnce(json(200, {
        status: "failed",
        tests: [{ passed: true, expected: "5", actual: "5" }, { passed: false, expected: "0", actual: "1" }],
        message: "",
        compiler_output: null,
      }))
      .mockResolvedValueOnce(json(200, [{ inputs: ["2", "3"], expected: "5" }, { inputs: ["-4", "4"], expected: "0" }]));
    const res = await runCode(sum, "code");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ code: "code" });
    expect(res.status).toBe("failed");
    expect(res.tests.map((t) => t.name)).toEqual(["sum(2, 3)", "sum(-4, 4)"]);
    expect(res.compilerOutput).toBeUndefined();
  });

  it("still returns results if the test names can't be loaded", async () => {
    const other = findExercise("celsius-to-fahrenheit")!;
    fetchMock
      .mockResolvedValueOnce(json(200, { status: "compilation_error", tests: [], message: "Compilation failed.", compiler_output: "error: x" }))
      .mockRejectedValueOnce(new TypeError("offline"));
    const res = await runCode(other, "bad");
    expect(res.status).toBe("compilation_error");
    expect(res.compilerOutput).toBe("error: x");
  });
});
