// Tracks which exercises are solved (key: cpp-platform:solved, a list of exercise ids).
import type { Exercise } from "../exercises";
import { clearCode, loadCode } from "./codeStorage";
import { readJSON, write } from "./local";

export type Status = "new" | "started" | "solved";

export function getSolved(): string[] {
  const list = readJSON<unknown>("solved", []);
  return Array.isArray(list) ? list.filter((x): x is string => typeof x === "string") : [];
}

// Only call this when the backend says every hidden test passed.
export function markSolved(exerciseId: string): void {
  const solved = getSolved();
  if (!solved.includes(exerciseId)) write("solved", JSON.stringify([...solved, exerciseId]));
}

export function getStatus(exercise: Exercise): Status {
  if (getSolved().includes(exercise.id)) return "solved";
  const code = loadCode(exercise.id);
  return code !== null && code !== exercise.starterCode ? "started" : "new";
}

export function getStatuses(list: Exercise[]): Record<string, Status> {
  return Object.fromEntries(list.map((e) => [e.id, getStatus(e)]));
}

// Erases solved marks and saved code for the given exercises.
export function resetProgress(list: Exercise[]): void {
  write("solved", "[]");
  list.forEach((e) => clearCode(e.id));
}
