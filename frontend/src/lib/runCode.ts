// Sends the student's code to the backend, which compiles and scores it in the sandbox.
// The browser only sends { code }; the tests and scoring stay on the server.
import { api } from "./api";
import type { Exercise } from "./exercises";

export type TestResult = { name: string; passed: boolean; expected: string; actual: string };

export type RunResult = {
  status: "passed" | "failed" | "compilation_error" | "timeout" | "execution_error";
  tests: TestResult[];
  compilerOutput?: string; // only for compilation_error
  message?: string; // extra info, e.g. a runtime error
};

type ApiRun = {
  status: RunResult["status"];
  tests: { passed: boolean; expected: string; actual: string }[];
  message: string;
  compiler_output: string | null;
};

// Test inputs are public (learning platform), so we can label each result like "sum(2, 3)".
const inputsCache = new Map<string, Promise<string[][]>>();

function loadInputs(exercise: Exercise): Promise<string[][]> {
  const key = `${exercise.topic}/${exercise.id}`;
  let cached = inputsCache.get(key);
  if (!cached) {
    cached = api<{ inputs: string[] }[]>(`/lessons/${exercise.topic}/exercises/${exercise.id}/tests`, { auth: false })
      .then((tests) => tests.map((t) => t.inputs));
    inputsCache.set(key, cached);
    cached.catch(() => inputsCache.delete(key)); // don't remember a failure
  }
  return cached;
}

// "sum(2, 3)" -> "sum", taken from the first example. Falls back to plain "Test 1" labels.
function testName(exercise: Exercise, inputs: string[] | undefined, index: number): string {
  const fn = exercise.examples[0]?.input.split("(")[0];
  return inputs && fn ? `${fn}(${inputs.join(", ")})` : `Test ${index + 1}`;
}

export async function runCode(exercise: Exercise, code: string): Promise<RunResult> {
  const run = await api<ApiRun>(`/lessons/${exercise.topic}/exercises/${exercise.id}/run`, {
    method: "POST",
    body: { code },
  });
  // Names are cosmetic, so a failure to load them must not hide the real results.
  const inputs = await loadInputs(exercise).catch(() => [] as string[][]);
  return {
    status: run.status,
    message: run.message || undefined,
    compilerOutput: run.compiler_output ?? undefined,
    tests: run.tests.map((t, i) => ({ name: testName(exercise, inputs[i], i), ...t })),
  };
}
