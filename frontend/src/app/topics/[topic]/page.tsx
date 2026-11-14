"use client";

// Topic page (/topics/<id>): the lesson, then that topic's exercises.
// /topics/all is the Full C++ page: every exercise, with search, topic filters, and a random pick.
import ExerciseCard from "@/components/ExerciseCard";
import Lesson from "@/components/Lesson";
import ProgressBar from "@/components/ProgressBar";
import ProtectedPage from "@/components/ProtectedPage";
import { exercises, exercisesInTopic, filterExercises } from "@/lib/exercises";
import { findLesson } from "@/lib/lessons";
import { fetchStatuses, statusOf, type StatusMap } from "@/lib/progress";
import { ALL_TOPICS_ID, findTopic, topics } from "@/lib/topics";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export default function TopicPage() {
  const { topic: topicId } = useParams<{ topic: string }>();
  const router = useRouter();
  const isAll = topicId === ALL_TOPICS_ID; // true on the Full C++ page
  const topic = findTopic(topicId);

  const [error, setError] = useState("");
  const [statuses, setStatuses] = useState<StatusMap>({});
  const [search, setSearch] = useState("");
  const [topicFilter, setTopicFilter] = useState<string | null>(null);
  const exercisesRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (!isAll && !topic) return;
    fetchStatuses(isAll ? topics.map((t) => t.id) : [topicId])
      .then(setStatuses)
      .catch((e) => setError(e instanceof Error ? e.message : "Something went wrong"));
  }, [isAll, topic, topicId]);

  if (!isAll && !topic) {
    return (
      <ProtectedPage>
        <main className="container notFound">
          <p className="mono">error: topic &quot;{topicId}&quot; not found</p>
          <Link className="button" href="/dashboard">Back to Dashboard</Link>
        </main>
      </ProtectedPage>
    );
  }

  const lesson = isAll ? undefined : findLesson(topicId);
  const list = isAll ? exercises : exercisesInTopic(topicId);
  const shown = isAll ? filterExercises(list, search, topicFilter) : list;
  const solved = list.filter((e) => statusOf(statuses, e) === "solved").length;

  // Scroll down from the lesson to the exercise list.
  function scrollToExercises() {
    exercisesRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  function openRandom() {
    const pick = shown[Math.floor(Math.random() * shown.length)];
    if (pick) router.push(`/exercises/${pick.slug}`);
  }

  return (
    <ProtectedPage>
      <main className="container">
        <Link className="backLink" href="/dashboard">← Dashboard</Link>
        <div className="topicHeader">
          <div>
            <h1>{isAll ? "Full C++" : topic!.name}</h1>
            <p>{isAll ? "Every exercise from every topic." : topic!.description}</p>
          </div>
          <div className="topicHeaderProgress">
            <span>{solved} of {list.length} solved</span>
            <ProgressBar done={solved} total={list.length} label="Progress in this section" />
          </div>
        </div>

        {lesson && (
          <Lesson lesson={lesson} onStart={scrollToExercises} />
        )}

        {!isAll && (
          <h2 className="exercisesHeading" ref={exercisesRef} tabIndex={-1}>
            Exercises
          </h2>
        )}

        {isAll && (
          <>
            <div className="toolbar">
              <input
                className="search"
                type="search"
                placeholder="Search by name or tag…"
                aria-label="Search exercises"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <button className="button secondary" onClick={openRandom} disabled={shown.length === 0}>
                Random exercise
              </button>
            </div>
            <div className="filters">
              <button className={`chip ${topicFilter === null ? "active" : ""}`} aria-pressed={topicFilter === null} onClick={() => setTopicFilter(null)}>
                All
              </button>
              {topics.map((t) => (
                <button key={t.id} className={`chip ${topicFilter === t.id ? "active" : ""}`} aria-pressed={topicFilter === t.id} onClick={() => setTopicFilter(t.id)}>
                  {t.name}
                </button>
              ))}
            </div>
          </>
        )}

        {shown.length === 0 ? (
          <p className="empty">No exercises match your search.</p>
        ) : (
          <div className="cards">
            {shown.map((exercise) => (
              <ExerciseCard
                key={exercise.id}
                exercise={exercise}
                status={statusOf(statuses, exercise)}
                topicName={isAll ? findTopic(exercise.topic)?.name : undefined}
              />
            ))}
          </div>
        )}
      </main>
    </ProtectedPage>
  );
}
