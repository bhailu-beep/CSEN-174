// TODO(backend): PROTOTYPE LOGIN, username + password, no email.
// Accounts are saved in this browser only, so this is NOT secure.
// The backend team will replace these functions with real login later; the pages won't need to change.
import { read, readJSON, remove, write } from "./storage/local";

export const DEMO_USERNAME = "student";
export const DEMO_PASSWORD = "Demo123!";

type Accounts = Record<string, { username: string; password: string }>;

// Returns an error message, or null if the account was created.
export function signup(username: string, password: string): string | null {
  const name = username.trim();
  if (!/^[A-Za-z0-9_]{3,20}$/.test(name)) return "Username must be 3–20 letters, numbers, or underscores.";
  if (password.length < 6) return "Password must be at least 6 characters.";

  const accounts = readJSON<Accounts>("accounts", {});
  const key = name.toLowerCase();
  if (accounts[key] || key === DEMO_USERNAME) return "That username is taken.";

  accounts[key] = { username: name, password };
  write("accounts", JSON.stringify(accounts));
  write("user", name);
  return null;
}

export function login(username: string, password: string): boolean {
  const key = username.trim().toLowerCase();
  if (key === DEMO_USERNAME && password === DEMO_PASSWORD) {
    write("user", DEMO_USERNAME);
    return true;
  }
  const account = readJSON<Accounts>("accounts", {})[key];
  if (!account || account.password !== password) return false;
  write("user", account.username);
  return true;
}

export function currentUser(): string | null {
  return read("user");
}

export function logout(): void {
  remove("user");
}
