// Progress and saved code now live on the server (GET /lessons/{lesson}/progress and .../code).
import { api } from "./api";
import type { Exercise } from "./exercises";

export type Status = "new" | "started" | "solved";
// Exercise ids are only unique inside a lesson, so statuses are keyed by "lesson/exercise".
export type StatusMap = Record<string, Status>;

type ExerciseProgress = { exercise_id: string; completed: boolean; started: boolean };

export const statusKey = (e: Pick<Exercise, "topic" | "id">) => `${e.topic}/${e.id}`;

export const statusOf = (map: StatusMap, e: Exercise): Status => map[statusKey(e)] ?? "new";

export async function fetchStatuses(lessonIds: string[]): Promise<StatusMap> {
  const lists = await Promise.all(lessonIds.map((id) => api<ExerciseProgress[]>(`/lessons/${id}/progress`)));
  const map: StatusMap = {};
  lessonIds.forEach((lessonId, i) => {
    for (const p of lists[i]) {
      map[`${lessonId}/${p.exercise_id}`] = p.completed ? "solved" : p.started ? "started" : "new";
    }
  });
  return map;
}

const codePath = (e: Pick<Exercise, "topic" | "id">) => `/lessons/${e.topic}/exercises/${e.id}/code`;

// Returns "" if the student has nothing saved yet.
export const loadCode = (e: Exercise) => api<string>(codePath(e));
export const saveCode = (e: Exercise, code: string) => api<void>(codePath(e), { method: "PUT", body: { code } });
