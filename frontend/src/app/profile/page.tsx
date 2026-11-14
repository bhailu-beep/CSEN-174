"use client";

// Profile page (/profile): stats and progress by topic.
import { useAuth } from "@/components/AuthProvider";
import ProgressBar from "@/components/ProgressBar";
import ProtectedPage from "@/components/ProtectedPage";
import { exercises, exercisesInTopic } from "@/lib/exercises";
import { fetchStatuses, statusOf, type StatusMap } from "@/lib/progress";
import { topics } from "@/lib/topics";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function ProfilePage() {
  const { user } = useAuth();
  const [statuses, setStatuses] = useState<StatusMap>({});
  const [error, setError] = useState("");  

  useEffect(() => {
    fetchStatuses(topics.map((t) => t.id))
      .then(setStatuses)
      .catch((e) => setError(e instanceof Error ? e.message : "Something went wrong."));
  }, []);

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
      </main>
    </ProtectedPage>
  );
}
