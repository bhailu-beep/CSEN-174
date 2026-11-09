"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { currentUser } from "@/lib/auth";

// Wrap a page in this to send logged-out visitors to /login.
export default function ProtectedPage({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    if (currentUser()) setAllowed(true);
    else router.replace("/login");
  }, [router]);

  return allowed ? <>{children}</> : <p className="container">Loading…</p>;
}
