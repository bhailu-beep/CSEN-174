"use client";

// Sign-up page (/signup): create an account with a username and password (no email).
import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signup } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (password !== confirm) return setError("Passwords don't match.");
    const problem = signup(username, password);
    if (problem) return setError(problem);
    router.push("/dashboard");
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
          <button className="button full" type="submit">Create Account</button>
        </form>
        {/* TODO(backend): remove this note once accounts are saved on the server. */}
        <p className="hint">Prototype: accounts are only saved in this browser for now.</p>
        <p className="footnote">Already have an account? <Link href="/login">Log in</Link></p>
      </div>
    </main>
  );
}
