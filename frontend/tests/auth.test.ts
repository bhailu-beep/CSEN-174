// Tests for src/lib/auth.ts with fetch mocked (the backend owns the real accounts).
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getAccessToken, setAccessToken } from "@/lib/api";
import { login, logout, register, restoreSession, validateCredentials } from "@/lib/auth";

const json = (status: number, body?: unknown) =>
  new Response(body === undefined ? null : JSON.stringify(body), { status });

let fetchMock: ReturnType<typeof vi.fn>;
beforeEach(() => {
  fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  setAccessToken(null);
});
afterEach(() => vi.unstubAllGlobals());

describe("validateCredentials", () => {
  it("accepts a good username and password", () => expect(validateCredentials("bemmy_h", "secret1")).toBeNull());
  it("rejects bad usernames", () => {
    expect(validateCredentials("ab", "secret1")).toMatch(/Username/);
    expect(validateCredentials("has space", "secret1")).toMatch(/Username/);
  });
  it("rejects too short or too long passwords", () => {
    expect(validateCredentials("zack", "123")).toMatch(/Password/);
    expect(validateCredentials("zack", "x".repeat(73))).toMatch(/Password/);
  });
});

describe("register / login / logout", () => {
  it("login stores the access token and returns the user", async () => {
    fetchMock
      .mockResolvedValueOnce(json(200, { access_token: "tok" }))
      .mockResolvedValueOnce(json(200, { id: 1, username: "lori" }));
    expect(await login(" lori ", "secret1")).toEqual({ id: 1, username: "lori" });
    expect(getAccessToken()).toBe("tok");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ username: "lori", password: "secret1" });
  });

  it("register posts to /auth/register", async () => {
    fetchMock
      .mockResolvedValueOnce(json(200, { access_token: "tok" }))
      .mockResolvedValueOnce(json(200, { id: 2, username: "zack" }));
    await register("zack", "secret1");
    expect(fetchMock.mock.calls[0][0]).toContain("/auth/register");
  });

  it("a wrong password rejects with the backend message and stores no token", async () => {
    fetchMock.mockResolvedValueOnce(json(401, { detail: "Invalid username or password" }));
    await expect(login("lori", "wrong12")).rejects.toThrow("Invalid username or password");
    expect(getAccessToken()).toBeNull();
  });

  it("logout clears the token even if the request fails", async () => {
    setAccessToken("tok");
    fetchMock.mockRejectedValueOnce(new TypeError("offline"));
    await expect(logout()).rejects.toThrow();
    expect(getAccessToken()).toBeNull();
  });
});

describe("restoreSession", () => {
  it("returns null with no refresh cookie", async () => {
    fetchMock.mockResolvedValueOnce(json(401, { detail: "Missing refresh token" }));
    expect(await restoreSession()).toBeNull();
  });

  it("returns the user when the refresh cookie is valid", async () => {
    fetchMock
      .mockResolvedValueOnce(json(200, { access_token: "tok" }))
      .mockResolvedValueOnce(json(200, { id: 1, username: "lori" }));
    expect(await restoreSession()).toEqual({ id: 1, username: "lori" });
  });
});
