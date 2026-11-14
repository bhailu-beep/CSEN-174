"use client";

// Exercise page (/exercises/<slug>): the problem on the left, the editor and test results on the right.
import CodeEditor from "@/components/CodeEditor";
import ProtectedPage from "@/components/ProtectedPage";
import TestResults from "@/components/TestResults";
import { exercisesInTopic, findExercise } from "@/lib/exercises";
import { loadCode, saveCode } from "@/lib/progress";
import { runCode, type RunResult } from "@/lib/runCode";
import { findTopic } from "@/lib/topics";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

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
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load the saved code (or the starter code) from the server whenever the exercise changes.
  useEffect(() => {
    setShowHint(false);
    setResult(null);
    setError("");
    setConfirmReset(false);
    if (!exercise) return;
    let cancelled = false;
    setEditorVersion(0); // show "Loading editor…" until the saved code arrives
    loadCode(exercise)
      .then((saved) => saved || exercise.starterCode) // "" means nothing saved yet
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Couldn't load your saved code.");
        return exercise.starterCode;
      })
      .then((initial) => {
        if (cancelled) return;
        setCode(initial);
        setEditorVersion((v) => v + 1);
      });
    return () => {
      cancelled = true;
      if (saveTimer.current) clearTimeout(saveTimer.current); // pending save is dropped on navigation
    };
  }, [exercise]);

  // Save after the student pauses typing. Only real edits are saved, so "started" stays accurate.
  function scheduleSave(value: string) {
    if (saveTimer.current) clearTimeout(saveTimer.current);
    const target = exercise!;
    saveTimer.current = setTimeout(() => {
      saveCode(target, value).catch(() => setError("Couldn't save your code. Check your connection."));
    }, 800);
  }

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
    scheduleSave(value);
    setResult(null);
    setConfirmReset(false);
  }

  // If the student changed the code, ask once before throwing it away.
  function reset() {
    if (code !== exercise!.starterCode && !confirmReset) return setConfirmReset(true);
    setCode(exercise!.starterCode);
    setEditorVersion((v) => v + 1);
    if (saveTimer.current) clearTimeout(saveTimer.current);
    // Overwrite the saved copy so the old code doesn't come back on reload.
    saveCode(exercise!, exercise!.starterCode).catch(() => setError("Couldn't save your code. Check your connection."));
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
      // The server scores the run and records the exercise as solved when every test passes.
      setResult(await runCode(exercise!, code));
    } catch (e) {
      // NetworkError (server unreachable) or ApiError (e.g. 401, 404, 5xx): show the real message.
      setError(e instanceof Error ? e.message : "Something went wrong.");
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
