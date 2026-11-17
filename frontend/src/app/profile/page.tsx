"use client";

// Profile page (/profile): stats, progress by topic, and a button to reset progress.
import { useAuth } from "@/components/AuthProvider";
import ProgressBar from "@/components/ProgressBar";
import ProtectedPage from "@/components/ProtectedPage";
import { exercises, exercisesInTopic } from "@/lib/exercises";
import { fetchStatuses, resetProgress, statusOf, type StatusMap } from "@/lib/progress";
import { topics } from "@/lib/topics";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function ProfilePage() {
  const { user } = useAuth();
  const [statuses, setStatuses] = useState<StatusMap>({});
  const [error, setError] = useState("");
  const [confirming, setConfirming] = useState(false);
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    fetchStatuses(topics.map((t) => t.id))
      .then(setStatuses)
      .catch((e) => setError(e instanceof Error ? e.message : "Something went wrong."));
  }, []);

  // Two clicks needed so progress isn't erased by accident.
  async function handleReset() {
    if (!confirming) return setConfirming(true);
    setResetting(true);
    setError("");
    try {
      await resetProgress();
      setStatuses(await fetchStatuses(topics.map((t) => t.id)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setResetting(false);
      setConfirming(false);
    }
  }

  const count = (s: "new" | "started" | "solved") =>
    exercises.filter((e) => statusOf(statuses, e) === s).length;

  return (
    <ProtectedPage>
      <main className="container">
        {error && <p className="error" role="alert">{error}</p>}
        <div className="profileHeader">
          <div className="avatar" aria-hidden="true">{user?.username.charAt(0).toUpperCase()}</div>
          <h1>{user?.username}</h1>
        </div>

        <div className="stats">
          <div className="stat"><strong>{count("solved")}</strong><span>Solved</span></div>
          <div className="stat"><strong>{count("started")}</strong><span>In progress</span></div>
          <div className="stat"><strong>{count("new")}</strong><span>Not started</span></div>
        </div>

        <h2>Progress by topic</h2>
        <ul className="topicList">
          {topics.map((topic) => {
            const list = exercisesInTopic(topic.id);
            const solved = list.filter((e) => statusOf(statuses, e) === "solved").length;
            return (
              <li key={topic.id}>
                <Link href={`/topics/${topic.id}`}>{topic.name}</Link>
                <ProgressBar done={solved} total={list.length} label={`${topic.name} progress`} />
                <span>{solved}/{list.length}</span>
              </li>
            );
          })}
        </ul>

        <div className="dangerZone">
          <button className="button secondary" disabled={resetting} onClick={handleReset} onBlur={() => setConfirming(false)}>
            {resetting ? "Resetting…" : confirming ? "Click again to erase all saved code and progress" : "Reset my progress"}
          </button>
        </div>
      </main>
    </ProtectedPage>
  );
}
