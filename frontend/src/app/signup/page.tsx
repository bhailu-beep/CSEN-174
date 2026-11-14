"use client";

// Sign-up page (/signup): create an account with a username and password (no email).
import { useAuth } from "@/components/AuthProvider";
import { validateCredentials } from "@/lib/auth";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (password !== confirm) return setError("Passwords don't match.");
    
    const problem = validateCredentials(username, password);

    if (problem) return setError(problem);

    setSubmitting(true);
    try {
      await signup(username, password);
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="authBackground">
      <div className="authCard">
        <h1>Create an account</h1>
        <p>Start your C++ learning journey.</p>
        <form onSubmit={submit}>
          <label>
            Username
            <input autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            Password
            <input type="password" autoComplete="new-password" minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          <label>
            Confirm password
            <input type="password" autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
          </label>
          {error && <p className="error" role="alert">{error}</p>}
          <button className="button full" type="submit" disabled={submitting}>Create Account</button>
        </form>
        <p className="footnote">Already have an account? <Link href="/login">Log in</Link></p>
      </div>
    </main>
  );
}
