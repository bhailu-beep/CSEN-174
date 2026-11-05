// Checks every topic has a complete lesson.
import { describe, expect, it } from "vitest";
import { findLesson, lessons } from "@/lib/lessons";
import { findTopic, topics } from "@/lib/topics";

describe("lessons", () => {
  it("has exactly one lesson for every topic", () => {
    for (const t of topics) expect(findLesson(t.id), t.id).toBeDefined();
    expect(lessons).toHaveLength(topics.length);
  });

  it("only uses real topic ids", () => {
    for (const l of lessons) expect(findTopic(l.topic), l.topic).toBeDefined();
  });

  it("gives every lesson an intro, sections, a mistake, and key points", () => {
    for (const l of lessons) {
      expect(l.intro.length, l.topic).toBeGreaterThan(0);
      expect(l.sections.length, l.topic).toBeGreaterThan(0);
      expect(l.mistake.wrong.length, l.topic).toBeGreaterThan(0);
      expect(l.mistake.right.length, l.topic).toBeGreaterThan(0);
      expect(l.keyPoints.length, l.topic).toBeGreaterThan(0);
    }
  });

  it("has matched backticks so code formatting doesn't spill over", () => {
    const texts = lessons.flatMap((l) => [l.intro, l.mistake.text, ...l.keyPoints, ...l.sections.map((s) => s.text)]);
    for (const t of texts) expect((t.match(/`/g) ?? []).length % 2, t).toBe(0);
  });
});
