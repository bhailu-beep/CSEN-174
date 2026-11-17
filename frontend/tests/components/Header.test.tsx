import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Header from "@/components/Header";

const push = vi.fn();
const logout = vi.fn();
let pathname = "/";
let auth: { user: { id: number; username: string } | null; loading: boolean; logout: typeof logout };

vi.mock("next/navigation", () => ({ useRouter: () => ({ push }), usePathname: () => pathname }));
vi.mock("@/components/AuthProvider", () => ({ useAuth: () => auth }));

beforeEach(() => {
  push.mockClear();
  logout.mockReset().mockResolvedValue(undefined);
  pathname = "/";
  auth = { user: null, loading: false, logout };
});

describe("Header", () => {
  it("shows Log In and Sign Up to a logged-out visitor", () => {
    render(<Header />);
    expect(screen.getByRole("link", { name: "Log In" })).toHaveAttribute("href", "/login");
    expect(screen.getByRole("link", { name: "Sign Up" })).toHaveAttribute("href", "/signup");
    expect(screen.queryByRole("link", { name: "Dashboard" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Log Out" })).not.toBeInTheDocument();
  });

  it("shows Dashboard, Profile and Log Out to a logged-in user", () => {
    auth = { user: { id: 1, username: "ada" }, loading: false, logout };
    render(<Header />);
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("href", "/dashboard");
    expect(screen.getByRole("link", { name: "Profile" })).toHaveAttribute("href", "/profile");
    expect(screen.getByRole("button", { name: "Log Out" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Log In" })).not.toBeInTheDocument();
  });

  it("shows neither set of links while the session is being restored", () => {
    auth = { user: null, loading: true, logout };
    render(<Header />);
    expect(screen.queryByRole("link", { name: "Log In" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Dashboard" })).not.toBeInTheDocument();
  });

  it("highlights the link for the current page", () => {
    auth = { user: { id: 1, username: "ada" }, loading: false, logout };
    pathname = "/profile";
    render(<Header />);
    expect(screen.getByRole("link", { name: "Profile" })).toHaveClass("active");
    expect(screen.getByRole("link", { name: "Dashboard" })).not.toHaveClass("active");
  });

  it("logs out and goes to the home page", async () => {
    auth = { user: { id: 1, username: "ada" }, loading: false, logout };
    render(<Header />);
    fireEvent.click(screen.getByRole("button", { name: "Log Out" }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/"));
    expect(logout).toHaveBeenCalledTimes(1);
  });

  it("still goes home if the logout request fails", async () => {
    auth = { user: { id: 1, username: "ada" }, loading: false, logout };
    logout.mockRejectedValue(new Error("offline"));
    render(<Header />);
    fireEvent.click(screen.getByRole("button", { name: "Log Out" }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/"));
  });

  it("links the logo to the home page", () => {
    render(<Header />);
    expect(screen.getByRole("link", { name: "CompleteC home" })).toHaveAttribute("href", "/");
  });
});
