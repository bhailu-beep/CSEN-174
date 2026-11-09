"use client";

// Login page (/login): username + password, plus a one-click demo account.
import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { DEMO_PASSWORD, DEMO_USERNAME, login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function logInAs(name: string, pass: string) {
    if (!login(name, pass)) return setError("Incorrect username or password.");
    router.push("/dashboard");
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    logInAs(username, password);
  }

  return (
    <main className="authBackground">
      <div className="authCard">
        <h1>Welcome back!</h1>
        <p>Log in to continue practicing C++.</p>
        <form onSubmit={submit}>
          <label>
            Username
            <input autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            Password
            <input type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          {error && <p className="error" role="alert">{error}</p>}
          <button className="button full" type="submit">Log In</button>
        </form>
        {/* TODO(backend): remove the demo account button once real login exists. */}
        <button className="demoButton" onClick={() => logInAs(DEMO_USERNAME, DEMO_PASSWORD)}>Try Demo Account</button>
        <p className="footnote">New here? <Link href="/signup">Sign up</Link></p>
      </div>
    </main>
  );
}
