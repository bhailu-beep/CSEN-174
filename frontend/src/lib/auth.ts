// Real account calls. The access token lives in memory (see api.ts); the refresh token is an httpOnly cookie.
import { api, refreshSession, setAccessToken } from "./api";

export type User = { id: number; username: string };
type TokenResponse = { access_token: string };

// Same rules as the backend, so students get instant feedback. The backend still enforces them.
export function validateCredentials(username: string, password: string): string | null {
  if (!/^[A-Za-z0-9_]{3,20}$/.test(username.trim())) return "Username must be 3–20 letters, numbers, or underscores.";
  if (new TextEncoder().encode(password).length < 6) return "Password must be at least 6 characters.";
  if (new TextEncoder().encode(password).length > 72) return "Password must be at most 72 bytes.";
  return null;
}

export const fetchMe = () => api<User>("/auth/me");

async function authenticate(path: string, username: string, password: string): Promise<User> {
  const { access_token } = await api<TokenResponse>(path, {
    method: "POST",
    body: { username: username.trim(), password },
    auth: false,
  });
  setAccessToken(access_token);
  return fetchMe();
}

export const register = (username: string, password: string) => authenticate("/auth/register", username, password);
export const login = (username: string, password: string) => authenticate("/auth/login", username, password);

export async function logout(): Promise<void> {
  try {
    await api<void>("/auth/logout", { method: "POST", auth: false });
  } finally {
    setAccessToken(null);
  }
}

// On page load: use the refresh cookie to get back into an existing session, or return null.
export async function restoreSession(): Promise<User | null> {
  if (!(await refreshSession())) return null;
  return fetchMe();
}
