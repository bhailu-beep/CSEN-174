// The one place that talks to the backend over HTTP.
// - Sends the Bearer access token (kept in memory only, never in localStorage).
// - Tells network failures (NetworkError) apart from HTTP errors (ApiError).
// - On a 401 it refreshes the token once and retries the request once.
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class NetworkError extends Error {
  constructor() {
    super("Couldn't reach the server. Check your connection and try again.");
    this.name = "NetworkError";
  }
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

let accessToken: string | null = null;
let onSessionExpired: (() => void) | null = null;
let refreshing: Promise<string | null> | null = null;

export const setAccessToken = (token: string | null) => { accessToken = token; };
export const getAccessToken = () => accessToken;
// The AuthProvider registers this so it can log the user out when a refresh fails.
export const setSessionExpiredHandler = (fn: (() => void) | null) => { onSessionExpired = fn; };

// FastAPI sends {detail: "text"} for most errors and {detail: [{msg}, ...]} for validation errors.
function errorMessage(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const msg = (detail[0] as { msg?: unknown }).msg;
    if (typeof msg === "string") return msg;
  }
  return `Request failed (${status}).`;
}

async function send(path: string, init: RequestInit): Promise<Response> {
  try {
    return await fetch(`${BASE_URL}${path}`, { credentials: "include", ...init });
  } catch {
    throw new NetworkError();
  }
}

async function parse<T>(res: Response): Promise<T> {
  const body = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, errorMessage(body, res.status));
  return body as T;
}

// Asks the backend for a new access token using the refresh cookie.
// Returns null if there is no valid session. Parallel callers share one request.
export function refreshSession(): Promise<string | null> {
  refreshing ??= (async () => {
    try {
      const res = await send("/auth/refresh", { method: "POST" });
      if (!res.ok) return (accessToken = null);
      accessToken = ((await res.json()) as { access_token: string }).access_token;
      return accessToken;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

type Options = { method?: string; body?: unknown; auth?: boolean };

export async function api<T>(path: string, { method = "GET", body, auth = true }: Options = {}): Promise<T> {
  const attempt = () => {
    const headers: Record<string, string> = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (auth && accessToken) headers.Authorization = `Bearer ${accessToken}`;
    return send(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  };

  let res = await attempt();
  if (res.status === 401 && auth) {
    if (await refreshSession()) {
      res = await attempt();
    } else {
      onSessionExpired?.();
    }
  }
  return parse<T>(res);
}
