"use client";

// Dashboard (/dashboard): overall progress, the Full C++ section, and the topic cards.
import { useAuth } from "@/components/AuthProvider";
import ProgressBar from "@/components/ProgressBar";
import ProtectedPage from "@/components/ProtectedPage";
import { exercises, exercisesInTopic } from "@/lib/exercises";
import { fetchStatuses, statusOf, type StatusMap } from "@/lib/progress";
import { ALL_TOPICS_ID, topics } from "@/lib/topics";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const { user } = useAuth();
  const [statuses, setStatuses] = useState<StatusMap>({});
  const [error, setError] = useState("");  

  useEffect(() => {
    fetchStatuses(topics.map((t) => t.id))
      .then(setStatuses)
      .catch((e) => setError(e instanceof Error ? e.message : "Something went wrong."));
  }, []);

  const solvedIn = (list: typeof exercises) => list.filter((e) => statusOf(statuses, e) === "solved").length;
  const totalSolved = solvedIn(exercises);
  // The first exercise the student started but hasn't solved, for the "Continue" link.
  const inProgress = exercises.find((e) => statusOf(statuses, e) === "started");

  return (
    <ProtectedPage>
      <main className="container">
        <div className="welcome">
          <h1>Welcome, {user?.username}!</h1>
          <p>{totalSolved} of {exercises.length} exercises solved</p>
          <ProgressBar done={totalSolved} total={exercises.length} label="Overall progress" />
          {inProgress && (
            <Link className="continueLink" href={`/exercises/${inProgress.slug}`}>
              Continue: {inProgress.title} →
            </Link>
          )}
        </div>

        {error && <p className="error" role="alert">{error}</p>}

        <Link className="fullCpp" href={`/topics/${ALL_TOPICS_ID}`}>
          <div>
            <h2>Full C++</h2>
            <p>Every exercise in one place. Search, filter by topic, or pick a random one.</p>
          </div>
          <span className="fullCppArrow" aria-hidden="true">→</span>
        </Link>

        <h2>Topics</h2>
        <div className="cards topicGrid">
          {topics.map((topic) => {
            const list = exercisesInTopic(topic.id);
            const solved = solvedIn(list);
            return (
              <Link className="card topicCard" href={`/topics/${topic.id}`} key={topic.id}>
                <h3>{topic.name}</h3>
                <p>{topic.description}</p>
                <div className="topicProgress">
                  <ProgressBar done={solved} total={list.length} label={`${topic.name} progress`} />
                  <span>{solved}/{list.length}</span>
                </div>
              </Link>
            );
          })}
        </div>
      </main>
    </ProtectedPage>
  );
}
