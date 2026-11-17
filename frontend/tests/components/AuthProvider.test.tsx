import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import AuthProvider, { useAuth } from "@/components/AuthProvider";
import { setAccessToken } from "@/lib/api";

const json = (status: number, body?: unknown) =>
  new Response(body === undefined ? null : JSON.stringify(body), { status });

function Probe() {
  const { user, loading, logout } = useAuth();
  return (
    <div>
      <p>{loading ? "checking" : user ? `hello ${user.username}` : "logged out"}</p>
      <button onClick={() => logout().catch(() => {})}>out</button>
    </div>
  );
}

let fetchMock: ReturnType<typeof vi.fn>;
beforeEach(() => {
  fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  setAccessToken(null);
});
afterEach(() => vi.unstubAllGlobals());

describe("AuthProvider", () => {
  it("restores the session from the refresh cookie on page load", async () => {
    fetchMock
      .mockResolvedValueOnce(json(200, { access_token: "tok" }))
      .mockResolvedValueOnce(json(200, { id: 1, username: "ada" }));
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(screen.getByText("checking")).toBeInTheDocument();
    expect(await screen.findByText("hello ada")).toBeInTheDocument();
  });

  it("is logged out when there is no valid cookie", async () => {
    fetchMock.mockResolvedValueOnce(json(401, { detail: "Missing refresh token" }));
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(await screen.findByText("logged out")).toBeInTheDocument();
  });

  it("shows logged out (not a crash) when the server is unreachable", async () => {
    fetchMock.mockRejectedValueOnce(new TypeError("offline"));
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(await screen.findByText("logged out")).toBeInTheDocument();
  });

  it("logs out locally even if the logout request fails", async () => {
    fetchMock
      .mockResolvedValueOnce(json(200, { access_token: "tok" }))
      .mockResolvedValueOnce(json(200, { id: 1, username: "ada" }))
      .mockRejectedValueOnce(new TypeError("offline"));
    render(<AuthProvider><Probe /></AuthProvider>);
    await screen.findByText("hello ada");
    fireEvent.click(screen.getByText("out"));
    await waitFor(() => expect(screen.getByText("logged out")).toBeInTheDocument());
  });
});
