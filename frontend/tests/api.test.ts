// Tests for the fetch helper in src/lib/api.ts, with fetch mocked.
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api, ApiError, NetworkError, setAccessToken } from "@/lib/api";

const json = (status: number, body?: unknown) =>
  new Response(body === undefined ? null : JSON.stringify(body), { status });

let fetchMock: ReturnType<typeof vi.fn>;
beforeEach(() => {
  fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  setAccessToken("tok1");
});
afterEach(() => vi.unstubAllGlobals());

const authHeader = (call: number) => (fetchMock.mock.calls[call][1].headers as Record<string, string>).Authorization;

describe("api()", () => {
  it("sends the Bearer token and cookies, and returns JSON", async () => {
    fetchMock.mockResolvedValueOnce(json(200, [1, 2]));
    expect(await api<number[]>("/lessons/")).toEqual([1, 2]);
    expect(authHeader(0)).toBe("Bearer tok1");
    expect(fetchMock.mock.calls[0][1].credentials).toBe("include");
  });

  it("sends a JSON body", async () => {
    fetchMock.mockResolvedValueOnce(json(204));
    await api("/x", { method: "PUT", body: { code: "hi" } });
    expect(fetchMock.mock.calls[0][1].body).toBe('{"code":"hi"}');
  });

  it("throws NetworkError when the server is unreachable", async () => {
    fetchMock.mockRejectedValueOnce(new TypeError("Failed to fetch"));
    await expect(api("/x")).rejects.toBeInstanceOf(NetworkError);
  });

  it("throws ApiError with the backend's detail message", async () => {
    fetchMock.mockResolvedValueOnce(json(400, { detail: "Username is already taken" }));
    await expect(api("/x")).rejects.toMatchObject({ status: 400, message: "Username is already taken" });
  });

  it("reads the first message of a validation error list", async () => {
    fetchMock.mockResolvedValueOnce(json(422, { detail: [{ msg: "too short" }] }));
    await expect(api("/x")).rejects.toMatchObject({ message: "too short" });
  });

  it("on 401 refreshes once and retries with the new token", async () => {
    fetchMock
      .mockResolvedValueOnce(json(401, { detail: "expired" }))
      .mockResolvedValueOnce(json(200, { access_token: "tok2" })) // /auth/refresh
      .mockResolvedValueOnce(json(200, { ok: true }));
    expect(await api("/x")).toEqual({ ok: true });
    expect(fetchMock.mock.calls[1][0]).toContain("/auth/refresh");
    expect(authHeader(2)).toBe("Bearer tok2");
  });

  it("gives up and reports the 401 when the refresh fails", async () => {
    fetchMock
      .mockResolvedValueOnce(json(401, { detail: "expired" }))
      .mockResolvedValueOnce(json(401, { detail: "Missing refresh token" }));
    const err = (await api("/x").catch((e) => e)) as ApiError;
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(401);
    expect(fetchMock).toHaveBeenCalledTimes(2); // no retry loop
  });

  it("does not try to refresh for auth: false requests", async () => {
    fetchMock.mockResolvedValueOnce(json(401, { detail: "Invalid username or password" }));
    await expect(api("/auth/login", { method: "POST", auth: false })).rejects.toMatchObject({ status: 401 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
