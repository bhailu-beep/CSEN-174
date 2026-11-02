"use client";

// Dashboard (/dashboard): overall progress, the Full C++ section, and the topic cards.
import Link from "next/link";
import { useEffect, useState } from "react";
import ProtectedPage from "@/components/ProtectedPage";
import ProgressBar from "@/components/ProgressBar";
import { currentUser } from "@/lib/auth";
import { exercises, exercisesInTopic } from "@/lib/exercises";
import { ALL_TOPICS_ID, topics } from "@/lib/topics";
import { getStatuses, type Status } from "@/lib/storage/progressStorage";

export default function Dashboard() {
  const [name, setName] = useState("");
  const [statuses, setStatuses] = useState<Record<string, Status>>({});

  // Saved progress lives in the browser, so read it after the page loads.
  useEffect(() => {
    setName(currentUser() ?? "");
    setStatuses(getStatuses(exercises));
  }, []);

  const solvedIn = (list: typeof exercises) => list.filter((e) => statuses[e.id] === "solved").length;
  const totalSolved = solvedIn(exercises);
  // The first exercise the student started but hasn't solved, for the "Continue" link.
  const inProgress = exercises.find((e) => statuses[e.id] === "started");

  return (
    <ProtectedPage>
      <main className="container">
        <div className="welcome">
          <h1>Welcome, {name}!</h1>
          <p>{totalSolved} of {exercises.length} exercises solved</p>
          <ProgressBar done={totalSolved} total={exercises.length} label="Overall progress" />
          {inProgress && (
            <Link className="continueLink" href={`/exercises/${inProgress.slug}`}>
              Continue: {inProgress.title} →
            </Link>
          )}
        </div>

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
