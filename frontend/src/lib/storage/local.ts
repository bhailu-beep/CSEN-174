// The ONLY place that touches the browser's localStorage.
// Every read/write is wrapped so the site still works if storage is blocked or cleared.
const PREFIX = "cpp-platform:";

export function read(key: string): string | null {
  try { return localStorage.getItem(PREFIX + key); } catch { return null; }
}

export function write(key: string, value: string): void {
  try { localStorage.setItem(PREFIX + key, value); } catch { /* storage unavailable */ }
}

export function remove(key: string): void {
  try { localStorage.removeItem(PREFIX + key); } catch { /* storage unavailable */ }
}

export function readJSON<T>(key: string, fallback: T): T {
  try { return JSON.parse(read(key) ?? "") as T; } catch { return fallback; }
}
