// Shown for any URL that doesn't match a page (404).
import Link from "next/link";

export default function NotFound() {
  return (
    <main className="container notFound">
      <p className="mono">error: page not found (404)</p>
      <h1>This page doesn&apos;t exist.</h1>
      <Link className="button" href="/">Go home</Link>
    </main>
  );
}
