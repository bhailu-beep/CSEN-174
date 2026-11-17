import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ExerciseCard from "@/components/ExerciseCard";
import { findExercise } from "@/lib/exercises";

const sum = findExercise("sum-two-numbers")!;

describe("ExerciseCard", () => {
  it("links to the exercise by slug and shows its title and tags", () => {
    render(<ExerciseCard exercise={sum} status="new" />);
    expect(screen.getByRole("link")).toHaveAttribute("href", "/exercises/sum-two-numbers");
    expect(screen.getByText("Sum Two Numbers")).toBeInTheDocument();
    sum.tags.forEach((tag) => expect(screen.getByText(tag)).toBeInTheDocument());
  });

  it("shows no badge for a new exercise", () => {
    render(<ExerciseCard exercise={sum} status="new" />);
    expect(screen.queryByText(/solved|in progress/i)).not.toBeInTheDocument();
  });

  it("shows Solved and In progress badges", () => {
    const { rerender } = render(<ExerciseCard exercise={sum} status="solved" />);
    expect(screen.getByText(/Solved/)).toBeInTheDocument();
    rerender(<ExerciseCard exercise={sum} status="started" />);
    expect(screen.getByText("In progress")).toBeInTheDocument();
  });

  it("shows the topic name on the Full C++ page", () => {
    render(<ExerciseCard exercise={sum} topicName="Basics" />);
    expect(screen.getByText("Basics")).toBeInTheDocument();
  });
});
