// TODO(backend): PLACEHOLDER until the backend is ready.
// Later this will send { exerciseId, code } to the backend and get a RunResult back.
// The backend runs the HIDDEN tests; the browser never sees them.
import type { Exercise } from "./exercises";

export type TestResult = { name: string; passed: boolean; expected: string; actual: string };

export type RunResult = {
  status: "passed" | "failed" | "compilation_error" | "timeout" | "execution_error";
  tests: TestResult[];
  compilerOutput?: string; // only for compilation_error
  message?: string; // extra info, e.g. a runtime error
  preview?: boolean; // true = sample results, the code was NOT actually run
};

export async function runCode(exercise: Exercise, _code: string): Promise<RunResult> {
  await new Promise((resolve) => setTimeout(resolve, 700)); // pretend to wait for the server

  // Sample results built from the public examples, just to show the layout.
  return {
    status: "failed",
    preview: true,
    tests: exercise.examples.map((ex, i) => ({
      name: ex.input,
      expected: ex.output,
      passed: i === 0,
      actual: i === 0 ? ex.output : "?",
    })),
  };
}
