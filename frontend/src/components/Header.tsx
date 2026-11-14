"use client";

// The bar at the top of every page: logo on the left, links on the right.
import { useAuth } from "@/components/AuthProvider";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export default function Header() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  async function handleLogout() {
    await logout();
    router.push("/");
  }

  return (
    <header className="header">
      <Link href="/" className="logo" aria-label="CompleteC home">
        Complete<span className="logoC">C</span>
      </Link>
      <nav>
        {/* Logged in: app links. Logged out: Log In / Sign Up. */}
        {loading ? null : user ? (
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
