import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ExercisePage from "@/app/exercises/[slug]/page";
import { findExercise } from "@/lib/exercises";

const sum = findExercise("sum-two-numbers")!;
const loadCode = vi.fn();
const saveCode = vi.fn();
const runCode = vi.fn();

vi.mock("next/navigation", () => ({ useParams: () => ({ slug: "sum-two-numbers" }), useRouter: () => ({ replace: vi.fn() }) }));
vi.mock("@/components/AuthProvider", () => ({ useAuth: () => ({ user: { id: 1, username: "ada" }, loading: false }) }));
// Monaco doesn't run in jsdom, so a textarea stands in for the editor.
vi.mock("@/components/CodeEditor", () => ({
  default: ({ initialValue, onChange }: { initialValue: string; onChange: (v: string) => void }) => (
    <textarea aria-label="editor" defaultValue={initialValue} onChange={(e) => onChange(e.target.value)} />
  ),
}));
vi.mock("@/lib/progress", () => ({
  loadCode: (...a: unknown[]) => loadCode(...a),
  saveCode: (...a: unknown[]) => saveCode(...a),
}));
vi.mock("@/lib/runCode", () => ({ runCode: (...a: unknown[]) => runCode(...a) }));

const editor = () => screen.findByLabelText("editor") as Promise<HTMLTextAreaElement>;

beforeEach(() => {
  loadCode.mockReset().mockResolvedValue("");
  saveCode.mockReset().mockResolvedValue(undefined);
  runCode.mockReset();
});

describe("exercise page", () => {
  it("shows the problem, examples and hint toggle", async () => {
    render(<ExercisePage />);
    await editor();
    expect(screen.getByRole("heading", { name: sum.title })).toBeInTheDocument();
    expect(screen.getByText(sum.description)).toBeInTheDocument();
    expect(screen.queryByText(sum.hint)).not.toBeInTheDocument();
    fireEvent.click(screen.getByText("Show hint"));
    expect(screen.getByText(sum.hint)).toBeInTheDocument();
  });

  it("starts from the starter code when nothing is saved", async () => {
    render(<ExercisePage />);
    expect((await editor()).value).toBe(sum.starterCode);
    expect(saveCode).not.toHaveBeenCalled(); // opening an exercise must not mark it started
  });

  it("loads the student's saved code from the server", async () => {
    loadCode.mockResolvedValue("int sum(int a, int b) { return a + b; }");
    render(<ExercisePage />);
    expect((await editor()).value).toContain("return a + b");
    expect(loadCode).toHaveBeenCalledWith(expect.objectContaining({ id: "sum", topic: "basics" }));
  });

  it("shows 'Loading editor…' until the saved code arrives", async () => {
    let arrive!: (code: string) => void;
    loadCode.mockReturnValue(new Promise<string>((resolve) => { arrive = resolve; }));
    render(<ExercisePage />);
    expect(screen.getByText("Loading editor…")).toBeInTheDocument();
    arrive("saved");
    expect((await editor()).value).toBe("saved");
  });

  it("falls back to starter code and shows an error if loading fails", async () => {
    loadCode.mockRejectedValue(new Error("Could not reach the server."));
    render(<ExercisePage />);
    expect((await editor()).value).toBe(sum.starterCode);
    expect(await screen.findByText("Could not reach the server.")).toBeInTheDocument();
  });

  it("saves once, after the student stops typing", async () => {
    render(<ExercisePage />);
    const box = await editor();
    fireEvent.change(box, { target: { value: "a" } });
    fireEvent.change(box, { target: { value: "ab" } });
    expect(saveCode).not.toHaveBeenCalled();
    await waitFor(() => expect(saveCode).toHaveBeenCalledTimes(1), { timeout: 2000 });
    expect(saveCode).toHaveBeenCalledWith(expect.objectContaining({ id: "sum" }), "ab");
  });

  it("runs the code and shows the results", async () => {
    runCode.mockResolvedValue({
      status: "passed",
      tests: [{ name: "sum(2, 3)", passed: true, expected: "5", actual: "5" }],
    });
    render(<ExercisePage />);
    await editor();
    fireEvent.click(screen.getByRole("button", { name: /Run Code/ }));
    expect(await screen.findByText("All tests passed!")).toBeInTheDocument();
    expect(runCode).toHaveBeenCalledWith(expect.objectContaining({ id: "sum" }), sum.starterCode);
  });

  it("shows a compile error", async () => {
    runCode.mockResolvedValue({ status: "compilation_error", tests: [], compilerOutput: "error: oops" });
    render(<ExercisePage />);
    await editor();
    fireEvent.click(screen.getByRole("button", { name: /Run Code/ }));
    expect(await screen.findByText("error: oops")).toBeInTheDocument();
  });

  it("shows the real error message when the server cannot be reached", async () => {
    runCode.mockRejectedValue(new Error("Could not reach the server."));
    render(<ExercisePage />);
    await editor();
    fireEvent.click(screen.getByRole("button", { name: /Run Code/ }));
    expect(await screen.findByText("Could not reach the server.")).toBeInTheDocument();
    expect(screen.queryByText("All tests passed!")).not.toBeInTheDocument();
  });

  it("disables Run while a run is in progress", async () => {
    runCode.mockReturnValue(new Promise(() => {}));
    render(<ExercisePage />);
    await editor();
    fireEvent.click(screen.getByRole("button", { name: /Run Code/ }));
    expect(await screen.findByRole("button", { name: "Running…" })).toBeDisabled();
  });

  it("asks before resetting edited code, then overwrites the saved copy", async () => {
    loadCode.mockResolvedValue("my edits");
    render(<ExercisePage />);
    await editor();
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByRole("button", { name: "Click again to reset" })).toBeInTheDocument();
    expect(saveCode).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Click again to reset" }));
    expect(saveCode).toHaveBeenCalledWith(expect.objectContaining({ id: "sum" }), sum.starterCode);
    expect((await editor()).value).toBe(sum.starterCode);
  });
});
