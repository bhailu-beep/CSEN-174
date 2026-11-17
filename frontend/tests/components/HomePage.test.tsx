import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Home from "@/app/page";

let auth: { user: { id: number; username: string } | null; loading: boolean };

vi.mock("@/components/AuthProvider", () => ({ useAuth: () => auth }));

beforeEach(() => {
  auth = { user: null, loading: false };
});

describe("home page", () => {
  it("sends a logged-out visitor to sign up", () => {
    render(<Home />);
    expect(screen.getByRole("link", { name: /Get Started/ })).toHaveAttribute("href", "/signup");
    expect(screen.queryByRole("link", { name: /Dashboard/ })).not.toBeInTheDocument();
  });

  it("sends a logged-in user to the dashboard", () => {
    auth = { user: { id: 1, username: "ada" }, loading: false };
    render(<Home />);
    expect(screen.getByRole("link", { name: /Go to Dashboard/ })).toHaveAttribute("href", "/dashboard");
    expect(screen.queryByRole("link", { name: /Get Started/ })).not.toBeInTheDocument();
  });

  it("shows no button while the session is being restored", () => {
    auth = { user: null, loading: true };
    render(<Home />);
    expect(screen.queryByRole("link", { name: /Get Started/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Dashboard/ })).not.toBeInTheDocument();
  });

  it("still shows the headline in every state", () => {
    auth = { user: null, loading: true };
    render(<Home />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Build Your Skills.");
  });
});