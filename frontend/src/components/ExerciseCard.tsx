import Link from "next/link";
import type { Exercise } from "@/lib/exercises";
import type { Status } from "@/lib/storage/progressStorage";

// One exercise in a list. Shows its tags and whether it's solved or in progress.
export default function ExerciseCard({ exercise, status, topicName }: { exercise: Exercise; status?: Status; topicName?: string }) {
  return (
    <Link className="card exerciseCard" href={`/exercises/${exercise.slug}`}>
      {(topicName || status === "solved" || status === "started") && (
        <div className="cardTop">
          {topicName ? <span className="topicLabel">{topicName}</span> : <span />}
          {status === "solved" && <span className="status solved">✓ Solved</span>}
          {status === "started" && <span className="status started">In progress</span>}
        </div>
      )}
      <h3>{exercise.title}</h3>
      <p>{exercise.description}</p>
      <div className="tags">
        {exercise.tags.map((tag) => <span className="tag" key={tag}>{tag}</span>)}
      </div>
    </Link>
  );
}
