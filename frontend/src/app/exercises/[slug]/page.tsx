"use client";

// Exercise page (/exercises/<slug>): the problem on the left, the editor and test results on the right.
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ProtectedPage from "@/components/ProtectedPage";
import CodeEditor from "@/components/CodeEditor";
import TestResults from "@/components/TestResults";
import { exercisesInTopic, findExercise } from "@/lib/exercises";
import { findTopic } from "@/lib/topics";
import { clearCode, loadCode, saveCode } from "@/lib/storage/codeStorage";
import { markSolved } from "@/lib/storage/progressStorage";
import { runCode, type RunResult } from "@/lib/runCode";

export default function ExercisePage() {
  const { slug } = useParams<{ slug: string }>();
  const exercise = findExercise(slug);

  const [code, setCode] = useState("");
  const [showHint, setShowHint] = useState(false);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState("");
  const [confirmReset, setConfirmReset] = useState(false);
  const [editorVersion, setEditorVersion] = useState(0); // bump this to load new code into the editor

  // Load the saved code (or the starter code) whenever the exercise changes.
  useEffect(() => {
    if (exercise) {
      setCode(loadCode(exercise.id) ?? exercise.starterCode);
      setEditorVersion((v) => v + 1);
    }
    setShowHint(false);
    setResult(null);
    setError("");
    setConfirmReset(false);
  }, [exercise]);

  if (!exercise) {
    return (
      <ProtectedPage>
        <main className="container notFound">
          <p className="mono">error: exercise &quot;{slug}&quot; not found</p>
          <Link className="button" href="/dashboard">Back to Dashboard</Link>
        </main>
      </ProtectedPage>
    );
  }

  const topic = findTopic(exercise.topic);
  const siblings = exercisesInTopic(exercise.topic);
  const index = siblings.findIndex((e) => e.id === exercise.id);
  const prev = siblings[index - 1];
  const next = siblings[index + 1];

  function updateCode(value: string) {
    setCode(value);
    saveCode(exercise!.id, value);
    setResult(null);
    setConfirmReset(false);
  }

  // If the student changed the code, ask once before throwing it away.
  function reset() {
    if (code !== exercise!.starterCode && !confirmReset) return setConfirmReset(true);
    setCode(exercise!.starterCode);
    setEditorVersion((v) => v + 1);
    clearCode(exercise!.id);
    setResult(null);
    setError("");
    setConfirmReset(false);
  }

  async function run() {
    if (running) return;
    setRunning(true);
    setResult(null);
    setError("");
    try {
      const res = await runCode(exercise!, code);
      setResult(res);
      // Only a real run where every test passed counts as solved (never the sample results).
      const allPassed = res.status === "passed" && res.tests.length > 0 && res.tests.every((t) => t.passed);
      if (allPassed && !res.preview) markSolved(exercise!.id);
    } catch {
      // runCode() throws when the server can't be reached.
      setError("Couldn't reach the server. Check your connection and try again.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <ProtectedPage>
      <main className="workspace">
        <section className="problem">
          <nav className="breadcrumb" aria-label="Breadcrumb">
            <Link href="/dashboard">Dashboard</Link>
            <span aria-hidden="true">/</span>
            <Link href={`/topics/${exercise.topic}`}>{topic?.name}</Link>
          </nav>
          <h1>{exercise.title}</h1>
          <div className="tags">
            {exercise.tags.map((tag) => <span className="tag" key={tag}>{tag}</span>)}
          </div>

          <h3>Problem</h3>
          <p>{exercise.description}</p>

          <h3>Examples</h3>
          <div className="example">
            {exercise.examples.map((ex) => (
              <div key={ex.input}>
                <code>{ex.input}</code> <span className="arrow">→</span> <code>{ex.output}</code>
              </div>
            ))}
          </div>

          <button className="hintToggle" aria-expanded={showHint} onClick={() => setShowHint(!showHint)}>
            {showHint ? "Hide hint" : "Show hint"}
          </button>
          {showHint && <p className="hintBox">{exercise.hint}</p>}
          <p className="reviewLesson">
            <Link href={`/topics/${exercise.topic}`}>Review the lesson</Link>
          </p>

          <nav className="exerciseNav" aria-label={`More ${topic?.name} exercises`}>
            {prev ? <Link href={`/exercises/${prev.slug}`}>← {prev.title}</Link> : <span />}
            {next && <Link href={`/exercises/${next.slug}`}>{next.title} →</Link>}
          </nav>
        </section>

        <section className="editorPanel">
          <div className="editorHeader">
            <strong>Code Editor</strong>
            <div>
              <button className="button secondary" disabled={running} onClick={reset} onBlur={() => setConfirmReset(false)}>
                {confirmReset ? "Click again to reset" : "Reset"}
              </button>
              <button className="button" disabled={running} onClick={run}>{running ? "Running…" : "▶ Run Code"}</button>
            </div>
          </div>
          <div className="fileName">solution.cpp · C++</div>
          {editorVersion > 0 ? (
            <CodeEditor key={`${exercise.id}-${editorVersion}`} initialValue={code} onChange={updateCode} readOnly={running} />
          ) : (
            <div className="codeEditor"><p className="editorLoading">Loading editor…</p></div>
          )}
          <TestResults result={result} running={running} error={error} />
        </section>
      </main>
    </ProtectedPage>
  );
}
