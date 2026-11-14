"use client";

// Holds the logged-in user in React state and restores the session on page load.
// useAuth() gives pages { user, loading, login, signup, logout }.
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { setSessionExpiredHandler } from "@/lib/api";
import * as auth from "@/lib/auth";
import type { User } from "@/lib/auth";

type AuthState = {
  user: User | null;
  loading: boolean; // true until the first session check finishes
  login: (username: string, password: string) => Promise<void>;
  signup: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    auth.restoreSession()
      .then((u) => !cancelled && setUser(u))
      .catch(() => !cancelled && setUser(null)) // server unreachable: show logged out
      .finally(() => !cancelled && setLoading(false));
    setSessionExpiredHandler(() => setUser(null));
    return () => {
      cancelled = true;
      setSessionExpiredHandler(null);
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => setUser(await auth.login(username, password)), []);
  const signup = useCallback(async (username: string, password: string) => setUser(await auth.register(username, password)), []);
  const logout = useCallback(async () => {
    try {
      await auth.logout();
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo(() => ({ user, loading, login, signup, logout }), [user, loading, login, signup, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
