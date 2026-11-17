import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TopicPage from "@/app/topics/[topic]/page";
import { exercises, exercisesInTopic } from "@/lib/exercises";
import { topics } from "@/lib/topics";

let params: { topic: string };
const fetchStatuses = vi.fn();

vi.mock("next/navigation", () => ({ useParams: () => params, useRouter: () => ({ push: vi.fn(), replace: vi.fn() }) }));
vi.mock("@/components/AuthProvider", () => ({ useAuth: () => ({ user: { id: 1, username: "ada" }, loading: false }) }));
vi.mock("@/lib/progress", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/progress")>()),
  fetchStatuses: (...args: unknown[]) => fetchStatuses(...args),
}));

beforeEach(() => {
  fetchStatuses.mockReset();
  fetchStatuses.mockResolvedValue({});
});

describe("topic page: lesson grouping", () => {
  it("shows only the exercises of one lesson", async () => {
    params = { topic: "loops" };
    render(<TopicPage />);
    exercisesInTopic("loops").forEach((e) => expect(screen.getByText(e.title)).toBeInTheDocument());
    exercisesInTopic("basics").forEach((e) => expect(screen.queryByText(e.title)).not.toBeInTheDocument());
    await waitFor(() => expect(fetchStatuses).toHaveBeenCalledWith(["loops"]));
  });

  it("shows every exercise from every lesson on Full C++", async () => {
    params = { topic: "all" };
    render(<TopicPage />);
    exercises.forEach((e) => expect(screen.getByText(e.title)).toBeInTheDocument());
    await waitFor(() => expect(fetchStatuses).toHaveBeenCalledWith(topics.map((t) => t.id)));
  });

  it("shows server progress: solved count and badges", async () => {
    params = { topic: "basics" };
    fetchStatuses.mockResolvedValue({ "basics/sum": "solved", "basics/is-even": "started" });
    render(<TopicPage />);
    expect(await screen.findByText("1 of 3 solved")).toBeInTheDocument();
    expect(screen.getByText(/✓ Solved/)).toBeInTheDocument();
    expect(screen.getByText("In progress")).toBeInTheDocument();
  });

  it("shows an error message when progress can't be loaded", async () => {
    params = { topic: "basics" };
    fetchStatuses.mockRejectedValue(new Error("Couldn't reach the server. Check your connection and try again."));
    render(<TopicPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't reach the server");
  });

  it("shows not-found for an unknown topic and does not call the API", () => {
    params = { topic: "nope" };
    render(<TopicPage />);
    expect(screen.getByText(/topic "nope" not found/)).toBeInTheDocument();
    expect(fetchStatuses).not.toHaveBeenCalled();
  });
});
