import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ProtectedPage from "@/components/ProtectedPage";

const replace = vi.fn();
let auth: { user: { id: number; username: string } | null; loading: boolean };

vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));
vi.mock("@/components/AuthProvider", () => ({ useAuth: () => auth }));

beforeEach(() => replace.mockClear());

describe("ProtectedPage", () => {
  it("shows the page to a logged-in user", () => {
    auth = { user: { id: 1, username: "ada" }, loading: false };
    render(<ProtectedPage><p>secret</p></ProtectedPage>);
    expect(screen.getByText("secret")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("waits while the session is being restored, without redirecting", () => {
    auth = { user: null, loading: true };
    render(<ProtectedPage><p>secret</p></ProtectedPage>);
    expect(screen.getByText("Loading…")).toBeInTheDocument();
    expect(screen.queryByText("secret")).not.toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("sends a logged-out visitor to /login", () => {
    auth = { user: null, loading: false };
    render(<ProtectedPage><p>secret</p></ProtectedPage>);
    expect(screen.queryByText("secret")).not.toBeInTheDocument();
    expect(replace).toHaveBeenCalledWith("/login");
  });
});
