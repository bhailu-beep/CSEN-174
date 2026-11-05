// Shows the outcome after clicking Run Code.
import type { RunResult } from "@/lib/runCode";

const HEADLINES: Record<RunResult["status"], string> = {
  passed: "All tests passed!",
  failed: "Some tests failed",
  compilation_error: "Your code didn't compile",
  timeout: "Time limit exceeded",
  execution_error: "Your program crashed",
};

const EXPLANATIONS: Partial<Record<RunResult["status"], string>> = {
  compilation_error: "Fix the error below, then run again.",
  timeout: "Your code took too long. Check for a loop that never ends.",
  execution_error: "Something went wrong while running, like dividing by zero or reading outside an array.",
};

type Props = { result: RunResult | null; running: boolean; error: string };

// The panel under the editor. Handles every kind of outcome the backend can send.
export default function TestResults({ result, running, error }: Props) {
  const passed = result?.tests.filter((t) => t.passed).length ?? 0;

  return (
    <div className="results" aria-live="polite">
      <div className="resultsHeader">
        <strong>Test Results</strong>
        {result && result.tests.length > 0 && <span>{passed} / {result.tests.length} passed</span>}
      </div>

      {running && <p>Running your code…</p>}
      {!running && error && <p className="resultStatus fail">{error}</p>}
      {!running && !error && !result && <p>Click Run Code to test your solution.</p>}

      {result && (
        <>
          {/* TODO(backend): this note goes away once runCode() returns real results. */}
          {result.preview && (
            <p className="previewNote">
              Sample results: your code was not actually run. Real results will show here once the backend is connected.
            </p>
          )}
          <p className={`resultStatus ${result.status === "passed" ? "pass" : "fail"}`}>{HEADLINES[result.status]}</p>
          {EXPLANATIONS[result.status] && <p>{EXPLANATIONS[result.status]}</p>}
          {result.compilerOutput && <pre className="errorOutput">{result.compilerOutput}</pre>}
          {result.message && <pre className="errorOutput">{result.message}</pre>}

          <ul className="testList">
            {result.tests.map((test) => (
              <li key={test.name} className={test.passed ? "pass" : "fail"}>
                <span className="testIcon" aria-label={test.passed ? "passed" : "failed"}>{test.passed ? "✓" : "✗"}</span>
                <code>{test.name}</code>
                <span className="testDetail">
                  expected <code>{test.expected}</code>
                  {!test.passed && <>, got <code>{test.actual}</code></>}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
