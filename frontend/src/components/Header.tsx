"use client";

// The bar at the top of every page: logo on the left, links on the right.
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { currentUser, logout } from "@/lib/auth";

export default function Header() {
  const [user, setUser] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  // Re-check who's logged in every time the page changes (e.g. right after logging in).
  useEffect(() => setUser(currentUser()), [pathname]);

  function handleLogout() {
    logout();
    setUser(null);
    router.push("/");
  }

  return (
    <header className="header">
      <Link href="/" className="logo" aria-label="CompleteC home">
        Complete<span className="logoC">C</span>
      </Link>
      <nav>
        {/* Logged in: app links. Logged out: Log In / Sign Up. */}
        {user ? (
          <>
            <Link href="/dashboard" className={pathname === "/dashboard" ? "active" : ""}>Dashboard</Link>
            <Link href="/profile" className={pathname === "/profile" ? "active" : ""}>Profile</Link>
            <button className="linkButton" onClick={handleLogout}>Log Out</button>
          </>
        ) : (
          <>
            <Link href="/login">Log In</Link>
            <Link className="button" href="/signup">Sign Up</Link>
          </>
        )}
      </nav>
    </header>
  );
}
