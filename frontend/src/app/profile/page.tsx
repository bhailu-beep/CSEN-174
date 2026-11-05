"use client";

// Profile page (/profile): stats, progress by topic, and a button to reset progress.
import Link from "next/link";
import { useEffect, useState } from "react";
import ProtectedPage from "@/components/ProtectedPage";
import ProgressBar from "@/components/ProgressBar";
import { currentUser } from "@/lib/auth";
import { exercises, exercisesInTopic } from "@/lib/exercises";
import { topics } from "@/lib/topics";
import { getStatuses, resetProgress, type Status } from "@/lib/storage/progressStorage";

export default function ProfilePage() {
  const [name, setName] = useState("");
  const [statuses, setStatuses] = useState<Record<string, Status>>({});
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    setName(currentUser() ?? "");
    setStatuses(getStatuses(exercises));
  }, []);

  // Two clicks needed so progress isn't erased by accident.
  function handleReset() {
    if (!confirming) return setConfirming(true);
    resetProgress(exercises);
    setStatuses(getStatuses(exercises));
    setConfirming(false);
  }

  const count = (s: Status) => exercises.filter((e) => statuses[e.id] === s).length;

  return (
    <ProtectedPage>
      <main className="container">
        <div className="profileHeader">
          <div className="avatar" aria-hidden="true">{name.charAt(0).toUpperCase()}</div>
          <h1>{name}</h1>
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
            const solved = list.filter((e) => statuses[e.id] === "solved").length;
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
          <button className="button secondary" onClick={handleReset} onBlur={() => setConfirming(false)}>
            {confirming ? "Click again to erase all saved code and progress" : "Reset my progress"}
          </button>
        </div>
      </main>
    </ProtectedPage>
  );
}
