// Checks the exercise data is valid and that search/filtering works.
// Run this after adding or editing exercises: npm test
import { describe, expect, it } from "vitest";
import { exercises, exercisesInTopic, filterExercises, findExercise } from "@/lib/exercises";
import { ALL_TOPICS_ID, findTopic, topics } from "@/lib/topics";

describe("exercise data", () => {
  it("has unique ids and slugs", () => {
    expect(new Set(exercises.map((e) => e.id)).size).toBe(exercises.length);
    expect(new Set(exercises.map((e) => e.slug)).size).toBe(exercises.length);
  });

  it("puts every exercise in a real topic", () => {
    for (const e of exercises) expect(findTopic(e.topic), e.id).toBeDefined();
  });

  it("gives every topic at least one exercise", () => {
    for (const t of topics) expect(exercisesInTopic(t.id).length, t.id).toBeGreaterThan(0);
  });

  it("does not use the reserved 'all' id as a topic", () => {
    expect(findTopic(ALL_TOPICS_ID)).toBeUndefined();
  });

  it("gives every exercise starter code and at least one example", () => {
    for (const e of exercises) {
      expect(e.starterCode.length, e.id).toBeGreaterThan(0);
      expect(e.examples.length, e.id).toBeGreaterThan(0);
    }
  });

  it("finds an exercise by slug", () => {
    expect(findExercise("factorial")?.id).toBe("016-factorial");
    expect(findExercise("nope")).toBeUndefined();
  });
});

describe("filterExercises", () => {
  it("returns everything with no search and no topic", () => {
    expect(filterExercises(exercises, "", null)).toHaveLength(exercises.length);
  });

  it("filters by topic", () => {
    const result = filterExercises(exercises, "", "loops");
    expect(result.length).toBeGreaterThan(0);
    expect(result.every((e) => e.topic === "loops")).toBe(true);
  });

  it("searches titles and tags, ignoring case", () => {
    expect(filterExercises(exercises, "PALINDROME", null).map((e) => e.slug)).toEqual(["is-palindrome"]);
    const hits = filterExercises(exercises, "pointers", null);
    expect(hits.length).toBeGreaterThan(0);
    expect(hits.every((e) => e.title.toLowerCase().includes("pointers") || e.tags.some((t) => t.includes("pointers")))).toBe(true);
  });

  it("combines search and topic", () => {
    expect(filterExercises(exercises, "factorial", "strings")).toHaveLength(0);
  });
});
